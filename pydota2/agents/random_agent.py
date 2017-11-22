# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A random agent for Dota2."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy

from pydota2.agents import base_agent
from pydota2.lib import actions
from pydota2.gen_data.json_lookup import getNameOfKey

class RandomAgent(base_agent.BaseAgent):
    """
       A random agent for Dota2.
       It does NOT learn, just takes an available actions at a given time
       completely at random.
    """

    def step(self, obs, world_state):
        super(RandomAgent, self).step(obs)
        
        selected_actions = []
        if world_state:
            pIDs = world_state.get_player_ids()
            if len(pIDs) == 5:
                for player_id in pIDs:
                    function_id = numpy.random.choice(obs.observation['available_actions'][player_id])
                    print('RandomAgent chose random action: %d for player_id %d' % (function_id, player_id))
                    if function_id == 3:
                        ability_ids = world_state.get_player_ability_ids(player_id, True) #TODO - remove False when implemented
                        if len(ability_ids) > 0:
                            rand = numpy.random.randint(0, len(ability_ids))
                            name = ability_ids[rand]
                            print('PID: %d, Rand: %d, RandName: %s, AbilityIDS: %s' % (player_id, rand, name, str(ability_ids)))
                            args = [[name]]
                        else:
                            args = [[0]]
                    else:
                        args = [[numpy.random.randint(0, size) for size in arg.sizes]
                                for arg in self.action_spec.functions[function_id].args]
                    selected_actions.append(actions.FunctionCall(player_id, function_id, args))
                
                # now add team-wide functions, (we use pid = 0)
                function_id = numpy.random.choice(obs.observation['available_actions'][0])
                print('RandomAgent chose random action: %d for the team' % (function_id))
                args = [[numpy.random.randint(0, size) for size in arg.sizes]
                         for arg in self.action_spec.functions[function_id].args]
                selected_actions.append(actions.FunctionCall(0, function_id, args))

        #print("RandomAgent selected actions:", selected_actions)
        return selected_actions