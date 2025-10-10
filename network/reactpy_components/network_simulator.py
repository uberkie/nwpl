"""Lightweight network simulator for testing topologies and commands.

Provides: Bridge, Device, DummyTerminal, Router (basic routing table),
NetworkSimulator and simple commands: ping and traceroute.

Notes:
- No ARP is simulated. Devices determine whether a destination is "local"
  based on the sender's interface network. If the destination is not in the
  sender's local subnet, the sender will consult its routing table; if no
  route exists (or gateway unreachable) the packet is dropped.
- Layer2 forwarding is only allowed between ports on the same Bridge.
- VLANs are not modelled in detail here but could be attached to Bridge.
"""

from dataclasses import dataclass, field
import ipaddress

from typing import List, Dict, Optional, Tuple
from ipaddress import ip_network
from typing import Union


@dataclass
class Port:
    id: str
    device: "Device"
    ip_interface: Optional[ipaddress.IPv4Interface] = None
    bridge: Optional["Bridge"] = None
    vlan: Optional[int] = None
    iftype: str = "ethernet"

    def has_ip(self, ip: str) -> bool:
        """Return True if this port has the specified IP."""
        if not self.ip_interface:
            return False
        try:
            candidate = (
                ip if isinstance(ip, ipaddress.IPv4Address)
                else ipaddress.IPv4Address(str(ip))
            )
        except Exception:
            return False
        return candidate == self.ip_interface.ip


@dataclass
class Bridge:
    name: str
    vlan_aware: bool = False
    ports: List["Port"] = field(default_factory=list)
    l2_table: Dict[ipaddress.IPv4Address, "Port"] = field(default_factory=dict)

    def connect(self, port: "Port"):
        """Connect a port to the bridge and learn its IP."""
        port.bridge = self
        if port not in self.ports:
            self.ports.append(port)
        if port.ip_interface:
            ip = port.ip_interface.ip
            # store learned addresses as strings for consistent lookup
            self.l2_table[str(ip)] = port

    def disconnect(self, port: "Port"):
        """Disconnect a port from the bridge."""
        if port in self.ports:
            self.ports.remove(port)
        if port.ip_interface:
            ip = port.ip_interface.ip
            self.l2_table.pop(str(ip), None)
        port.bridge = None

    def forward(self, src_ip: str, dst_ip: str, vlan: Optional[int] = None):
        """Forward packet based on learned IP→Port mapping."""
        # normalize the lookup key to string to match learned entries
        try:
            dst_addr = ipaddress.ip_address(dst_ip)
            key = str(dst_addr)
        except Exception:
            key = str(dst_ip)
        if key in self.l2_table:
            return self.l2_table[key].device  # return destination device
        return None  # destination not found


class Device:
    def __init__(self, name: str):
        self.name = name
        self.ports: List[Port] = []
        # routing table entries: list of dicts with keys: network (IPv4Network), gateway (str or None)
        self.routes: List[Dict] = []
        # NAT rules: list of dicts {type: 'snat'|'dnat', match: IPv4Network or IPv4Address string, to: ip string}
        self.nat_rules: List[Dict] = []

    def add_port(self, port_id: str, ip_with_prefix: Optional[str] = None) -> Port:
        p = Port(id=port_id, device=self)
        if ip_with_prefix:
            p.ip_interface = ipaddress.IPv4Interface(ip_with_prefix)
        self.ports.append(p)
        return p

    def set_port_vlan(self, port: Port, vlan: Optional[int]):
        port.vlan = vlan

    def add_route(self, network: str, gateway: Union[str, 'Port', None] = None):
        self.routes.append({
            "network": ip_network(network),
            "gateway": gateway,
        })
    def add_nat(self, nat_type: str, match: str, to: str):
        """Add a simple static NAT rule.

        nat_type: 'snat' or 'dnat'
        match: an IP or network string (e.g. '192.0.2.0/24' or '203.0.113.5')
        to: replacement IP string
        """
        # store raw strings; matching will parse
        parsed = None
        if '/' in match:
            parsed = ipaddress.IPv4Network(match)
        else:
            try:
                parsed = ipaddress.IPv4Address(match)
            except Exception:
                parsed = match  # leave as raw string
        self.nat_rules.append({"type": nat_type, "match": parsed, "to": to})

    def find_port_for_src(self, src_ip: str) -> Optional[Port]:
        for p in self.ports:
            if p.ip_interface and p.ip_interface.ip == ipaddress.IPv4Address(src_ip):
                return p
        return None

    def longest_prefix_route(self, dst_ip: str):
        dst = ipaddress.IPv4Address(dst_ip)
        best = None
        best_prefix = -1
        for r in self.routes:
            net = r["network"]
            if dst in net:
                if net.prefixlen > best_prefix:
                    best = r
                    best_prefix = net.prefixlen
        return best

    def receive_packet(self, packet: Dict, ingress: Port, simulator: "NetworkSimulator") -> Optional[Dict]:
        """Process incoming packet. For DummyTerminal this will reply to ping.

        Returns an optional response packet dict (for ping replies).
        """
        # Base device: no special behaviour
        return None

    def apply_snat(self, packet: Dict) -> Dict:
        """Apply static SNAT rules on outgoing packet (simple override)."""
        for r in self.nat_rules:
            if r.get("type") != "snat":
                continue
            try:
                # match against src or network
                m = r.get("match")
                if isinstance(m, ipaddress.IPv4Network):
                    if ipaddress.IPv4Address(packet.get("src")) in m:
                        old = packet.get("src")
                        packet = {**packet, "src": str(r.get("to"))}
                        # record trace
                        packet.setdefault("trace", []).append({"device": self.name, "action": "snat", "from": old, "to": r.get("to")})
                        break
                elif isinstance(m, ipaddress.IPv4Address):
                    if packet.get("src") == str(m):
                        old = packet.get("src")
                        packet = {**packet, "src": str(r.get("to"))}
                        packet.setdefault("trace", []).append({"device": self.name, "action": "snat", "from": old, "to": r.get("to")})
                else:
                    if packet.get("src") == m:
                        old = packet.get("src")
                        packet = {**packet, "src": str(r.get("to"))}
                        packet.setdefault("trace", []).append({"device": self.name, "action": "snat", "from": old, "to": r.get("to")})
                        break
            except Exception:
                continue
        return packet

    def apply_dnat(self, packet: Dict) -> Dict:
        """Apply static DNAT rules on incoming packet (simple override)."""
        for r in self.nat_rules:
            if r.get("type") != "dnat":
                continue
            try:
                m = r.get("match")
                if isinstance(m, str) and '/' in m:
                    net = ipaddress.IPv4Network(m)
                    if ipaddress.IPv4Address(packet.get("dst")) in net:
                        old = packet.get("dst")
                        packet = {**packet, "dst": str(r.get("to"))}
                        packet.setdefault("trace", []).append({"device": self.name, "action": "dnat", "from": old, "to": r.get("to")})
                        break
                else:
                    if packet.get("dst") == m:
                        old = packet.get("dst")
                        packet = {**packet, "dst": str(r.get("to"))}
                        packet.setdefault("trace", []).append({"device": self.name, "action": "dnat", "from": old, "to": r.get("to")})
                        break
            except Exception:
                continue
        return packet

    def ping(self, src_ip: str, dst_ip: str, simulator: "NetworkSimulator", ttl: int = 64) -> Tuple[bool, List[str]]:
        pkt = {"type": "icmp-echo", "src": src_ip, "dst": dst_ip, "ttl": ttl}
        pkt = self.apply_snat(pkt)
        res = simulator.handle_packet(pkt, self, None)
        success = False
        trace = []
        if isinstance(res, dict):
            if res.get("type") in ("icmp-reply",):
                success = True
            trace = res.get("trace", [])
        return success, trace

    def traceroute(self, src_ip: str, dst_ip: str, simulator: "NetworkSimulator", max_hops: int = 30) -> List[str]:
        path = []
        for ttl in range(1, max_hops + 1):
            pkt = {"type": "icmp-echo", "src": src_ip, "dst": dst_ip, "ttl": ttl}
            pkt = self.apply_snat(pkt)
            res = simulator.handle_packet(pkt, self, None)
            if isinstance(res, dict):
                if res.get("type") == "icmp-reply":
                    path.extend(res.get("trace", []))
                    break
                elif res.get("type") == "icmp-time-exceeded":
                    path.extend(res.get("trace", []))
                elif res.get("type") == "unreachable":
                    path.extend(res.get("trace", []))
                    break
        return path


class Router(Device):
    def __init__(self, name: str):
        super().__init__(name)
        # nat_table: list of mappings for active translations
        # each mapping: {proto: 'icmp', 'orig_src': str, 'orig_dst': str, 'translated_src': str, 'translated_dst': str, 'ingress': Port, 'egress': Port}
        self.nat_table: List[Dict] = []

    def _find_nat_mapping_for_reply(self, pkt: Dict) -> Optional[Dict]:
        # For simplicity, match on proto=icmp and src/dst reversed (reply from internal host)
        if pkt.get("type") not in ("icmp-reply",):
            return None
        src = pkt.get("src")
        dst = pkt.get("dst")
        if not src or not dst:
            return None
        for m in self.nat_table:
            # reply will be from translated_dst -> translated_src
            if m.get("translated_src") == dst and m.get("translated_dst") == src:
                return m
        return None

    def receive_packet(self, packet: Dict, ingress: Port, simulator: "NetworkSimulator") -> Optional[Dict]:
        # Decrement TTL
        packet["ttl"] = packet.get("ttl", 64) - 1
        if packet["ttl"] <= 0:
            return {"type": "icmp-time-exceeded", "from": self.name, "trace": packet.get("trace", []) + [{"device": self.name, "action": "ttl-expired"}]}
        # Forward based on routing table
        dst = packet.get("dst")
        # preserve original dst for mapping
        orig_dst = dst
        if not orig_dst:
            return {"type": "error", "reason": "no-dst", "from": self.name, "trace": packet.get("trace", [])}

        # If the packet is destined to one of our own addresses, consume it here
        try:
            if dst and self.find_port_for_src(dst):
                packet.setdefault("trace", []).append({"device": self.name, "action": "deliver"})
                return packet
        except Exception:
            pass

        # If this packet is a reply intended for a previously SNATed flow, reverse-translate
        for m in list(self.nat_table):
            # reply from external -> public_ip (translated_src)
            if packet.get("dst") == m.get("translated_src") and packet.get("src") == m.get("orig_dst"):
                # reverse-translate destination back to internal host
                packet.setdefault("trace", []).append({"device": self.name, "action": "reverse-snat-reply", "to_internal": m.get("orig_src")})
                packet = {**packet, "dst": m.get("orig_src")}
                break

        # Apply DNAT rules before routing (destination translation)
        packet = self.apply_dnat(packet)
        # if DNAT changed dst, create a nat mapping so replies can be reverse-translated
        if packet.get("dst") != orig_dst:
            mapping = {
                "proto": "icmp",
                "orig_src": packet.get("src"),
                "orig_dst": orig_dst,
                "translated_src": packet.get("src"),
                "translated_dst": packet.get("dst"),
                "ingress": ingress,
                "egress": None,
            }
            self.nat_table.append(mapping)

        # Re-evaluate dst after DNAT (packet may have been translated)
        dst = packet.get("dst")
        if not dst:
            return {"type": "error", "reason": "no-dst-after-dnat", "from": self.name, "trace": packet.get("trace", [])}
        route = self.longest_prefix_route(dst)
        if not route:
            return {"type": "unreachable", "from": self.name, "trace": packet.get("trace", []) + [{"device": self.name, "action": "no-route"}]}
        gw = route.get("gateway")
        # If gateway is None, consider directly connected; try to send on a port whose network contains dst
        if gw is None:
            # attempt to find a local port whose network contains dst
            for p in self.ports:
                if p.ip_interface and ipaddress.IPv4Address(dst) in p.ip_interface.network:
                    packet.setdefault("trace", []).append({"device": self.name, "action": "try-local-port", "port": p.id, "port_ip": str(p.ip_interface.ip), "network": str(p.ip_interface.network)})
                    # record egress port for any mapping that points to this translated dst
                    for m in self.nat_table:
                        if m.get("translated_dst") == packet.get("dst") and m.get("egress") is None:
                            m["egress"] = p
                    return simulator.forward_l2(self, p, packet)
            # If we couldn't find a local port, check nat_table for an egress port to forward to
            for m in self.nat_table:
                if m.get("translated_dst") == dst and m.get("egress") is not None:
                    packet.setdefault("trace", []).append({"device": self.name, "action": "nat-egress-fallback", "egress": m.get("egress").id})
                    return simulator.forward_l2(self, m.get("egress"), packet)

            return {"type": "unreachable", "from": self.name, "trace": packet.get("trace", []) + [{"device": self.name, "action": "l2-dst-not-found"}]}
        else:
            # gateway is an IP — try to find device with that IP on same bridge
            target = simulator.find_device_by_ip(gw)
            if not target:
                return {"type": "unreachable", "from": self.name, "trace": packet.get("trace", []) + [{"device": self.name, "action": "gw-not-found", "gateway": gw}]}
            # forward to that device (simulate a hop)
            # apply SNAT rules on this router before forwarding
            orig_src = packet.get("src")
            packet = self.apply_snat(packet)
            # if SNAT changed source, record mapping so replies can be reverse-translated
            if packet.get("src") != orig_src:
                mapping = {
                    "proto": "icmp",
                    "orig_src": orig_src,
                    "orig_dst": packet.get("dst"),
                    "translated_src": packet.get("src"),
                    "translated_dst": packet.get("dst"),
                    "ingress": ingress,
                    "egress": None,
                }
                self.nat_table.append(mapping)

            # record hop
            packet.setdefault("trace", []).append({"device": self.name, "action": "forward", "via": "gateway", "gateway": gw})
            return simulator.handle_packet(packet, self, ingress)


class DummyTerminal(Device):
    def __init__(self, name: str):
        super().__init__(name)


class NetworkSimulator:
    def __init__(self):
        self.devices: List[Device] = []
        self.bridges: Dict[str, Bridge] = {}

    def add_device(self, dev: Device):
        self.devices.append(dev)

    def add_bridge(self, name: str) -> Bridge:
        b = Bridge(name=name)
        self.bridges[name] = b
        return b

    def find_device_by_ip(self, ip: str) -> Optional[Tuple[Device, Port]]:
        ipaddr = ipaddress.IPv4Address(ip)
        for d in self.devices:
            for p in d.ports:
                if p.ip_interface and p.ip_interface.ip == ipaddr:
                    return d, p
        return None

    def forward_l2(self, src_device: Device, out_port: Port, packet: Dict) -> Optional[Dict]:
        # Forward via bridge attached to out_port to the device owning dst ip
        if out_port.bridge is None:
            return {"type": "unreachable", "from": src_device.name, "trace": packet.get("trace", []) + [{"device": src_device.name, "action": "no-bridge"}]}
        dst_ip = packet["dst"]
        bridge = out_port.bridge
        # try learned L2 table first to prioritize known destination
        ports_to_check = list(bridge.ports)
        try:
            lookup_key = str(ipaddress.ip_address(dst_ip))
        except Exception:
            lookup_key = str(dst_ip)
        learned_port = bridge.l2_table.get(lookup_key)
        if learned_port and learned_port in bridge.ports and learned_port is not out_port:
            # ensure VLAN compatibility when bridge is VLAN aware
            if not bridge.vlan_aware or learned_port.vlan == out_port.vlan:
                ports_to_check = [learned_port] + [p for p in bridge.ports if p is not learned_port]

        for p in ports_to_check:
            if p is out_port:
                continue
            # record that we're checking this bridge port
            packet.setdefault("trace", []).append({"device": src_device.name, "action": "check-bridge-port", "port": p.id, "port_dev": p.device.name, "port_ip": str(p.ip_interface.ip) if p.ip_interface else None})
            # VLAN-aware forwarding: only forward if VLANs match when bridge is vlan_aware
            if out_port.bridge.vlan_aware:
                if p.vlan != out_port.vlan:
                    continue
            if p.has_ip(dst_ip):
                # deliver to device
                # For ICMP echo, destination should reply
                dest_dev = p.device
                # Build path info
                packet_path = packet.get("path", []) + [src_device.name]
                # record L2 hop
                packet.setdefault("trace", []).append({"device": src_device.name, "action": "l2-forward", "to": dest_dev.name, "bridge": out_port.bridge.name, "vlan": out_port.vlan})
                # Apply DNAT on the destination device before delivering
                pkt2 = {**packet, "path": packet_path}
                pkt2 = dest_dev.apply_dnat(pkt2)
                # Destination receives packet
                resp = dest_dev.receive_packet(pkt2, p, self)
                if resp is None:
                    # If destination is terminal and handles ping by replying
                    # Build reply packet manually
                    if pkt2.get("type") == "icmp-reply":
                        pkt2.setdefault("trace", []).append({"device": dest_dev.name, "action": "deliver"})
                        return pkt2
                    if packet.get("type") == "icmp-echo":
                        # normalize reply addresses to strings
                        reply_src = str(dst_ip)
                        reply_dst = str(packet["src"])
                        reply = {
                            "type": "icmp-reply",
                            "src": reply_src,
                            "dst": reply_dst,
                            "path": packet_path + [dest_dev.name],
                            "trace": packet.get("trace", []) + [{"device": dest_dev.name, "action": "reply"}]
                        }
                        # route the reply through the simulator (use ingress=None to let handle_packet re-resolve)
                        src_match = self.find_device_by_ip(packet["src"])
                        if src_match:
                            # dest_dev is replying host, pass ingress=None so handle_packet looks up ports as normal
                            return self.handle_packet(reply, dest_dev, None)
                        else:
                            return None
                else:
                    return resp
        return {"type": "unreachable", "from": src_device.name, "trace": packet.get("trace", []) + [{"device": src_device.name, "action": "l2-dst-not-found"}]}

    def handle_packet(self, packet: Dict, src_device: Device, ingress: Optional[Port]) -> Optional[Dict]:
        """Top-level packet handling. Decides whether to use L2 forwarding or routing."""
        src_ip = packet.get("src")
        dst_ip = packet.get("dst")
        # ensure trace exists
        packet.setdefault("trace", [])
        # find source port for src_ip
        src_port = src_device.find_port_for_src(src_ip)
        if not src_port:
            # If device doesn't own the src IP, fail
            packet.setdefault("trace", []).append({"device": src_device.name, "action": "error-src-not-on-device", "src": src_ip})
            return {"type": "error", "reason": "src-ip-not-on-device", "from": src_device.name, "trace": packet.get("trace", [])}

        # Determine if dst is in same subnet as the source port
        try:
            dst_addr = ipaddress.IPv4Address(dst_ip)
        except Exception:
            dst_addr = None

        if dst_addr is not None and src_port.ip_interface and dst_addr in src_port.ip_interface.network:
            # local delivery via L2 bridge
            return self.forward_l2(src_device, src_port, packet)

        # Not local: consult routing table on source device
        # Apply SNAT on source device before routing
        packet = src_device.apply_snat(packet)

        route = src_device.longest_prefix_route(dst_ip)
        if not route:
            # try to find an adjacent device on the same bridge (treat as implicit gateway)
            try:
                if src_port and src_port.bridge:
                    for p in src_port.bridge.ports:
                        if p is src_port:
                            continue
                        # prefer a device with an IP (candidate gateway)
                        if p.ip_interface:
                            # invoke that device's receive_packet as a gateway hop
                            return p.device.receive_packet({**packet, "path": packet.get("path", []) + [src_device.name]}, p, self)
            except Exception:
                pass
            return {"type": "unreachable", "from": src_device.name}

        gw = route.get("gateway")
        if gw is None:
            # directly connected route: try to forward via any port whose network contains dst
            for p in src_device.ports:
                if p.ip_interface and dst_addr is not None and dst_addr in p.ip_interface.network:
                    return self.forward_l2(src_device, p, packet)
            return {"type": "unreachable", "from": src_device.name}
        else:
            # gateway specified: find device with gateway IP
            gw_match = self.find_device_by_ip(gw)
            if not gw_match:
                return {"type": "unreachable", "from": src_device.name}
            next_dev, next_port = gw_match
            # deliver to gateway device; simulate hop by invoking its receive_packet
            packet = {**packet, "path": packet.get("path", []) + [src_device.name]}
            return next_dev.receive_packet(packet, next_port, self)
