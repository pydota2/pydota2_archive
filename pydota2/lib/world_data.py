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
"""Expose world data in a more useful form than the raw protos."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six

"""
THIS FILE IS NOT COMPLETE ALTHOUGH IT WILL COMPILE
"""

class HeroSelectionData(object):
    """Handle initial data durning hero selection."""
    
    def __init__(self, data):
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in hero selection
        assert data.game_state == 3
        

class WorldData(object):
    """Expose world data in a more useful form than the raw protos."""

    def __init__(self, data):
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in game
        assert data.game_state in [4,5]
        
        self.team_id = data.team_id
        
        self.create_units(data.units)
        self.update_players(data.players)

    def create_units(self, unit_data):
        self.good_players = {}  # on my team
        self.bad_players = {}   # on enemy team
        
        self.good_hero_units = []
        self.bad_hero_units = []
        
        self.good_courier = None
        self.bad_courier = None
        
        bInvalidFound = False
        for unit in unit_data:
            if unit.unit_type == 1:  # HERO
                if unit.team_id == self.team_id:
                    self.good_players[unit.player_id] = {'unit': unit}
                else:
                    self.bad_players[unit.player_id] = {'unit': unit}

            elif unit.unit_type == 2:  # CREEP HERO
                if unit.team_id == self.team_id:
                    self.good_hero_units.append(unit)
                else:
                    self.bad_hero_units.append(unit)
            
            elif unit.unit_type == 11:  # COURIER
                if unit.team_id == self.team_id:
                    self.good_courier = unit
                else:
                    self.bad_courier = unit
            
            elif unit.unit_type == 0:  # INVALID
                print("INVALID UNIT TYPE:\n%s" % str(unit))
                bInvalidFound = True
    
    def update_players(self, player_data):
        for player in player_data:
            if player.player_id in self.good_players.keys():
                self.good_players[player.player_id]['player'] = player
            elif player.player_id in self.bad_players.keys():
                self.bad_players[player.player_id]['player'] = player

    def get_available_level_points(self, player_id):
        if player_id in self.good_players.keys():
            skilled_pts = 0
            for ability in self.good_players[player_id]['unit'].abilities:
                skilled_pts += ability.level
            level = self.good_players[player_id]['unit'].level
            delta = level - skilled_pts - sum(1 for v in [17, 19, 21, 22, 23, 24] if level >= v)
            if delta > 0:
                print('%s is able to level %d abilities' % (self.good_players[player_id]['unit'].name, delta))
            return max(delta,0)
        return 0

    def get_unit_by_handle(self, unit_data, handle):
        for unit in unit_data:
            if unit.handle == handle:
                return unit
        return None

    def get_player_by_id(self, player_id):
        if player_id in self.good_players.keys():
            return self.good_players[player_id]
        elif player_id in self.bad_players.keys():
            return self.bad_players[player_id]
        return None

    def get_player_abilities(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player['unit'].abilities
        return []

    def get_player_items(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player['unit'].items
        return []

    def get_player_location(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player['unit'].location
        return []
        
    @property
    def get_my_players(self):
        return self.good_players
        
    @property
    def get_my_minions(self):
        return self.good_hero_units
