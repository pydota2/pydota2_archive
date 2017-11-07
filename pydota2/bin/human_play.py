#!/usr/bin/python

# NOTE: This code is to a large degree based on DeepMind work for 
#       AI in StarCraft2, just ported towards the Dota 2 game.
#       DeepMind's License is posted below.

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

"""Setup the files and sockets so our bots can play on one team and learn."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pydota2.bin import prep_dota_client
from pydota2.lib.proto_connector import ProtoThread
from pydota2.lib.client_connector import ClientThread
import pydota2.protobuf.CMsgBotWorldState_pb2 as _pb
from pydota2.env import dota2_env

from absl import app
from absl import flags

FLAGS = flags.FLAGS
BASE_PORT = 2220

flags.DEFINE_enum("team", None, dota2_env.teams.keys(), "Bot Team/Side (Radiant or Dire)")
flags.DEFINE_bool("save_replay", False, "Should replay be saved")
flags.mark_flag_as_required("team")


def processData(data):
    data_frame = _pb.CMsgBotWorldState()
    data_frame.ParseFromString(data)
    print('Data:\n%s' % str(data_frame))


def main(unused_argv):
    print("Flag: ", FLAGS.team, ", Value: ", dota2_env.teams[FLAGS.team])
    PORT = BASE_PORT + dota2_env.teams[FLAGS.team]  # Assert the team was selected
    
    # move over all the bot code to correct steam location so when a bot
    # game is launched it reads it from the Local Dev Script default location
    prep_dota_client.main(None)

    threads = []
    try:
        # create our CMsgBotWorldState threads
        thread_proto = ProtoThread(1, FLAGS.team, FLAGS.save_replay, processData)
        thread_http = ClientThread(2, FLAGS.team, PORT)
        
        # Start our threads
        thread_proto.start()
        thread_http.start()

        # Append to list
        threads.append(thread_proto)
        threads.append(thread_http)

    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
    finally:
        # Wait for all threads to complete
        for t in threads:
            t.join()


if __name__ == "__main__":
    app.run(main)

