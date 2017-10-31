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

import os
import socket
import threading
import time

from struct import *
from datetime import datetime

import six
from six.moves import queue

from absl import app

HOST = '127.0.0.1'      # The remote host
RADIANT_PORT    = 12120 # The same port as used by the server
DIRE_PORT       = 12121 # The same port as used by the server
DIR_REPLAY      = 'replays'

threadLock = threading.Lock()
sDate = f"{datetime.now():%Y_%m_%d_%H%M_}"

def saveProtoToFile(fname, binData):
    with open(fname, 'bw') as f:
        f.write(binData)

class protoThread (threading.Thread):
    def __init__(self, threadID, name, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.port = port
      
    def run(self):
        print("Starting Thread %d for %s" % (self.threadID, self.name))
        dir_path = os.path.join(DIR_REPLAY, sDate + self.name)
        # check if directory exists, if not, make it
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.processProto(dir_path)
      
    def processProto(self, dir_path):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, self.port))

            i = 0
            while i < 1000000:
                binSize = s.recv(4)

                if not binSize:
                    print("%s proto stream not found! Exiting!" % (self.name))
                    break

                if binSize:
                    protoSize = unpack("<I", binSize)
                    print("%s protoSize: %d" % (self.name, protoSize[0]))
                    binData = s.recv(protoSize[0])

                    # Get lock to synchronize threads
                    threadLock.acquire()
                    saveProtoToFile(os.path.join(dir_path, str(i).zfill(6) + '.bin'), binData)
                    # Free lock to release for next thread
                    threadLock.release()
                    i += 1

            print("Closing Socket")
            s.close()

def main(unused_argv):
    threads = []
    try:
        # Create our threads
        t1 = protoThread(1, 'Radiant', RADIANT_PORT)
        t2 = protoThread(2, 'Dire', DIRE_PORT)

        # Start our threads
        t1.start()
        time.sleep(1)
        t2.start()

        # Append to list
        threads.append(t1)
        threads.append(t2)
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
    finally:
        # Wait for all threads to complete
        for t in threads:
            t.join()

if __name__ == "__main__":
    app.run(main)