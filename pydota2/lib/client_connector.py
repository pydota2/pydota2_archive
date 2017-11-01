# NOTE: This code is to a large degree based on DeepMind work for
#       AI in StarCraft2, just ported towards the Dota 2 game.
#       DeepMind's License is posted below.

#!/usr/bin/python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# NOTE: This file assumes that your bot code running within the Dota2
#       client use the CreateHTTPRequest() API
"""Detect POST requests from CreateHTTPRequests() and provide data via response."""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import traceback
import threading
from datetime import datetime

from flask import Flask, request, jsonify

app = Flask('__name__')

HOST = '127.0.0.1'


class ClientThread(threading.Thread):
    def __init__(self, threadID, name, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name  # should be either 'Radiant' or 'Dire'
        self.port = port

    def run(self):
        print("Starting Thread %d for %s" % (self.threadID, self.name))
        app.run(host=HOST, debug=False, port=self.port)

    @app.route('/', methods=['POST'])
    def post(self):
        response = {}
        response['status'] = 200

        try:
            data = request.get_json()

            if request.content_length < 1000 and request.content_length != 0:
                filename = 'out/{0}.json'.format(str(datetime.now()))
                with open(filename, 'w') as f:
                     f.write(data)

                print('Wrote', filename)
            else:
                print("Request too long", request.content_length)
                response = {"status": 413, "content_length": request.content_length, "content": data}
                return jsonify(response)
        except:
            traceback.print_exc()
            response['status'] = 500
            return jsonify(response)

        return jsonify(response)
