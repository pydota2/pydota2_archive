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

"""Export just the bits of lib that an agent is likely to need.
See ../README.md for more information.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from pydota2.lib.actions import Arguments
from pydota2.lib.actions import FunctionCall
from pydota2.lib.actions import FUNCTIONS
from pydota2.lib.actions import TYPES
from pydota2.lib.features import FeatureType
#from pydota2.lib.features import GLYPH_FEATURES
#from pydota2.lib.features import PLAYER_FEATURES