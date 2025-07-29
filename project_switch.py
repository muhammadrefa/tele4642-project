"""
SNACK: Social Network Access Connection Kontroller - Switch
Powered by Ryu

TELE4642 Network Technologies project
- Muhammad Refa Utama Putra (z5467671)
- Abbas Eldirani (z5638923)
- Andrew Beh (z5361137)

The University of New South Wales - 2025
"""

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

        self.logger.info(f"SNACK initialised!")
        self.logger.info(f"Allow time: {self.time_allowed} secs.")
        self.logger.info(f"Block time: {self.time_blocked} secs.")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_feature_handler(self, ev):
        msg = ev.msg  # packet_in data structure
        dp = msg.datapath  # datapath (switch)

        self.add_proactive_flow(dp)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg            # packet_in data structure
        dp = msg.datapath       # datapath (switch)
        ofp = dp.ofproto        # openflow protocol
        ofp_parser = dp.ofproto_parser

        self.add_reactive_flow(dp)

    def add_proactive_flow(self, dp) -> None:
        """
        Add proactive flow
        :param dp: datapath
        """
        ofp = dp.ofproto  # openflow protocol
        ofp_parser = dp.ofproto_parser

        # TODO: Check datapath to distinguish dumb switches and firewall (move checking if necessary)

        # Example
        if not (dp.id & 0xFFFFFF):
            self.logger.info(f"not switch (?) (dpid: {dp.id:016x})")
            return

    def add_reactive_flow(self, dp):
        """
        Add reactive flow
        :param dp: datapath
        """

        # TODO: Check datapath to distinguish dumb switches and firewall (move checking if necessary)
        pass

    def add_flow_dumb_switch(self, dp) -> None:
        """
        Flow table for dumb switches
        :param dp: datapath
        """

        # TODO: Flow table for dumb switches (proactive)
        pass

    def add_flow_firewall(self, dp) -> None:
        """
        Flow table for firewall switch
        :param dp: datapath
        """

        # TODO: Flow table for firewall (reactive). Add arguments if needed
        pass

    # Flow table example
    def flow_edge(self, dp, sw_num: int, pod_num: int):
        ofp = dp.ofproto  # openflow protocol
        ofp_parser = dp.ofproto_parser

        # ARP
        match = ofp_parser.OFPMatch(in_port=1, eth_type=0x0806)
        actions = [ofp_parser.OFPActionOutput(2), ofp_parser.OFPActionOutput(3)]
        mod = ofp_parser.OFPFlowMod(
            datapath=dp,
            priority=1,
            match=match,
            instructions=[ofp_parser.OFPInstructionActions(
                ofp.OFPIT_APPLY_ACTIONS,
                actions
            )]
        )
        dp.send_msg(mod)

        for i in range(0, math.ceil(self.k / 2)):
            mod = ofp_parser.OFPFlowMod(
                datapath=dp,
                command=ofp.OFPFC_ADD,
                priority=ofp.OFP_DEFAULT_PRIORITY,
                match=ofp_parser.OFPMatch(eth_type=0x0800, ipv4_dst=f'10.{pod_num}.{sw_num}.{i + 2}/32'),
                instructions=[ofp_parser.OFPInstructionActions(
                    ofp.OFPIT_APPLY_ACTIONS,
                    [ofp_parser.OFPActionOutput(i + 1)]
                )]
            )
            dp.send_msg(mod)

        # edge to aggregation
        match = ofp_parser.OFPMatch(eth_type=0x0800, ipv4_dst=f'0.0.0.0/0')
        mod = ofp_parser.OFPFlowMod(
            datapath=dp,
            # table_id=3,
            command=ofp.OFPFC_ADD,
            priority=ofp.OFP_DEFAULT_PRIORITY,
            match=match,
            instructions=[ofp_parser.OFPInstructionGotoTable(3)]
        )
        dp.send_msg(mod)

        for i in range(0, math.ceil(self.k / 2)):
            match = ofp_parser.OFPMatch(eth_type=0x0800, ipv4_dst=(f'0.0.0.{i + 2}', '0.0.0.255'))
            actions = [ofp_parser.OFPActionOutput(math.ceil(self.k / 2) + i + 1)]
            mod = ofp_parser.OFPFlowMod(
                datapath=dp,
                table_id=3,
                command=ofp.OFPFC_ADD,
                priority=ofp.OFP_DEFAULT_PRIORITY,
                match=match,
                instructions=[ofp_parser.OFPInstructionActions(
                    ofp.OFPIT_APPLY_ACTIONS,
                    actions
                )]
            )
            dp.send_msg(mod)
