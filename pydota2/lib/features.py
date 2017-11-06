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

Features for Dota 2 represent the layers of actionable interfaces the agent can
control. These are separated into types of controllable feature layersi where an
action at each layer can be taken simultaneously. 
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
    }


class GlyphFeatures(collections.namedtuple("GlyphFeatures", [
    "available"])):
    __slots__ = ()

    def __new__(cls, **kwargs):
        feats = {}
        for name, (scale, type_) in six.iteritems(kwargs):
            feats[name] = Feature(
                index=GlyphFeatures._fields.index(name),
                name=name
                scale=scale
                type=type_)
        return super(GlyphFeatures, cls).__new__(cls, **feats)


class Features(object):
    """
        Transform feature lauyers from Dota2 Observation protos into numpy arrays.

        This has the implementation details of how to transform a Dota 2 environment.
        It translates between agent action/observation formats and Dota 2 
        action/observations formats, which should not be seen by agent authors. The
        Dota 2 protos contain more information than is necessary.

        This is not part of the `environment` so that it can also be used in other 
        contexts, e.g. a supervised dataset pipeline.
    """

    def __init__(self, feature_layer, hide_specific_actions=True):
        """Initialize a Features instance."""
        self._feature_layer = feature_layer
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
