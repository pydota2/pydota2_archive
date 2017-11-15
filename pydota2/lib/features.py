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

Features for Dota 2 represent the structured data available to the agents.
These are separated into types of controllable features where an
action from each set can be taken simultaneously. 
These include:
    * Players (5 per team)
    * Illusions
    * Minions 
    * Courier
    * Ping (the ability to ping)
    * Purchasing
    * Glyph Usage
"""

class FeatureType(enum.Enum):
    """
        SCALAR represents things represented by a number (e.g., health)
        CATEGORICAL represents things belonging toa category (e.g, heroID, minionID)
        VECTOR represents things represented by a <X,Y,Z> float vector (e.g., Location)
    """
    SCALAR = 1
    CATEGORICAL = 2
    VECTOR = 3

class Feature(collections.namedtuple(
    "Feature", ["index", "name", "scale", "type"])):
    
    """Define properties of a feature layer.

    Attributes:
        index: Index of this layer into the set of layers.
        name: The name of the layer within the set.
        scale: Max value (+1) of this layer, used to scale the values.
        type: A FeatureType for scalar vs categorical vs vector.
    """
    __slots__ = ()

    dtypes = {
        1: np.uint8,
        8: np.uint8,
        16: np.uint16,
        32: np.uint32,
        64: np.uint64,
    }


class Features(object):
    """
        Transform structured Dota2 data (observation protobufs) into numpy arrays.

        This has the implementation details of how to transform a Dota 2 environment.
        It translates between agent action/observation formats and Dota 2 
        action/observations formats, which should not be seen by agent authors. The
        Dota 2 protos contain more information than is necessary.

        This is not part of the `environment` so that it can also be used in other 
        contexts, e.g. a supervised dataset pipeline.
    """

    def __init__(self, hide_specific_actions=True):
        """Initialize a Features instance."""
        self._hide_specific_actions = hide_specific_actions
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
            "team": (3,),
            "available_actions": (0,),
        }

    def action_spec(self):
        return self._valid_functions

    @sw.decorate
    def transform_obs(self, obs):
        """
           Transform Dota2 observations into something an agent can handle.
           Observations come to us through the CMsgBotWorldState protobufs, 
           and we have to select which pieces of data to send to our RL agent.
        """

        # empty np.array stub (for quick-reuse) # TODO - fix size once implemented
        empty = np.array([], dtype=np.int32).reshape((0,7))

        # prepare our output observations for agents RL, prefil those that might
        # be empty with emtpy stub in case they are not present in protobuf
        out = {}

        # team specific observations
        out['team'] = np.array([
            obs.dota_time,
            obs.time_of_day,
            obs.glyph_cooldown,
        ], dtype=np.float32)
        
        """
        # hero specific observations
        def hero_vec(u):
            return np.array((
                u.level,
                u.health,
                u.health_ratio,
                u.health_regen,
                u.mana,
                u.mana_ratio,
                u.mana_regen,
                u.net_worth,
                u.primary_attribute,
            ), dtype=np.float16)

        heroes = obs.players
        units = obs.units
        out['heroes'] = np.array([], dtype=np.float16)
        with sw('heroes'):
            for hero in heroes:
                for unit in units:
                    if unit.unit_type == 1 and unit.player_id == hero.player_id:
                        out['heroes'] = np.append(out['heroes'], hero_vec(unit))

        # unit specific observations
        """
        
        # comprehensive list of all available actions
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
    
    @sw.decorate
    def transform_action(self, obs, func_call, skip_available=False):
        """Tranform an agent-style action to one that Dota2 can consume.
        Args:
          obs: a `sc_pb.Observation` from the previous frame.
          func_call: a `FunctionCall` to be turned into a `sc_pb.Action`.
          skip_available: If True, assume the action is available. This should only
              be used for testing or if you expect to make actions that weren't
              valid at the last observation.
        Returns:
          a corresponding `sc_pb.Action`.
        Raises:
          ValueError: if the action doesn't pass validation.
        """
        func_id = func_call.function
        try:
            func = actions.FUNCTIONS[func_id]
        except KeyError:
            raise ValueError("Invalid function id: %s." % func_id)

        # Available?
        if not (skip_available or func_id in self.available_actions(obs)):
            raise ValueError("Function %s/%s is currently not available" % (
            func_id, func.name))

        # Right number of args?
        if len(func_call.arguments) != len(func.args):
            raise ValueError(
                "Wrong number of arguments for function: %s, got: %s" % (
                func, func_call.arguments))
        
        # Args are valid?
        for t, arg in zip(func.args, func_call.arguments):
            sizes = t.sizes
            
            if len(sizes) != len(arg):
                raise ValueError(
                    "Wrong number of values for argument of %s, got: %s" % (
                    func, func_call.arguments))
                    
            for s, a in zip(sizes, arg):
                if not 0 <= a < s:
                    raise ValueError("Argument is out of range for %s, got: %s" % (
                    func, func_call.arguments))
        
        return (func_call.player_id, func_id, func_call.arguments)
              
    @sw.decorate
    def reverse_action(self, action):
        """
           Transform a Dota2-style action into an agent-style action.
        """

        def func_call(func_id, args):
            return actions.FunctionCall(func_id, [[int(v) for v in a] for a in args])

        def func_call_ability(ability_id, cmd_type, args):
            """Get the function id for a specific ability id and action type."""
            if ability_id not in actions.ABILITY_IDS:
                logging.warning("Unknown ability_id: %s. Treating as a no-op.", ability_id)
                return func_call_name("no_op", [])

            if self._hide_specific_actions:
                general_id = next(iter(actions.ABILITY_IDS[ability_id])).general_id
                if general_id:
                    ability_id = general_id

            for func in actions.ABILITY_IDS[ability_id]:
                if func.function_type is cmd_type:
                    return func_call(func.id, args)

            raise ValueError("Unknown ability_id: %s, type: %s. Likely a bug." % (
                ability_id, cmd_type.__name__))

        def func_call_name(name, args):
            return func_call(actions.FUNCTIONS[name].id, args)

        return func_call_name("no_op", [])


    def _init_valid_functions(self):
        """Initialize ValidFunctions and setup the callbacks."""
        sizes = {
            "location": tuple(int(i) for i in (-7000,7000)),
        }
        
        types = actions.Arguments(*[
            actions.ArgumentType.spec(t.id, t.name, sizes.get(t.name, t.sizes))
            for t in actions.TYPES])

        functions = actions.Functions([
            actions.Function.spec(f.id, f.name, tuple(types[t.id] for t in f.args))
            for f in actions.FUNCTIONS])
        
        print(types)
        return actions.ValidActions(types, functions)
