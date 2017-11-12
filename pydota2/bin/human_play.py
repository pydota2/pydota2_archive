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

import importlib
import threading

from future.builtins import range    # pylint: disable=redefined-builtin

from pydota2.env import available_actions_printer
from pydota2.env import run_loop
from pydota2.env import dota2_env
from pydota2.lib import stopwatch

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
flags.DEFINE_bool("render", False, "Whether to render with pygame.")
flags.DEFINE_integer("max_agent_steps", 10000, "Total agent steps.")
flags.DEFINE_integer("game_steps_per_episode", 0, "Game steps per episode.")
flags.DEFINE_integer("step_mul", 8, "Game steps per agent step.")
flags.DEFINE_string("agent", "pydota2.agents.random_agent.RandomAgent", "Which agent to run")
flags.DEFINE_enum("difficulty", None, dota2_env.difficulties.keys(), "Bot's strength.")
flags.DEFINE_bool("profile", False, "Whether to turn on code profiling.")
flags.DEFINE_bool("trace", False, "Whether to trace the code execution.")
flags.DEFINE_integer("parallel", 1, "How many instances to run in parallel.")

flags.mark_flag_as_required("team")


def run_agent_thread(agent_cls, visualize):
    print("Starting Thread for Agent(s)")
    with dota2_env.Dota2Env(
            difficulty=FLAGS.difficulty,
            step_mul=FLAGS.step_mul,
            game_steps_per_episode=FLAGS.game_steps_per_episode,
            visualize=visualize) as env:
        env = available_actions_printer.AvailableActionsPrinter(env)
        agent = agent_cls()
        run_loop.run_loop([agent], env, FLAGS.max_agent_steps)
        if FLAGS.save_replay:
            env.save_replay(agent_cls.__name__)

            
def processData(data):
    data_frame = _pb.CMsgBotWorldState()
    data_frame.ParseFromString(data)
    #print('Data:\n%s' % str(data_frame))


def main(unused_argv):
    """Run an agent."""
    stopwatch.sw.enabled = FLAGS.profile or FLAGS.trace
    stopwatch.sw.trace = FLAGS.trace

    PORT = BASE_PORT + dota2_env.teams[FLAGS.team]  # Assert the team was selected
    
    # move over all the bot code to correct steam location so when a bot
    # game is launched it reads it from the Local Dev Script default location
    prep_dota_client.main(None)

    threads = []
    try:
        # create our CMsgBotWorldState threads
        thread_proto = ProtoThread(1, FLAGS.team, save_proto=FLAGS.save_replay, func_callback=processData)
        thread_http = ClientThread(2, FLAGS.team, PORT)
        
        agent_module, agent_name = FLAGS.agent.rsplit(".", 1)
        agent_cls = getattr(importlib.import_module(agent_module), agent_name)
        
        # Start our protocol threads
        thread_proto.start()
        thread_http.start()
        
        # Append our protocol threads to list
        threads.append(thread_proto)
        threads.append(thread_http)
        
        # if we are running multiple agents, start and append them
        for _ in range(FLAGS.parallel - 1):
            t = threading.Thread(target=run_agent_thread, args=(agent_cls, False))
            t.start()
            threads.append(t)
            
        # and start our main agent (or only agent if only running one)
        t = threading.Thread(target=run_agent_thread, args=(agent_cls, FLAGS.render))
        t.start()
        threads.append(t)

    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
    finally:
        # Wait for all threads to complete
        for t in threads:
            t.join()

    if FLAGS.profile:
        print(stopwatch.sw)

if __name__ == "__main__":
    app.run(main)

