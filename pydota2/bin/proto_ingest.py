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

"""Save protobuf serialized data from gameplay to replays directory."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pydota2.lib.proto_connector import ProtoThread

from absl import app


def main(unused_argv):
    threads = []
    try:
        # Create our threads and set func callback to our save to file function
        t1 = ProtoThread(1, 'Radiant', save_proto=True)
        t2 = ProtoThread(2, 'Dire', save_proto=True)

        # Start our threads
        t1.start()
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