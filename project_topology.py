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
    def build(self):
        # ----- GENERATE NETWORK DEVICES ----- #

        # --- Internal network devices --- #
        # TODO: Social media dept. hosts
        # TODO: Other dept. hosts
        # TODO: Internal switches
        # Define departments and their /24 subnets (second octet)
        # --- Internal departmental switches ---
        swS = self.addSwitch(name='swS', dpid='00000000000101')
        swO = self.addSwitch(name='swO', dpid='00000000000201')

        # --- Hosts for Social media dept (S) ---
        hostS0 = self.addHost(name='hostS0', ip='10.1.1.1/24')
        hostS1 = self.addHost(name='hostS1', ip='10.1.1.2/24')
        self.addLink(swS, hostS0, port1=1)
        self.addLink(swS, hostS1, port1=2)

        # --- Hosts for Other dept (O) ---
        hostO0 = self.addHost(name='hostO0', ip='10.1.2.1/24')
        hostO1 = self.addHost(name='hostO1', ip='10.1.2.2/24')
        self.addLink(swO, hostO0, port1=1)
        self.addLink(swO, hostO1, port1=2)

        # --- Central SDN switch ---
        core_sw = self.addSwitch(name='swCentral', dpid='00000000010101')

        # Link central switch to departmental switches
        # Note: port numbers on core switch are 1 and 2, on dept switches fixed at port 3
        self.addLink(core_sw, swS, port1=1, port2=3)
        self.addLink(core_sw, swO, port1=2, port2=3)

        # --- External network simulated devices ---

        # ISP/external switch
        isp_sw = self.addSwitch(name='swISP', dpid='00000000020001')
        self.addLink(isp_sw, core_sw, port1=1, port2=3)

        # External service hosts
        twitter = self.addHost(name='twitter', ip='10.2.1.1/24')
        facebook = self.addHost(name='facebook', ip='10.2.2.1/24')
        google = self.addHost(name='google', ip='10.2.3.1/24')
        m365 = self.addHost(name='m365', ip='10.2.4.1/24')

        # Connect external hosts to ISP switch
        self.addLink(isp_sw, twitter, port1=2)
        self.addLink(isp_sw, facebook, port1=3)
        self.addLink(isp_sw, google, port1=4)
        self.addLink(isp_sw, m365, port1=5)



        # Example (from Fat Tree Topo)
        # edSws = [[self.addSwitch(f'edSw{pod}{i}', dpid=f'0000000000{pod:02X}{i:02X}01') for i in range(0, edSw_cnt)] for pod in range(0, k)]
        # hosts = [[self.addHost(f'host{pod}{i}', ip=f'10.{pod}.{math.floor(i/edSw_cnt)}.{(i%edSw_cnt)+2}') for i in range(0, host_cnt)] for pod in range(0, k)]

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
        # self.addLink(edSws[pod][i], hosts[pod][(i * edSw_cnt) + j], port1=j+1)


if __name__ == "__main__":
        topo = SNACKTopo()

        # I cannot get this working in Fat Tree Topology
        net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True, autoStaticArp=True)
        net.addController('controller', controller=RemoteController, ip="127.0.0.1", port=6633, protocol="OpenFlow13")
        net.start()
        CLI(net)
        net.stop()
