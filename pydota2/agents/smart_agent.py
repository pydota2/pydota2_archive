import sys
import random
import math
import json

import numpy as np

from pydota2.env import environment

from pydota2.agents import base_agent
from pydota2.lib import actions
from pydota2.lib import features
from pydota.ml_algo import QLearning
import pydota2.lib.location as loc

_NOT_QUEUED = [0]

_HERO_NO_OP = actions.FUNCTIONS.hero_no_op.id
_HERO_CLEAR_ACTION = actions.FUNCTIONS.hero_clear_action.id
_HERO_MOVE_TO_LOCATION = actions.FUNCTIONS.hero_move_to_location.id

ACTION_DO_NOTHING           = 'DoNothing'
ACTION_CLEAR_ACTION         = 'ClearAction'
ACTION_CLEAR_ACTION_STOP    = 'ClearActionStop'
ACTION_MOVE                 = 'Move'

smart_actions = [
    ACTION_DO_NOTHING,
    ACTION_CLEAR_ACTION,
    ACTION_CLEAR_ACTION_STOP,
]

# create our 8-directional moves
for mm_degree in range(0, 360, 45):
    smart_actions.append(ACTION_MOVE+ '_' + str(mm_degree))

TIME_STEP_REWARD        = -1.0
TIME_STEP_CLOSER_REWARD = -0.5
ARRIVED_AT_LOC_REWARD   = 10.0


class MoveAgent(base_agent.BaseAgent):
    def __init__(self):
        super(MoveAgent, self).__init__()
        
        self.qlearn = QLearning(actions=list(range(len(smart_actions))))
        
        self.dest_loc = loc.center

        self.previous_dist = {}
        self.previous_action = {}
        self.previous_state = {}
        
    def step(self, obs, world_state):
        super(MoveAgent, self).step(obs)
        
        #if self.steps >= 300:
        #    self.qlearn.dump_table()
        #    self._state = environment.StepType.LAST

        if not world_state:
            return []

        pids = world_state.get_player_ids()
        if len(pids) < 5:
            return []

        selected_actions = []
        for pid in pids:
            player = world_state.get_player_by_id(pid)
            player_loc = player.get_location()
            dist_to_loc = player_loc.dist(self.dest_loc)

            # initialize our previous variables if first valid step
            if not pid in self.previous_dist.keys():
                self.previous_dist[pid] = dist_to_loc
                self.previous_action[pid] = None
                self.previous_state[pid] = None
        
            loc_delta = self.dest_loc - player_loc
            desired_degree_facing = math.degrees(math.atan2(loc_delta.y, loc_delta.x))
            
            if desired_degree_facing < 22.5 or desired_degree_facing >= (360.0 - 22.5):
                desired_degree_facing = int(0)
            elif desired_degree_facing < (45.0+22.5) or desired_degree_facing >= 22.5:
                desired_degree_facing = int(45)
            elif desired_degree_facing < (90.0+22.5) or desired_degree_facing >= (90.0-22.5):
                desired_degree_facing = int(90)
            elif desired_degree_facing < (135.0+22.5) or desired_degree_facing >= (135.0-22.5):
                desired_degree_facing = int(135)
            elif desired_degree_facing < (180.0+22.5) or desired_degree_facing >= (180.0-22.5):
                desired_degree_facing = int(180)
            elif desired_degree_facing < (225.0+22.5) or desired_degree_facing >= (225.0-22.5):
                desired_degree_facing = int(225)
            elif desired_degree_facing < (270.0+22.5) or desired_degree_facing >= (270.0-22.5):
                desired_degree_facing = int(270)
            elif desired_degree_facing < (315.0+22.5) or desired_degree_facing >= (315.0-22.5):
                desired_degree_facing = int(315)
            else
                raise Exception("Bad Desired Angle: %f" % desired_degree_facing)

            # discretize our location to a square cell (200 units wide and tall)
            x_grid = int(player_loc.x / 200.0)
            y_grid = int(player_loc.y / 200.0)

            # estimated state space size: 156,800
            current_state = np.zeros(3)
            current_state[0] = x_grid                   # 140 x_grid values
            current_state[1] = y_grid                   # 140 y_grid values
            current_state[2] = desired_degree_facing    # 8 facing values

            # with 156,800 states and 11 possible actions we estimate our full
            # models contains 1,724,800 state-action nodes


            # if we previously took an action, evaluate its reward
            if self.previous_action[pid] is not None:
                reward = 0

                if dist_to_loc < 50:
                    reward += 10.0
                    self._state = environment.StepType.LAST
                elif dist_to_loc < self.previous_dist[pid]:
                    reward += -0.5
                elif dist_to_loc == self.previous_dist[pid]:
                    reward += -1.0
                else:
                    reward += -2.0
                
                # update our learning model with the reward for that action
                print("From State '%s' took Action '%s' and got '%f' reward arriving at new_state '%s'" % 
                      (self.previous_state[pid], self.previous_action[pid], reward, current_state))
                print("Prev Dist was '%f', New Dist is '%f'" % (self.previous_dist[pid], dist_to_loc))
                self.qlearn.learn(str(self.previous_state[pid]), self.previous_action[pid], reward, str(current_state))
            
            # choose an action to take give our learning model
            rl_action = self.qlearn.choose_action(str(current_state))
            smart_action = smart_actions[rl_action]
            
            self.previous_dist[pid] = dist_to_loc
            self.previous_state[pid] = current_state
            self.previous_action[pid] = rl_action
            
            degrees = 0
            if '_' in smart_action:
                smart_action, degrees = smart_action.split('_')
                degrees = int(degrees)
                
            if smart_action == ACTION_DO_NOTHING:
                selected_actions.append(actions.FunctionCall(pid, _HERO_NO_OP, []))

            elif smart_action == ACTION_CLEAR_ACTION:
                selected_actions.append(actions.FunctionCall(pid, _HERO_CLEAR_ACTION, [[0]]))
            
            elif smart_action == ACTION_CLEAR_ACTION_STOP:
                selected_actions.append(actions.FunctionCall(pid, _HERO_CLEAR_ACTION, [[1]]))
            
            elif smart_action == ACTION_MOVE:
                if _HERO_MOVE_TO_LOCATION in obs.observation["available_actions"][pid]:
                    selected_actions.append(actions.FunctionCall(pid, _HERO_MOVE_TO_LOCATION, 
                                            [player.max_reachable_location(degrees), _NOT_QUEUED]))
            else:
                selected_actions.append(actions.FunctionCall(pid, _HERO_NO_OP, []))

        return selected_actions
