#!/usr/bin/env python3

"""
SNACK: Social Network Access Connection Kontroller - Topology
Simulated using Mininet

TELE4642 Network Technologies project
- Muhammad Refa Utama Putra (z5467671)
- Abbas Eldirani (z5638923)
- Andrew Beh (z5361137)

The University of New South Wales - 2025
"""

from mininet.link import TCLink
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.cli import CLI


class SNACKTopo(Topo):
    def build(self, k):
        # ----- GENERATE NETWORK DEVICES ----- #

        # --- Internal network devices --- #
        # TODO: Social media dept. hosts
        # TODO: Other dept. hosts
        # TODO: Internal switches

        # --- External network simulated devices --- #
        # TODO: Social media services servers
        # TODO: External network switch (simulating ISP switch)

        # Example (from Fat Tree Topo)
        edSws = [[self.addSwitch(f'edSw{pod}{i}', dpid=f'0000000000{pod:02X}{i:02X}01') for i in range(0, edSw_cnt)] for pod in range(0, k)]
        hosts = [[self.addHost(f'host{pod}{i}', ip=f'10.{pod}.{math.floor(i/edSw_cnt)}.{(i%edSw_cnt)+2}') for i in range(0, host_cnt)] for pod in range(0, k)]

        # ----- ESTABLISH CONNECTIONS ----- #

        # --- Internal network connection --- #
        # TODO: Connect hosts from social media dept. to dept. switch
        # TODO: Connect hosts from other dept. to dept. switch
        # TODO: Connect dept. switch to central switch

        # --- External network simulated network --- #
        # TODO: Connect servers to ISP switch

        # --- Connect internal-external network --- #
        # TODO: Connect central switch to ISP switch

        # Example (from Fat Tree Topo)
        self.addLink(edSws[pod][i], hosts[pod][(i * edSw_cnt) + j], port1=j+1)


if __name__ == "__main__":
    # I cannot get this working in Fat Tree Topology
    net = Mininet(topo=FatTreeTopo(4), link=TCLink, controller=None, autoSetMacs=True, autoStaticArp=True)
    net.addController('controller', controller=RemoteController, ip="127.0.0.1", port=6633, protocol="OpenFlow13")
    net.start()
    CLI(net)
    net.stop()
