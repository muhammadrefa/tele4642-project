"""
SNACK: Social Network Access Connection Kontroller - Switch REST API
Powered by Ryu

TELE4642 Network Technologies project
- Muhammad Refa Utama Putra (z5467671)
- Abbas Eldirani (z5638923)
- Andrew Beh (z5361137)

The University of New South Wales - 2025
"""

import json
import time

from webob import Response
from ryu.app.wsgi import ControllerBase, route

class SNACKController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super().__init__(req, link, data, **config)
        self.snack_app = data['snack_api_app']

    @route('snack', '/snack/get/limited_host_status', methods=['GET'])
    def get_limited_host_status(self, req, **kwargs):
        result = self.snack_app.api_get_limited_host_status()
        for i in range(0, 10):
            if result is not None:
                break
            time.sleep(0.5)
            result = self.snack_app.api_get_limited_host_status()
        # TODO: Return 504 if failed to get
        body = json.dumps(result)
        resp = Response(content_type='application/json', body=body, charset='UTF-8')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
