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
        # Define departments and their /24 subnets (second octet)
        departments = {
            'S': 1,
            'O': 2,
            # add more departments here with unique subnet IDs
        }

        # Create departmental switches and hosts
        dept_switches = {}
        for dept_name, subnet_id in departments.items():
                # Add a switch for the department
                sw = self.addSwitch(
                        name=f'sw{dept_name}',
                        dpid=f'0000000000{subnet_id:02X}01'
                )
                dept_switches[dept_name] = sw

                # Add hosts for this department
                for h in range(k):
                        ip = f'10.1.{subnet_id}.{h + 1}/24'
                        host = self.addHost(
                                name=f'host{dept_name}{h}',
                                ip=ip
                        )
                        self.addLink(sw, host)

        # Central SDN switch
        core_sw = self.addSwitch(
                name='swCentral',
                dpid='00000000010101'
        )
        for sw in dept_switches.values():
                self.addLink(core_sw, sw)

        # --- External network simulated devices --- #
        # TODO: Social media services servers
        # TODO: External network switch (simulating ISP switch)

        # Simulated ISP/external switch
        isp_sw = self.addSwitch(
                name='swISP',
                dpid='00000000020001'
        )
        self.addLink(isp_sw, core_sw)

        # External service hosts
        services = {
                'twitter': '10.2.1.1/24',
                'facebook': '10.2.2.1/24',
                'google': '10.2.3.1/24',
                'm365': '10.2.4.1/24',
        }
        for svc_name, svc_ip in services.items():
                svc_host = self.addHost(
                        name=svc_name,
                        ip=svc_ip
                )
                self.addLink(isp_sw, svc_host)

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
        # Prompt user for number of hosts per department
        try:
                k = int(input('Enter number of hosts per department (e.g., 2): ').strip())
        except ValueError:
                print('Invalid input, defaulting to 2 hosts per department.')
                k = 2

        topo = SNACKTopo(k)

        # I cannot get this working in Fat Tree Topology
        net = Mininet(topo=topo, link=TCLink, controller=None, autoSetMacs=True, autoStaticArp=True)
        net.addController('controller', controller=RemoteController, ip="127.0.0.1", port=6633, protocol="OpenFlow13")
        net.start()
        CLI(net)
        net.stop()
