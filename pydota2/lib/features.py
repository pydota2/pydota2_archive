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
"""Transform Dota2 protobuf observations into numpy arrays."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
from absl import logging

import enum
import numpy as np
import six

from pydota2.lib import actions
from pydota2.lib import stopwatch

from pydota2.protobuf import CMsgBotWorldState_pb2 as d2_pb

sw = stopwatch.sw

"""
THIS FILE IS NOT COMPLETE AND WILL NOT COMPILE CURRENTLY
"""

class Features(object):
    """
    """

    def __init__(self):
        self._valid_functions = self._init_valid_functions()

    def observation_spec(self):
        """
        The observation specification for the Dota2 environment.

        Returns:
            The dict of observation names to their tensor shapes. Shapes with a 0 can
            vary in length, for example the number of valid actions depends on which
            units you have selected.
        """

        return {
            "player": (11,),
        }

    def action_spec(self):
        return self._valid_functions

    @sw.decorate
    def transorm_obs(self, obs):
        """Render some Dota2 observations into somethin an agent can handle."""
        empty = np.array([], dtype=np.int32).reshape((0,7)) #TODO - fix sizes once implemented
        out = {}

        out['player'] = np.array([
            obs.player_common.net_worth,
        ], dtype=np.int32)

        out['available_actions'] = np.array(self.available_actions(obs), dtype=np.int32)

        return out

    @sw.decorate
    def available_actions(self, obs):
        """Return a list of available action ids."""
        available_actions = set()
        
        for i, func in six.iteritems(actions.FUNCTIONS_AVAILABLE):
            if func.avail_fn(obs):
                available_actions.add(i)

        return list(available_actions)

    def _init_valid_functions(self):
        """Initialize ValidFunctions and setup the callbacks."""
        
        return actions.ValidActions(types, functions)
