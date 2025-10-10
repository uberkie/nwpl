from django.test import TestCase

from reactpy_components.network_simulator import DummyTerminal, NetworkSimulator, Router


class SimulatorTests(TestCase):
    def _link(self, sim: NetworkSimulator, *devices: DummyTerminal):
        bridge = sim.add_bridge("br")
        for dev in devices:
            bridge.connect(dev.ports[0])
        return bridge

    def test_ping_basic(self):
        sim = NetworkSimulator()
        terminal_a = DummyTerminal("a")
        terminal_a.add_port("eth0", "10.0.0.2/24")
        sim.add_device(terminal_a)

        terminal_b = DummyTerminal("b")
        terminal_b.add_port("eth0", "10.0.0.3/24")
        sim.add_device(terminal_b)

        self._link(sim, terminal_a, terminal_b)

        success, trace = terminal_a.ping("10.0.0.2", "10.0.0.3", sim)
        self.assertTrue(success)
        actions = {entry.get("action") for entry in trace}
        self.assertIn("reply", actions)

    def test_traceroute_reaches_router_destination(self):
        sim = NetworkSimulator()

        host = DummyTerminal("host")
        host.add_port("eth0", "192.168.1.2/24")
        sim.add_device(host)

        router = Router("r1")
        router.add_port("ge0", "192.168.1.1/24")
        router.add_route("192.168.1.0/24", None)
        sim.add_device(router)

        self._link(sim, host, router)

        hops = host.traceroute("192.168.1.2", "192.168.1.1", sim, max_hops=5)
        self.assertEqual(len(hops), 1)
        hop = hops[0]
        self.assertEqual(hop["result"], "icmp-reply")
        self.assertEqual(hop["device"], "r1")
        actions = {entry.get("action") for entry in hop["trace"]}
        self.assertIn("deliver", actions)
        self.assertIn("reply", actions)

    def test_traceroute_records_intermediate_router(self):
        sim = NetworkSimulator()

        host1 = DummyTerminal("h1")
        host1.add_port("eth0", "192.168.1.10/24")
        host1.add_route("192.168.2.0/24", "192.168.1.1")
        sim.add_device(host1)

        router = Router("r1")
        router.add_port("ge0", "192.168.1.1/24")
        router.add_port("ge1", "192.168.2.1/24")
        router.add_route("192.168.1.0/24", None)
        router.add_route("192.168.2.0/24", None)
        sim.add_device(router)

        host2 = DummyTerminal("h2")
        host2.add_port("eth0", "192.168.2.2/24")
        host2.add_route("192.168.1.0/24", "192.168.2.1")
        sim.add_device(host2)

        bridge1 = sim.add_bridge("br1")
        bridge1.connect(host1.ports[0])
        bridge1.connect(router.ports[0])

        bridge2 = sim.add_bridge("br2")
        bridge2.connect(router.ports[1])
        bridge2.connect(host2.ports[0])

        hops = host1.traceroute("192.168.1.10", "192.168.2.2", sim, max_hops=5)
        self.assertGreaterEqual(len(hops), 2)

        first_hop = hops[0]
        self.assertEqual(first_hop["ttl"], 1)
        self.assertEqual(first_hop["result"], "icmp-time-exceeded")
        self.assertEqual(first_hop["device"], "r1")
        self.assertIn("ttl-expired", {entry.get("action") for entry in first_hop["trace"]})

        final_hop = hops[-1]
        self.assertEqual(final_hop["result"], "icmp-reply")
        self.assertEqual(final_hop["device"], "h2")
        self.assertIn("deliver", {entry.get("action") for entry in final_hop["trace"]})

    def test_traceroute_timeout_records_placeholder(self):
        sim = NetworkSimulator()

        host = DummyTerminal("h1")
        host.add_port("eth0", "10.0.0.1/24")
        sim.add_device(host)

        # No routes or peers to respond
        hops = host.traceroute("10.0.0.1", "192.0.2.1", sim, max_hops=2)
        self.assertEqual(len(hops), 1)
        self.assertEqual(hops[0]["result"], "unreachable")
        self.assertEqual(hops[0]["device"], "h1")