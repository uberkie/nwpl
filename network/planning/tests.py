from django.test import TestCase
from network.reactpy_components.network_simulator import NetworkSimulator, DummyTerminal
# Create your tests here.

def test_ping_basic():
    sim = NetworkSimulator()
    a = DummyTerminal("a"); a.add_port("eth0","10.0.0.2/24"); sim.add_device(a)
    b = DummyTerminal("b"); b.add_port("eth0","10.0.0.3/24"); sim.add_device(b)
    br = sim.add_bridge("br"); br.connect(a.ports[0]); br.connect(b.ports[0])
    ok, trace = a.ping("10.0.0.2", "10.0.0.3", sim)
    assert ok
    assert any("reply" in entry for entry in trace) or any("device" in entry and "b" in entry for entry in trace)