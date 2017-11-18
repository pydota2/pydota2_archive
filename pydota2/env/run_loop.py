# NOTE: This code is to a large degree based on DeepMind work for 
#             AI in StarCraft2, just ported towards the Dota 2 game.
#             DeepMind's License is posted below.

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A run loop for agent/environment interaction."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time


def run_loop(agents, hs_agents, env, max_frames=0):
    """A run loop to have agents and an environment interact."""
    total_frames = 0
    start_time = time.time()

    action_spec = env.action_spec()
    observation_spec = env.observation_spec()
    
    for agent in agents:
        agent.setup(observation_spec, action_spec)
        
    for agent in hs_agents:
        print("IMPLEMENT HS AGENT SETUP")

    try:
        while True:
            timesteps = env.reset()
            for a in agents:
                a.reset()
            while True:
                total_frames += 1
                
                if timesteps[0].observation['game_loop'][0] in [4,5]:
                    actions = [agent.step(timestep, env.world_state())
                               for agent, timestep in zip(agents, timesteps)]
                    #print('run_loop actions:', actions)
                    if max_frames and total_frames >= max_frames:
                        return
                    if timesteps[0].last():
                        break
                    timesteps = env.step(actions)
                # TODO - fix below for Hero Selection
                else:
                    actions = [agent.step(timestep, env.world_state())
                               for agent, timestep in zip(agents, timesteps)]
                    if max_frames and total_frames >= max_frames:
                        return
                    if timesteps[0].last():
                        break
                    timesteps = env.step(actions)
    except KeyboardInterrupt:
        pass
    finally:
        elapsed_time = time.time() - start_time
        print("Took %.3f seconds for %s steps: %.3f fps" % (
                elapsed_time, total_frames, total_frames / elapsed_time))
