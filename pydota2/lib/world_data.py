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

import math
import six
import collections
from pydota2.lib.client_connector import getRttQueue
import pydota2.lib.location as loc
from pydota2.lib.gfile import *
import json


def load_json_file(fname):
    fname = JoinPath('pydota2', 'gen_data', fname)
    with open(fname, 'r') as infile:
        return json.load(infile)

        
ability_data = None
hero_data = None
unit_data = None

"""
THIS FILE IS NOT COMPLETE ALTHOUGH IT WILL COMPILE
"""

class HeroSelectionData(object):
    """Handle initial data durning hero selection."""
    
    def __init__(self, data):
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in hero selection
        assert data.game_state == 3
        

class AbilityData(object):
    """Maintain certain information about abilities."""
    def __init__(self, id, data):
        self.ability_id = id
        self.data = data
    
    def get_name(self):
        return ability_data[str(self.ability_id)]['Name']
    
    def get_level(self):
        return self.data.level
    
    def is_hidden(self):
        return 'Hidden' in ability_data[str(self.ability_id)].keys()
        
    def is_ultimate(self):
        return 'Ultimate' in ability_data[str(self.ability_id)].keys()
        
    def get_ult_starting_level(self):
        if 'LevelAvailable' in ability_data[str(self.ability_id)].keys():
            return ability_data[str(self.ability_id)]['LevelAvailable']
        else:
            return 6
    
    def get_ult_level_interval(self):
        if 'LevelsBetweenUpgrades' in ability_data[str(self.ability_id)].keys():
            return ability_data[str(self.ability_id)]['LevelsBetweenUpgrades']
        else:
            return 6


# NOTE: Items are "abilities" in all respects in Dota2
class ItemData(object):
    """Maintain certain information about items."""
    def __init__(self, id, data):
        self.item_id = id
        self.data = data
    
    def get_name(self):
        return ability_data[str(self.item_id)]['Name']

        
class PlayerData(object):
    """Maintain certain information about our players."""
    def __init__(self, pID, heroID):
        self.pid = pID
        self.hero_id = heroID
        self.prtt = collections.deque(maxlen=10)
        self.avg_prtt = 0.3
        self.abilities = []
        self.items = []
    
    def save_last_update(self, udata, pdata):
        self.pdata = pdata
        self.udata = udata
        self.update_abilities()
        self.update_items()
    
    def get_name(self):
        return hero_data[str(self.hero_id)]['Name']
        
    def get_talent_choice(self, tier):
        if 'Talents' in hero_data[str(self.hero_id)].keys():
            talents = hero_data[str(self.hero_id)]['Talents']
            tier = (tier-1)*2+1
            return talents['Talent_'+str(tier)], talents['Talent_'+str(tier+1)]
        else:
            return None, None
    
    def _update_prtt(self, prtt):
        self.prtt.append(prtt)
        self.avg_prtt = sum(self.prtt)/float(len(self.prtt))
    
    def is_alive(self):
        return self.pdata.is_alive
    
    def get_location(self):
        return loc.Location.build(self.udata.location)

    def get_location_xyz(self):
        l = self.get_location()
        return l.x, l.y, l.z
        
    def get_turn_rate(self):
        if 'TurnRate' in hero_data[str(self.hero_id)].keys():
            return hero_data[str(self.hero_id)]['TurnRate']
        else:
            print('<ERROR>: Missing TurnRate for pID: %d' % self.hero_id)
            return 0.5
    
    def time_to_face_heading(self, heading):
        # we want a facing differential between 180 and -180 degrees
        # since we will always turn in the direction of smaller angle,
        # never more than a 180 degree turn
        diff = math.fabs(heading - self.udata.facing)
        if diff > 180.0:
            diff = math.fabs(360.0 - diff)
        time_to_turn_180 = 0.03*math.pi/self.get_turn_rate()
        #print("[%d] Facing: %f, Heading: %f, Diff: %f, TurnTime180: %f, TimeToTurn: %f" % 
        #     (self.pid, self.udata.facing, heading, diff, time_to_turn_180, (diff/180.0)*time_to_turn_180))
        return (diff/180.0)*time_to_turn_180

    def time_to_face_location(self, location):
        loc_delta = loc.Location.build(location) - self.get_location()
        desired_heading = math.degrees(math.atan2(loc_delta.y, loc_delta.x))
        return self.time_to_face_heading(desired_heading)
        
    def get_reachable_distance(self, time_adj=0.0):
        currSpd = self.udata.current_movement_speed
        timeAvail = self.avg_prtt - time_adj
        dist = timeAvail * currSpd
        #print("[%d] Speed: %f, TimeAvail: %f, Reachable Distance: %f" % 
        #     (self.pid, currSpd, timeAvail, dist))
        return dist

    def max_reachable_location(self, heading):
        ttfh = self.time_to_face_heading(heading)
        max_reachable_dist = self.get_reachable_distance(ttfh)
        rad_angle = math.pi/2.0 - math.radians(heading)
        l = self.get_location()
        retLoc = loc.Location(l.x + 5.0*max_reachable_dist*math.cos(rad_angle), 
                              l.y + 5.0*max_reachable_dist*math.sin(rad_angle),
                              l.z)
        return retLoc
    
    def update_abilities(self):
        self.abilities = []
        for ab in self.udata.abilities:
            self.abilities.append(AbilityData(ab.ability_id, ab))
    
    def update_items(self):
        self.items = []
        for item in self.udata.items:
            self.items.append(ItemData(item.ability_id, item))
    
    def get_abilities(self):
        return self.abilities
        
    def get_level(self):
        return self.udata.level
        
    def get_items(self):
        return self.udata.items
        
    def get_is_stunned(self):
        return self.udata.is_stunned
        
    def get_is_rooted(self):
        return self.udata.is_rooted
        
class WorldData(object):
    """Expose world data in a more useful form than the raw protos."""

    def __init__(self, data):
        global ability_data, hero_data, unit_data
        """Takes data from Valve provided JSON-like text files."""
        # make sure we are in game
        assert data.game_state in [4,5]
        
        ability_data = load_json_file('abilities.json')
        hero_data = load_json_file('heroes.json')
        unit_data = load_json_file('units.json')
        
        self.team_id = data.team_id
        self.player_data = {}
        self.last_update = -1000.0
               
        self._create_units(data.units)
        self._update_players(data.players)
        
        for player_id in self.good_players.keys():
            self.player_data[player_id] = PlayerData(player_id, 
                self.good_players[player_id]['player'].hero_id)
            self.player_data[player_id].save_last_update(self.good_players[player_id]['unit'], 
                                                         self.good_players[player_id]['player'])
    
    def update_prtt(self):
        data, lock = getRttQueue()
        lock.acquire()
        if len(data) > 0 and data['Time'] > self.last_update:
            self.last_update = data['Time']
            for player_id in self.player_data.keys():
                if str(player_id) in data.keys():
                    self.player_data[player_id]._update_prtt(data[str(player_id)])
                    #print(player_id, " average RTT: ", self.get_player_prtt(player_id))
        lock.release()
        
    def get_player_prtt(self, player_id):
        return self.player_data[player_id].avg_prtt
    
    def update_world_data(self, data):
        # make sure we are in game
        assert data.game_state in [4,5]
        
        self._create_units(data.units)
        self._update_players(data.players)
        
        for player_id in self.good_players.keys():
            if not player_id in self.player_data.keys():
                self.player_data[player_id] = PlayerData(player_id, 
                    self.good_players[player_id]['player'].hero_id)
            self.player_data[player_id].save_last_update(self.good_players[player_id]['unit'], 
                                                         self.good_players[player_id]['player'])
        
        self.update_prtt()
        
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
        player = self.get_player_by_id(player_id)
        if player:
            skilled_pts = 0
            for ability in player.get_abilities():
                skilled_pts += ability.get_level()
            level = player.get_level()
            delta = level - skilled_pts - sum(1 for v in [17, 19, 21, 22, 23, 24] if level >= v)
            #if delta > 0:
            #    print('%s [Lvl: %d] is able to level %d abilities' % (player.get_name(), level, delta))
            return max(delta,0)
        return 0
        
    def get_unit_by_handle(self, unit_data, handle):
        for unit in unit_data:
            if unit.handle == handle:
                return unit
        return None

    def get_player_by_id(self, player_id):
        if player_id in self.player_data.keys():
            return self.player_data[player_id]
        return None

    def get_player_abilities(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.get_abilities()
        return []
    
    # this returns only ability IDs of abilties that can be leveled
    def get_player_ability_ids(self, player_id, bCanBeLeveled=True):
        if self.get_available_level_points(player_id) == 0:
            return []

        player = self.get_player_by_id(player_id)
        abilities = self.get_player_abilities(player_id)
        
        p_level = player.get_level()
        
        ids = []
        a_ids = []
        for ability in abilities:
            id = ability.ability_id
            a_ids.append(ability.get_name())
            
            # generic_hidden
            if id == 6251:
                continue
            
            # if we are considering level-based restrictions
            if bCanBeLeveled:
            
                # skip hidden abilities
                if ability.is_hidden():
                    continue

                
                a_level = ability.get_level()
                
                if a_level >= int(float(p_level/2.0)+0.5):
                    continue

                if ability.is_ultimate():
                    # can't level ultimate past 3 levels
                    if a_level >= 3:
                        continue
                        
                    start_level = ability.get_ult_starting_level()
                    level_interval = ability.get_ult_level_interval()
                    if p_level < start_level:
                        continue
                    if p_level < (start_level + (a_level * level_interval)):
                        continue
                else:
                    # can't level abilities past 4 levels (invoker exception)
                    if a_level >= 4:
                        continue
            
            # if we get here it can be leveled or we didn't care
            ids.append(ability.get_name())

        t1_talent_picked = False
        if p_level >= 10:
            choice_1, choice_2 = player.get_talent_choice(1)
            if (not choice_1 in a_ids) and (not choice_2 in a_ids):
                ids.append(choice_1)
                ids.append(choice_2)
            else:
                t1_talent_picked = True
        
        t2_talent_picked = False
        if p_level >= 15 and t1_talent_picked:
            choice_1, choice_2 = player.get_talent_choice(2)
            if (not choice_1 in a_ids) and (not choice_2 in a_ids):
                ids.append(choice_1)
                ids.append(choice_2)
            else:
                t2_talent_picked = True
        
        t3_talent_picked = False
        if p_level >= 20 and t2_talent_picked:
            choice_1, choice_2 = player.get_talent_choice(3)
            if (not choice_1 in a_ids) and (not choice_2 in a_ids):
                ids.append(choice_1)
                ids.append(choice_2)
            else:
                t3_talent_picked = True
        
        t4_talent_picked = False
        if p_level >= 25 and t3_talent_picked:
            choice_1, choice_2 = player.get_talent_choice(4)
            if (not choice_1 in a_ids) and (not choice_2 in a_ids):
                ids.append(choice_1)
                ids.append(choice_2)
            else:
                t4_talent_picked = True
                
        return ids

    def is_player_alive(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.is_alive()
        return False
    
    def is_player_stunned(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.get_is_stunned()
        return False
    
    def is_player_rooted(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.get_is_rooted()
        return False
    
    def get_player_items(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.get_items()
        return []

    def get_player_location(self, player_id):
        player = self.get_player_by_id(player_id)
        if player:
            return player.get_location()
        return loc.center
    
    def get_player_ids(self):
        return list(self.player_data.keys())
    
    @property
    def get_my_players(self):
        return self.good_players
        
    @property
    def get_my_minions(self):
        return self.good_hero_units
