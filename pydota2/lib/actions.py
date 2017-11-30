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
"""Define the static list of types and actions for Dota2."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import numbers

import six
from pydota2.lib import location


"""
THIS FILE IS NOT COMPLETE
"""


class ArgumentType(collections.namedtuple(
    "ArgumentType", ["id", "name", "sizes", "fn"])):
    """Represents a single argument type.
      Attributes:
        id: The argument id. This is unique.
        name: The name of the argument, also unique.
        sizes: The max+1 of each of the dimensions this argument takes.
        fn: The function to convert the list of integers into something more
            meaningful to be set in the protos to send to the game.
    """
    __slots__ = ()
    
    def __str__(self):
        return "%s/%s %s" % (self.id, self.name, list(self.sizes))

    @classmethod
    def enum(cls, options):
        """Create an ArgumentType where you choose one of a set of known values."""
        return cls(-1, "<none>", (len(options),), lambda a: options[a[0]])
    
    @classmethod
    def string(cls, string):
        """Create an ArgumentType with a single string in."""
        return cls(-1, "<none>", (string,), lambda a: a[0])
        
    @classmethod
    def scalar(cls, value):
        """Create an ArgumentType with a single scalar in range(value)."""
        return cls(-1, "<none>", (value,), lambda a: a[0])
    
    @classmethod
    def handle(cls, valid_handles):
        """Create an ArgumentType with a single handle value (uint32)."""
        return cls(-1, "<none>", (len(valid_handles),), lambda a: a[0])

    @classmethod
    def location(cls):  # No range because it's unknown at this time.
        """Create an ArgumentType that is represented by a location.Location."""
        return cls(-1, "<none>", (0, 0, 0), lambda a: location.Location(*a).floor())

    @classmethod
    def tree_id(cls, valid_tree_ids):
        """Create an ArgumentType that is a tree ID (uint32)."""
        return cls(-1, "<none>", (len(valid_tree_ids),), lambda a: a[0])
    
    @classmethod
    def spec(cls, id_, name, sizes):
        """Create an ArgumentType to be used in ValidActions."""
        return cls(id_, name, sizes, None)

class Arguments(collections.namedtuple("Arguments", [
    "player_id", "location", "handle", "tree_id", "ability_str",
    "queued", "bool"])):
    """The full list of argument types.
    Take a look at TYPES and FUNCTION_TYPES for more details.
    Attributes:
        location: A location vector (X, Y, Z(optional))
        obj_handle: a handle to a unit or ability object
        tree_id: A unique ID for a specific tree in map
        queued: Whether the action should be done now or later or over-write action.
        bool: A way to supply boolean (True / False) arguments to a command.
    """
    ___slots__ = ()
    
    @classmethod
    def types(cls, **kwargs):
        """Create an Arguments of the possible Types."""
        named = {name: type_._replace(id=Arguments._fields.index(name), name=name)
                for name, type_ in six.iteritems(kwargs)}
        return cls(**named)


ArgType_NORMAL  = 0
ArgType_PUSH    = 1
ArgType_QUEUE   = 2

# The list of known types.
TYPES = Arguments.types(
    bool = ArgumentType.enum([False, True]),
    queued = ArgumentType.enum([ArgType_NORMAL, ArgType_PUSH, ArgType_QUEUE]),
    player_id = ArgumentType.scalar(10),
    ability_str = ArgumentType.string(""),
    location = ArgumentType.location(),
    handle = ArgumentType.handle([0]),
    tree_id = ArgumentType.tree_id([0]),
)
        
# Which argument types do each function need?
FUNCTION_TYPES = {
    'cmd_atomic': [],
    'cmd_level_ability': [TYPES.ability_str],
    'cmd_ability': [],
    'cmd_ability_location': [TYPES.location],
    'cmd_ability_unit': [TYPES.handle],
    'cmd_ability_tree': [TYPES.tree_id],
    'cmd_ability_toggle': [], # for radiance, Medusa mana-shield, etc.
    'cmd_no_op': [],
    'cmd_bool': [TYPES.bool],
    'move_to_location': [TYPES.location, TYPES.queued],
    'attack_unit': [TYPES.handle],
}

# Which ones need an ability?
ABILITY_FUNCTIONS = {'cmd_ability'}

team_true = lambda pid, obs, ws: pid == 0
hero_true = lambda pid, obs, ws: pid > 0 and obs.game_state in [4,5]
    
class Function(collections.namedtuple(
    "Function", ["id", "name", "ability_id", "general_id", 
                 "args", "avail_fn"])):
    """Represents a function action.
    Attributes:
        id: The function id, which is what the agent will use.
        name: The name of the function. Should be unique.
        ability_id: The ability id to pass to dota2.
        general_id: 0 for normal abilities, and the ability_id of another ability if
            it can be represented by a more general action.
        function_type: One of the functions in FUNCTION_TYPES for how to send
            the dota2 action to hero in game.
        args: A list of the types of args passed to function_type.
        avail_fn: For non-abilities, this function returns whether the function is
            valid (enough mana and of cooldown).
    """
    __slots__ = ()

    @classmethod
    def pick_func(cls, id_, name, function_type, avail_fn=lambda pid, obs, ws: pid == 0 and obs.game_state == 3):
        """Define a function representing hero-selection actions take by hero-selection-agent."""
        return cls(id_, name, 0, 0, function_type, avail_fn)
        
    @classmethod
    def team_func(cls, id_, name, function_type, avail_fn=team_true):
        """Define a function representing team-wide actions take by master-agent."""
        return cls(id_, name, 0, 0, function_type, avail_fn)

    @classmethod
    def hero_func(cls, id_, name, function_type, avail_fn=hero_true):
        """Define a function representing a hero action."""
        return cls(id_, name, 0, 0, function_type, avail_fn)
    
    @classmethod
    def ability(cls, id_, name, function_type, ability_id, general_id=0, avail_fn=hero_true):
        """Define a function represented as a game ability."""
        return cls(id_, name, ability_id, general_id, function_type, avail_fn)
               
    @classmethod
    def spec(cls, id_, name, args):
        """Create a Function to be used in ValidActions."""
        return cls(id_, name, None, None, args, None)

    def __hash__(self):  # So it can go in a set().
        return self.id

    def __str__(self):
        return self.str()
    
    def str(self, space=False):
        """String version. Set space=True to line them all up nicely."""
        return "%s/%s (%s)" % (str(self.id).rjust(space and 5),
                           self.name.ljust(space and 50),
                           "; ".join(str(a) for a in self.args))
    
class Functions(object):
    """Represents the full set of functions.
    Can't use namedtuple since python3 has a limit of 255 function arguments, so
    build something similar.
    """

    def __init__(self, functions):
        self._func_list = functions
        self._func_dict = {f.name: f for f in functions}
        if len(self._func_dict) != len(self._func_list):
            raise ValueError("Function names must be unique.")

    def __getattr__(self, name):
        return self._func_dict[name]

    def __getitem__(self, key):
        if isinstance(key, numbers.Number):
            return self._func_list[key]
        return self._func_dict[key]

    def __iter__(self):
        return iter(self._func_list)

    def __len__(self):
        return len(self._func_list)
        
# pylint: disable=line-too-long
FUNCTIONS = Functions([
    Function.team_func(0, "team_glyph", FUNCTION_TYPES['cmd_atomic'],
                       lambda pid, obs, ws: pid == 0 and obs.game_state in [4,5] and 
                       (obs.glyph_cooldown == 0.0 or obs.glyph_cooldown < obs.dota_time)),  
    Function.hero_func(1, "hero_no_op", FUNCTION_TYPES['cmd_no_op']),
    Function.hero_func(2, "hero_clear_action", FUNCTION_TYPES['cmd_bool']),
    Function.hero_func(3, "hero_level_ability", FUNCTION_TYPES['cmd_level_ability'],
                       avail_fn=lambda pid, obs, ws: obs.game_state in [4,5] and 
                       pid > 0 and ws.get_available_level_points(pid) > 0),
    Function.hero_func(4, "hero_move_to_location", FUNCTION_TYPES['move_to_location'], 
                       avail_fn=lambda pid, obs, ws: obs.game_state in [4,5] and
                       pid > 0 and ws.is_player_alive(pid) and not ws.is_player_rooted(pid) and
                       not ws.is_player_stunned(pid)),
])
# pylint: enable=line-too-long

# Some indexes to support features.py and action conversion.
ABILITY_IDS = collections.defaultdict(set)  # {ability_id: {funcs}}
for func in FUNCTIONS:
    if func.ability_id >= 0:
        ABILITY_IDS[func.ability_id].add(func)
ABILITY_IDS = {k: frozenset(v) for k, v in six.iteritems(ABILITY_IDS)}
FUNCTIONS_AVAILABLE = {f.id: f for f in FUNCTIONS if f.avail_fn}


class FunctionCall(collections.namedtuple(
    "FunctionCall", ["player_id", "function", "arguments"])):
    """Represents a function call action.
      Attributes:
        player_id: Stores the intended bot of the FunctionCall, -1 for "any"/"world"
        function: Store the function id, eg 2 for select_location.
        arguments: The list of arguments for that function, each being a list of
                   ints. For select_location this could be: [[0], [23, 38]].
    """
    __slots__ = ()

    @classmethod
    def all_arguments(cls, player_id, function, arguments):
        """Helper function for creating `FunctionCall`s with `Arguments`.
        Args:
          function: The value to store for the action function.
          arguments: The values to store for the arguments of the action. Can either
            be an `Arguments` object, a `dict`, or an iterable. If a `dict` or an
            iterable is provided, the values will be unpacked into an `Arguments`
            object.
        Returns:
          A new `FunctionCall` instance.
        """
        if isinstance(arguments, dict):
            arguments = Arguments(**arguments)
        elif not isinstance(arguments, Arguments):
            arguments = Arguments(*arguments)
        return cls(player_id, [function, arguments])


class ValidActions(collections.namedtuple(
    "ValidActions", ["types", "functions"])):
    """The set of types and functions that are valid for an agent to use.
    Attributes:
      types: A namedtuple of the types that the functions require. Unlike TYPES
             above, this includes the sizes for screen and minimap.
      functions: A namedtuple of all the functions.
    """
    __slots__ = ()
