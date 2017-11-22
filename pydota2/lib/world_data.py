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
import collections
from pydota2.gen_data.json_lookup import *
from pydota2.lib.client_connector import getRttQueue

"""
THIS FILE IS NOT COMPLETE ALTHOUGH IT WILL COMPILE
"""

class HeroSelectionData(object):
    """Handle initial data durning hero selection."""
    
    def __init__(self, data):
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in hero selection
        assert data.game_state == 3
        

class PlayerData(object):
    """Maintain certain information about our players."""
    def __init__(self, pid):
        self.pid = pid
        self.rtt = collections.deque(maxlen=10)
    
    def save_last_update(self, udata, pdata):
        self.pdata = pdata
        self.udata = udata
    
    def _update_rtt(self, rtt):
        self.rtt.append(rtt)
        self.avg_rtt = sum(self.rtt)/float(len(self.rtt))
        
class WorldData(object):
    """Expose world data in a more useful form than the raw protos."""

    def __init__(self, data):
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in game
        assert data.game_state in [4,5]
        
        self.team_id = data.team_id
        self.player_data = {}
        self.last_update = -1000.0
               
        self._create_units(data.units)
        self._update_players(data.players)
        
        for player_id in self.good_players.keys():
            self.player_data[player_id] = PlayerData(player_id)
            self.player_data[player_id].save_last_update(self.good_players[player_id]['unit'], 
                                                         self.good_players[player_id]['player'])
    
    def update_rtt(self):
        data, lock = getRttQueue()
        lock.acquire()
        if len(data) > 0 and data['Time'] > self.last_update:
            self.last_update = data['Time']
            for player_id in self.player_data.keys():
                if str(player_id) in data.keys():
                    self.player_data[player_id]._update_rtt(data[str(player_id)])
                    print(player_id, " average RTT: ", self.player_data[player_id].avg_rtt)
        lock.release()
    
    def update_world_data(self, data):
        # make sure we are in game
        assert data.game_state in [4,5]
        
        self._create_units(data.units)
        self._update_players(data.players)
        
        for player_id in self.good_players.keys():
            if not player_id in self.player_data.keys():
                self.player_data[player_id] = PlayerData(player_id)
            self.player_data[player_id].save_last_update(self.good_players[player_id]['unit'], 
                                                         self.good_players[player_id]['player'])
        
        self.update_rtt()
        
    def store_player_info(self, data):
        for player in self.good_players.keys():
            if not player in self.player_data.keys():
                self.player_data = self.good_players[player]

    def _create_units(self, unit_data):
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
                #print("INVALID UNIT TYPE:\n%s" % str(unit))
                bInvalidFound = True
    
    def _update_players(self, player_data):
        for player in player_data:
            if player.player_id in self.good_players.keys():
                self.good_players[player.player_id]['player'] = player
            elif player.player_id in self.bad_players.keys():
                self.bad_players[player.player_id]['player'] = player

    def get_available_level_points(self, player_id):
        if player_id in self.good_players.keys():
            skilled_pts = 0
            for ability in self.get_player_abilities(player_id):
                skilled_pts += ability.level
            level = self.good_players[player_id]['unit'].level
            delta = level - skilled_pts - sum(1 for v in [17, 19, 21, 22, 23, 24] if level >= v)
            if delta > 0:
                print('%s [Lvl: %d] is able to level %d abilities' % (self.good_players[player_id]['unit'].name, level, delta))
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
    
    # this returns only ability IDs of abilties that can be leveled
    def get_player_ability_ids(self, player_id, bCanBeLeveled=True):
        if self.get_available_level_points(player_id) == 0:
            return []
        
        abilities = self.get_player_abilities(player_id)
        ids = []
        for ability in abilities:
            id = ability.ability_id
            
            # generic_hidden
            if id == 6251:
                continue
            
            # if we are considering level-based restrictions
            if bCanBeLeveled:
            
                # skip hidden abilities
                if isAbilityHidden('abilities.json', str(id)):
                    continue

                player = self.get_player_by_id(player_id)
                p_level = player['unit'].level
                a_level = ability.level
                
                if a_level >= int(float(p_level/2.0)+0.5):
                    continue
                
                bUlt = isAbilityUltimate('abilities.json', str(id))
                if bUlt:
                    # can't level ultimate past 3 levels
                    if a_level >= 3:
                        continue
                        
                    start_level = getUltStartingLevel('abilities.json', str(id))
                    level_interval = getUltLevelInterval('abilities.json', str(id))
                    if p_level < start_level:
                        continue
                    if p_level < (start_level + (a_level * level_interval)):
                        continue
                else:
                    # can't level abilities past 4 levels (invoker exception)
                    if a_level >= 4:
                        continue
            ids.append(getNameOfKey('abilities.json', str(id)))
        
        #TODO - add Talents
        #tier = 1
        #choice_1, choice_2 = getTalentChoice(str(player_id), tier)
        #if choice_1 and choice_2:
        #    ids.append(choice_1)
        #    ids.append(choice_2)
        
        return ids

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
    
    def get_player_ids(self):
        return list(self.good_players.keys())
        
    def get_reachable_distance(self, player_id):
        return 0
    
    @property
    def get_my_players(self):
        return self.good_players
        
    @property
    def get_my_minions(self):
        return self.good_hero_units
