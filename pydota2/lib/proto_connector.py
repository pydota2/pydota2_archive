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
# NOTE: This file assumes that your Dota2 launch options are properly
#       configured.
# Example: -botworldstatetosocket_radiant 12120 -botworldstatetosocket_dire 12121
#          -botworldstatetosocket_frames 10 -botworldstatesocket_threaded
"""Acquire CMsgBotWorldState serialized data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import socket
import threading
from datetime import datetime

from struct import *

from pydota2.lib import gfile

HOST            = '127.0.0.1'      # The remote host
RADIANT_PORT    = 12120 # The same port as used by the server
DIRE_PORT       = 12121 # The same port as used by the server
DIR_REPLAY      = 'replays'

sDate = "{:%Y_%m_%d_%H%M_}".format(datetime.now())

threadLock = threading.Lock()


class ProtoThread(threading.Thread):
    def __init__(self, threadID, name, save_proto=True, func_callback=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name  # should be either 'Radiant' or 'Dire'
        if self.name == 'Radiant':
            self.port = RADIANT_PORT
        else:
            self.port = DIRE_PORT
        self.num_proto = 0
        self.save_proto = save_proto
        self.func = func_callback

    def run(self):
        print("Starting Thread %d for %s" % (self.threadID, self.name))
        path = JoinPath(DIR_REPLAY, sDate + self.name)
        print("Save Path: %s" % path)
        self.create_save_directory(path)
        self.connect_with_server()

    def save_proto_to_file(self, bin_data):
        with open(JoinPath(DIR_REPLAY, sDate + self.name, str(self.num_proto).zfill(6) + '.bin'), 'bw') as f:
            f.write(bin_data)

    def create_save_directory(self, dir_path):
        # check if directory exists, if not, make it
        if not Exists(dir_path):
            MakeDirs(dir_path)

    def connect_with_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, self.port))

            while True:
                binSize = s.recv(4)

                if not binSize:
                    print("%s proto stream not found! Exiting!" % self.name)
                    break

                if binSize:
                    protoSize = unpack("<I", binSize)
                    print("%s protoSize: %d" % (self.name, protoSize[0]))
                    binData = s.recv(protoSize[0])

                    # Get lock to synchronize threads
                    threadLock.acquire()
                    if self.save_proto:
                        self.save_proto_to_file(binData)
                    if self.func:
                        self.func(binData)
                    # Free lock to release for next thread
                    threadLock.release()

                    self.num_proto += 1

            print("Closing Socket")
            s.close()


def createRadiantThread(save_to_proto=False, callback=None):
    return ProtoThread(1, 'Radiant', save_to_proto, callback)


def createDireThread(save_to_proto=False, callback=None):
    return ProtoThread(2, 'Dire', save_to_proto, callback)
