import random
import math

import numpy as np
import pandas as pd

from pydota2.agents import base_agent
from pydota2.lib import actions
from pydota2.lib import features
from pydota2.lib import Location as loc

_NOT_QUEUED = [0]

_HERO_NO_OP = actions.FUNCTIONS.hero_no_op.id
_HERO_CLEAR_ACTION = actions.FUNCTIONS.hero_clear_action.id
_HERO_MOVE_TO_LOCATION = actions.FUNCTIONS.hero_move_to_location.id

ACTION_DO_NOTHING           = 'DoNothing'
ACTION_CLEAR_ACTION         = 'ClearAction'
ACTION_CLEAR_ACTOIN_STOP    = 'ClearActionStop'
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

# Based on https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow
class QLearningTable:
    def __init__(self, actions, learning_rate=0.01, reward_decay=0.9, e_greedy=0.9):
        self.actions = actions  # a list
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions)

    def choose_action(self, observation):
        self.check_state_exist(observation)
        
        if np.random.uniform() < self.epsilon:
            # choose best action
            state_action = self.q_table.ix[observation, :]
            
            # some actions have the same value
            state_action = state_action.reindex(np.random.permutation(state_action.index))
            
            action = state_action.argmax()
        else:
            # choose random action
            action = np.random.choice(self.actions)
            
        return action

    def learn(self, s, a, r, s_):
        self.check_state_exist(s_)
        self.check_state_exist(s)
        
        q_predict = self.q_table.ix[s, a]
        q_target = r + self.gamma * self.q_table.ix[s_, :].max()
        
        # update
        self.q_table.ix[s, a] += self.lr * (q_target - q_predict)

    def check_state_exist(self, state):
        if state not in self.q_table.index:
            # append new state to q table
            self.q_table = self.q_table.append(pd.Series([0] * len(self.actions), index=self.q_table.columns, name=state))


class MoveAgent(base_agent.BaseAgent):
    def __init__(self):
        super(MoveAgent, self).__init__()
        
        self.qlearn = QLearningTable(actions=list(range(len(smart_actions))))
        
        self.dest_loc = loc.center

        self.previous_dist = {}
        self.previous_action = {}
        self.previous_state = {}
        
    def step(self, obs, world_state):
        super(MoveAgent, self).step(obs)

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
            desire_degree_facing = math.degrees(math.atan2(loc_delta.y, loc_delta.x))

            current_state = np.zeros(1)
            current_state[0] = desired_degree_facing

            # if we previously took an action, evaluate its reward
            if self.previous_action[pid] is not None:
                reward = 0

                if dist_to_loc < 50:
                    reward += ARRIVED_AT_LOC_REWARD
                elif dist_to_loc < self.previous_dist[pid]:
                    reward += TIME_STEP_CLOSER_REWARD
                else:
                    reward += TIME_STEP_REWARD
                
                # update our learning model with the reward for that action
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
                selected_actions.append(actions.FunctionCall(pid, _HERO_CLEAR_ACTION, [0]))
            
            elif smart_action == ACTION_CLEAR_ACTION_STOP:
                selected_actions(actions.FunctionCall(pid, _HERO_CLEAR_ACTION, [1]))
            
            elif smart_action == ACTION_MOVE:
                if _HERO_MOVE_TO_LOCATION in obs.observation["available_actions"][pid]:
                    selected_actions.append(actions.FunctionCall(pid, _HERO_MOVE_TO_LOCATION, 
                                            [player.max_reachable_location(degrees), _NOT_QUEUED]))
            else:
                selected_actions.append(actions.FunctionCall(pid, _HERO_NO_OP, []))

        return selected_actions
