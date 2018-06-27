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
import select
import threading
from datetime import datetime
from six.moves.queue import Queue

from struct import *

from pydota2.lib.gfile import *
import pydota2.protobuf.CMsgBotWorldState_pb2 as _pb

HOST            = '127.0.0.1'      # The remote host
RADIANT_PORT    = 12120 # The same port as used by the server
DIRE_PORT       = 12121 # The same port as used by the server
DIR_REPLAY      = 'replays'

sDate = "{:%Y_%m_%d_%H%M_}".format(datetime.now())

threadLock = threading.Lock()

class ProtoThread(threading.Thread):
    def __init__(self, threadID, name, save_proto=True, process_proto=True):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name  # should be either 'Radiant' or 'Dire'
        if self.name == 'Radiant':
            self.port = RADIANT_PORT
        else:
            self.port = DIRE_PORT
        self.num_proto = 0
        self.save_proto = save_proto
        self.process_proto = process_proto
        self.bDone = False
        self.proto_queue = Queue(maxsize=1)

    def add_to_proto_queue(self, data):
        data_frame = _pb.CMsgBotWorldState()
        data_frame.ParseFromString(data)
        # Get lock to synchronize threads
        #threadLock.acquire()
        self.proto_queue.put(data_frame, timeout=0.5)
        # Free lock to release for next thread
        #threadLock.release()

    def get_from_proto_queue(self):
        # Get lock to synchronize threads
        #threadLock.acquire()
        return self.proto_queue.get(timeout=0.5)
        # Free lock to release for next thread
        #threadLock.release()
        
    def run(self):
        print("Starting Protobuf Thread %d for %s" % (self.threadID, self.name))
        path = JoinPath(DIR_REPLAY, sDate + self.name)
        if self.save_proto:
            print("Save Path: %s" % path)
            self.create_save_directory(path)
        self.connect_with_server()
        
    def quit(self):
        self.bDone = True

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
            
            try:
                self.bDone = False
                while not self.bDone:
                    ready, _, _ = select.select([s], [], [])
                    if len(ready) > 0:
                        binSize = ready[0].recv(4)

                        if not binSize:
                            print("%s proto stream not found! Exiting!" % self.name)
                            break

                        else:
                            protoSize = unpack("@I", binSize)
                            print("%s protoSize: %d" % (self.name, protoSize[0]))
                            binData = ready[0].recv(protoSize[0])

                            if self.save_proto:
                                self.save_proto_to_file(binData)
                            if self.process_proto:
                                self.add_to_proto_queue(binData)

                            self.num_proto += 1
                            print("Process %d protos" % self.num_proto)
            finally:
                print("Closing Socket")
                s.shutdown(socket.SHUT_RDWR)
                s.close()


def createRadiantThread(save_proto=False):
    return ProtoThread(1, 'Radiant', save_proto, process_proto=False)


def createDireThread(save_proto=False):
    return ProtoThread(2, 'Dire', save_proto, process_proto=False)
