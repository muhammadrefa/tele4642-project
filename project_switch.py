"""
SNACK: Social Network Access Connection Kontroller - Switch
Powered by Ryu

TELE4642 Network Technologies project
- Muhammad Refa Utama Putra (z5467671)
- Abbas Eldirani (z5638923)
- Andrew Beh (z5361137)

The University of New South Wales - 2025
"""
import time
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3


class SNACKSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: set allowed & blocked time in secs (done as class member (or other convenient way)))
        self.time_allowed = 3600
        self.time_blocked = 3600
        self.start_time = time.time()
        
        self.social_dept_ips = ['10.1.1.1', '10.1.1.2']
        self.other_dept_ips = ['10.1.2.1', '10.1.2.2']
        self.social_media_ips = ['10.2.1.1', '10.2.4.1']
        self.productivity_ips = ['10.2.3.1', '10.2.4.1']

        self.dpid_central = 0x000001010101
        self.dpid_dump_switches = {0x000001000001, 0x000100000002, 0x000200000001}
        self.pair_timers = {}
        self.logger.info(f"SNACK initialised!")
        self.logger.info(f"Allow time: {self.time_allowed} secs.")
        self.logger.info(f"Block time: {self.time_blocked} secs.")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_feature_handler(self, ev):
        msg = ev.msg  # packet_in data structure
        dp = msg.datapath  # datapath (switch)
        dpid = dp.id

        self.logger.info(f"Switch connected with DPID: {dpid:012x}")

        if dpid == self.dpid_central:
            self.logger.info("Firewall rules are handled reactively")
            #self.add_flow_firewall(dp)
        elif dpid in self.dpid_dumb_switches:
            self.logger.info("Installing basic flow on dumb switch")
            self.add_flow_dumb_switch(dp)
        else:
            self.logger.warning(f"Unknown switch DPID: {dpid:012x}, no flow rules installed.")
        
        self.add_proactive_flow(dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg            # packet_in data structure
        dp = msg.datapath       # datapath (switch)
        ofp = dp.ofproto        # openflow protocol
        ofp_parser = dp.ofproto_parser

        in_port = msg.match['in_port']

        pkt = packet.packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == 0x88cc:
            return

        self.logger.info(f"Packetin from switch {dpid:012x}, in_port {in_port}, src {eth.src}, dst {eth.dst}")

        if dpid == self.dpid_central:
            self.logger.info("Packet came from firewall. Applying reactive flow logic.")
            self.add_reactive_flow(dp)
        else:
            self.logger.info("Packet came from dumb switch. Ignored.")
        
        #self.add_reactive_flow(dp)

    def add_proactive_flow(self, dp) -> None:
        """
        Add proactive flow
        :param dp: datapath
        """
        ofp = dp.ofproto  # openflow protocol
        ofp_parser = dp.ofproto_parser
        dpid = dp.id
        match_arp = parser.OFPMatch(eth_type=0x0806) #ARP
        actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
        self.add_flow(dp, 1, match_arp, actions)
        '''if dpid == self.dpid_central:
            self.logger.info("Installing proactive firewall rules")
            self.add_flow_firewall(dp)'''
        if dpid in self.dpid_dumb_switches:
            self.logger.info("Installing proactive dumb switches rules")
            self.add_flow_dumb_switch(dp)
        elif dpid == self.dpid_central:
            self.logger.info("Central switch handled reactively")
        else:
            self.logger.info("Unknown switch! No proactive flows installed")
        # TODO: Check datapath to distinguish dumb switches and firewall (move checking if necessary)

    def add_reactive_flow(self, dp):
        """
        Add reactive flow
        :param dp: datapath
        """
        parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if not ip_pkt: # not an IPv4 packet
            return  

        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst

        self.logger.info(f"Reactive decision: src={src_ip}, dst={dst_ip}")

        self.add_flow_firewall(dp, src_ip, dst_ip)
        # TODO: Check datapath to distinguish dumb switches and firewall (move checking if necessary)
        pass

    def add_flow_dumb_switch(self, dp) -> None:
        """
        Flow table for dumb switches
        :param dp: datapath
        """
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        match = parser.OFPMatch(eth_type=0x0800) # match all IPv4 packets
        actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)] # action: sending the packet normally
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)] #apply actions

        mod = parser.OFPFlowMod(
            datapath=dp,
            priority=0,
            match=match,
            instructions=inst
        )
        
        dp.send_msg(mod)

        # TODO: Flow table for dumb switches (proactive)
        pass

    def add_flow_firewall(self, dp) -> None:
        """
        Flow table for firewall switch
        :param dp: datapath
        """
        parser = dp.ofproto_parser
        ofp = dp.ofproto
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src_ip, ipv4_dst=dst_ip)

        if src_ip in self.social_dept_ips:
            self.logger.info(f"[ALLOW] Social Dept {src_ip} to {dst_ip}")
            actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
            self.add_flow(dp, 10, match, actions)
            return

        if src_ip in self.other_dept_ips and dst_ip in self.productivity_ips:
            self.logger.info(f"[ALLOW] Other Dept {src_ip} to productivity {dst_ip}")
            actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
            self.add_flow(dp, 10, match, actions)
            return

        if src_ip in self.other_dept_ips and dst_ip in self.social_media_ips:
            key = (src_ip, dst_ip)
            now = time.time()
            if key not in self.pair_timers:
                self.pair_timers[key] = now
                self.logger.info(f"Started timer for ({src_ip}, {dst_ip})")

            elapsed = int(now - self.pair_timers[key])
            cycle_time = self.time_allowed + self.time_blocked
            time_in_cycle = elapsed % cycle_time
            allow = time_in_cycle < self.time_allowed

            if allow:
                self.logger.info(f"[ALLOW] {src_ip} to {dst_ip} (within allowed window)")
                actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
            else:
                self.logger.info(f"[BLOCK] {src_ip} to {dst_ip} (within blocked window)")
                actions = []

            self.add_flow(dp, 10, match, actions, hard_timeout=3600)
            return

        self.logger.warning(f"[DROP] Unknown or unexpected traffic: {src_ip} -> {dst_ip}")
        self.add_flow(dp, 10, match, [])

        '''ofp = dp.ofproto
        parser = dp.ofproto_parser
        now = time.time()
        elapsed = int(now - self.start_time)
        allow_period = (elapsed // (self.time_allowed + self.time_blocked)) % 2 == 0
        self.logger.info(f"Installing firewall rules on switch {dp.id} at time {elapsed}s. Allow period: {allow_period}")
       
        for src in self.social_dept_ips: # traffic from social media dept to any destination
            for dst in self.social_media_ips + self.productivity_ips:
                match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)
                actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
                self.add_flow(dp, 10, match, actions)

        for src in self.other_dept_ips: # traffic from other dept to productivity services
            for dst in self.productivity_ips:
                match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)
                actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]
                self.add_flow(dp, 10, match, actions)

        for src in self.other_dept_ips: # controlled traffic from other dept to social media services
            for dst in self.social_media_ips:
                match = parser.OFPMatch(eth_type=0x0800, ipv4_src=src, ipv4_dst=dst)
                if allow_period:
                    actions = [parser.OFPActionOutput(ofp.OFPP_NORMAL)]  # Allow
                else:
                    actions = []  # Drop
                self.add_flow(dp, 10, match, actions)'''


        
        # TODO: Flow table for firewall (reactive). Add arguments if needed
        pass

    def add_flow(self, dp, priority, match, actions, idle_timeout=0, hard_timeout=0):
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp, priority=priority, match=match,
            instructions=inst, idle_timeout=idle_timeout,
            hard_timeout=hard_timeout
        )
        dp.send_msg(mod)
