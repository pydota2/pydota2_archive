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
import multiprocessing

from flask import Flask, request, jsonify, abort

app = Flask('__name__')

HOST = '127.0.0.1'

post_connected = False
post_queue = multiprocessing.Queue()

class ClientThread(threading.Thread):
    def __init__(self, threadID, name, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name  # should be either 'Radiant' or 'Dire'
        self.port = port
    
    @staticmethod
    def add_to_post_queue(value_tuple):
        if post_connected:
            #print("ADDING TO POST QUEUE: ", value_tuple)
            post_queue.put(value_tuple)

    @staticmethod
    def get_from_post_queue():
        return post_queue.get()
        
    def run(self):
        global post_connected
        post_connected = False
        
        print("Starting HTTP POST Thread %d for %s" % (self.threadID, self.name))
        try:
            app.run(host=HOST, debug=False, port=self.port)
        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, ClientThread exiting.")
            
    def quit(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        print("Shutting down the POST listener")
        func()
        
    @staticmethod
    @app.route('/', methods=['POST'])
    def post():
        global post_connected
        
        #print('IN POST')
        response = {}
        response['status'] = 200
        
        if request.method == 'POST':
            try:
                data = request.get_json()

                if data == None:
                    # this should raise an HTTPException
                    abort(400, 'POST Data was not JSON')

                if request.content_length < 1000 and request.content_length != 0:
                    print("Received Post: ", str(data))
                    
                    response['Type'] = data['Type']
                    
                    if data['Type'] == 'P':
                        response['Data'] = {}
                        while not post_queue.empty():
                            action_tuple = ClientThread.get_from_post_queue()
                            print('Action Tuple To Send To Dota: ', action_tuple)
                            if action_tuple:
                                response['Data'][str(action_tuple[0])] = {}
                                response['Data'][str(action_tuple[0])][str(action_tuple[1])] = action_tuple[2]
                    elif data['Type'] == 'X':
                        post_connected = True
                        
                    response['Time'] = data['Time']
                else:
                    print("Request too long", request.content_length)
                    response = {"status": 413, "content_length": request.content_length, "content": data}
                    return jsonify(response)
            except:
                traceback.print_exc()
                response['status'] = 500
        else:
            response['status'] = 401
            abort(400, 'Request Method is not POST')

        print('SENDING RESPONSE:\n', response)
        return jsonify(response)