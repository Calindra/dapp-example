# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from os import environ
import logging
import requests
from util import str2hex, hex2str
from challenge import Challenge, Move

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def add_notice(data):
    logger.info(f"Adding notice {data}")
    notice = {"payload": str2hex(data)}
    response = requests.post(rollup_server + "/notice", json=notice)
    logger.info(f"Received notice status {response.status_code} body {response.content}")

def add_report(output=""):
    logger.info("Adding report " + output)
    report = {"payload": str2hex(output)}
    response = requests.post(rollup_server + "/report", json=report)
    logger.info(f"Received report status {response.status_code}")
    
def handle_advance(data):
    try:
        payload = json.loads(hex2str(data["payload"]))
    except:
        return "reject"
    
    method = payload.get("method")
    sender = data["metadata"]["msg_sender"]
    logger.info(f"Received advance request data {payload}")
    
    handler = advance_method_handlers.get(method)
    if not handler:
        add_report("Invalid method.")
        return "reject"
    
    return handler(payload, sender)


def handle_inspect(data):
    try:
        payload = json.loads(hex2str(data["payload"]))
    except:
        return "reject"
    
    method = payload.get("method")
    logger.info(f"Received inspect request data {payload}")
    
    handler = inspect_method_handlers.get(method)
    if not handler:
        add_report("Invalid method.")
        return "reject"
    
    return handler(payload)

def create_challenge(payload, sender):
    add_report("create challenge")
    return "accept"

def accept_challenge(payload, sender):
    add_report("accept challenge")
    return "accept"

def reveal(payload, sender):
    add_report("reveal")
    return "accept"

def get_challenges(payload):
    add_report("get challenges")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

advance_method_handlers = {
    "create_challenge": create_challenge,
    "accept_challenge": accept_challenge,
    "reveal": reveal
}

inspect_method_handlers = {
    "get_challenges": get_challenges
}

# Advance
# - create challenge
# - accept challenge
# - reveal

# Inspect
# - get challenges

finish = {"status": "accept"}


while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
