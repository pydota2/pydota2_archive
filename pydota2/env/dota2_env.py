# NOTE: This code is to a large degree based on DeepMind work for 
#       AI in StarCraft2, just ported towards the Dota 2 game.
#       DeepMind's License is posted below.

"""A Dota 2 environment."""

"""
THIS FILE IS NOT COMPLETE AND WILL NOT COMPILE CURRENTLY
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import logging

from pydota2.env import environment

from pydota2.lib import stopwatch

sw = stopwatch.sw

difficulties = {
    "1": "Easy"
}

class Dota2Env(environment.Base):
    """
    A Dota 2 environment.
    The implementation details of the action and observation specs are in
    lib/features.py
    """

    def __init__(self, # pylint: disable=invalid-name
                )
        # pylint: disable=g-doc-args
		"""
		Create a Dota 2 Env

		Args:
			  _only_use_kwargs: Don't pass args, only kwargs.
		  discount: Returned as part of the observation.
		  agent_heroes: A list of Dota 2 heroes (max 5). These are the heroes you control.
		  enemy_heroes: A list of Dota 2 heroes (max 5). These are the heroes controlled by
			  the built-in bot.
		  difficulty: One of 1-9,A. How strong should the bot be?
		  step_mul: How many game steps per agent step (action/observation). None
			  means use the map default.
		  game_steps_per_episode: Game steps per episode, independent of the
			  step_mul. 0 means no limit. None means use the map default.
		  score_index: -1 means use the win/loss reward, >=0 is the index into the
			  score_cumulative with 0 being the curriculum score. None means use
			  the map default.
		  score_multiplier: How much to multiply the score by. Useful for negating.

		Raises:
		  ValueError: if the agent_heroes, enemy_heroes or difficulty are invalid.
		"""
		# pylint: enable=g-doc-args
		if _only_use_kwargs:
			raise ValueError("All arguments must be passed as keyword arguments.")

		agent_heroes = agent_heroes
		for agent_hero in agent_heroes:
			if agent_hero not in heroes:
				raise ValueError("Bad agent_hero args: %s" % (agent_hero))

		enemy_heroes = enemy_heroes
		for enemy_hero in enemy_heroes
			if enemy_hero not in heroes:
				raise ValueError("Bad enemy_hero args: %s" % (enemy_hero))

        difficulty = difficulty and str(difficulty) or "1"
        if difficulty not in difficulties:
            raise ValueError("Bad difficulty")

        self._num_players = 5

        self._setup((agent_heroes, enemy_heroes, difficulty), **kwargs)

    def _setup(self,
               player_setup,
               discount=1.0,
               step_mul=None,
               game_steps_per_episode=None):
        
        self._discount = discount
        self._step_mul = step_mul
        self._total_steps = 0

        self._last_score = None
        self._episode_length = game_steps_per_episode
        self._episode_steps = 0

        # TODO - need to add much more here

        self._episode_count = 0
        self._state = environment.StepType.LAST # Want to jump to `reset`.
        logging.info("Environment is ready.")

    def observation_spec(self):
        """Look at Features for full specs."""
        return self._features.observation_spec()

    def action_spec(self):
        """Look at Features for full specs."""
        return self._features.action_spec()

    def _restart(self):
        self._controllers[0].restart()

    @sw.decorate
    def reset(self):
        """Start a new episode."""
        self._episode_steps = 0
        if self._episode_count:
          	# No need to restart for the first episode.
          	self._restart()

        self._episode_count += 1
        logging.info("Starting episode: %s", self._episode_count)

        self._last_score = [0] * self._num_players
        self._state = environment.StepType.FIRST
        return self._step() 

    @sw.decorate
    def step(self, actions):
        """Apply actions, step the world forward, return observations."""
        if self._state == environment.StepType.LAST:
            return self.reset()

        # TODO - more
        
        self._state = environment.StepType.MID
        return self._step()

    def _step(self):
        # TODO - lots to fill out
        if self._state  == environment.StepType.LAST:
            logging.info("Episode finished. Outcome: %s, Reward: %s, Score: %s",
                         outcome, reward, [o["score_cumulative"][0] for o in agent_obs])

        return tuple()

    @property
    def state(self):
        return self._state

    def close(self):
        logging.info("Environment Close")

        if hasattr(self, "_controller") and self._controller:
            for c in self._controllers:
                c.quit()
            self._controllers = None

        logging.info(sw)
