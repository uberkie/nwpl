from network_simulator import NetworkSimulator, DummyTerminal, Router, Bridge, Port

if __name__ == "__main__":
    sim = NetworkSimulator()

    # host-a
    a = DummyTerminal("host-a")
    a_eth0 = a.add_port("eth0", "10.0.1.2/24")
    sim.add_device(a)

    # router
    gw = Router("rtr")

    # define ports first
    r1 = gw.add_port("r1", "10.0.1.1/24")       # towards host-a
    r2 = gw.add_port("r2", "203.0.113.1/24")    # towards host-b

    # then add routes
    gw.add_route("10.0.1.0/24", r1)
    gw.add_route("203.0.113.0/24", r2)

    sim.add_device(gw)



    # host-b
    b = DummyTerminal("host-b")
    b_eth0 = b.add_port("eth0", "203.0.113.5/24")
    sim.add_device(b)

    # bridges
    br_a = sim.add_bridge("br-a")
    br_ext = sim.add_bridge("br-ext")

    # connect ports to bridges
    br_a.connect(a_eth0)
    br_a.connect(r1)

    br_ext.connect(r2)
    br_ext.connect(b_eth0)

    # ping test
    print("ping from a -> b")
    ok, trace = a.ping("10.0.1.2", "203.0.113.5", sim)
    print("success:", ok)
    print("trace:")
    for t in trace:
        print(t)

    # traceroute test
    print("\ntraceroute:")
    tr = a.traceroute("10.0.1.2", "203.0.113.5", sim, max_hops=5)
    for t in tr:
        print(t)
