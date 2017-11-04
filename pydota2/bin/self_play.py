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

"""Setup the files and sockets so our bots can play each other and learn."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pydota2.bin import prep_dota_client
from pydota2.lib.proto_connector import createRadiantThread, createDireThread
from pydota2.lib.client_connector import ClientThread
import pydota2.protobuf.CMsgBotWorldState_pb2 as _pb

from absl import app

CLIENT_RADIANT_PORT = 2222
CLIENT_DIRE_PORT    = 2223


def processRadiantData(data):
    data_frame = _pb.CMsgBotWorldState()
    data_frame.ParseFromString(data)
    #print('Radiant Data Size:\n%s' % str(data_frame))


def processDireData(data):
    data_frame = _pb.CMsgBotWorldState()
    data_frame.ParseFromString(data)
    #print('Dire Data:\n%s' % str(data_frame))


def main(unused_argv):
    # move over all the bot code to correct steam location so when a bot
    # game is launched it reads it from the Local Dev Script default location
    prep_dota_client.main(None)

    threads = []
    try:
        # create our CMsgBotWorldState threads
        t1 = createRadiantThread(save_to_proto=True, callback=processRadiantData)
        t2 = createDireThread(save_to_proto=True, callback=processDireData)
        thrRadiantControl = ClientThread(3, 'Radiant', CLIENT_RADIANT_PORT)
        thrDireControl = ClientThread(4, 'Dire', CLIENT_DIRE_PORT)
        
        # Start our threads
        t1.start()
        t2.start()
        thrRadiantControl.start()
        thrDireControl.start()

        # Append to list
        threads.append(t1)
        threads.append(t2)
        threads.append(thrRadiantControl)
        threads.append(thrDireControl)

    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
    finally:
        # Wait for all threads to complete
        for t in threads:
            t.join()


if __name__ == "__main__":
    app.run(main)

