# pydota2

DeepMind (the guys behind the recent AlphaGo RL approaches) have recently 
(about a month ago) began working on their next ambitious project, namely 
RL-based AI for StarCraft II (with support from Blizzard).

They have created an open-source framework for this work so others could 
get involved (the open-source is just for the interaction with the game 
and custom/mini-games, etc. - but no actual agent learning code is shared).
LINK: [DeepMind SC2 Project](https://github.com/deepmind/pysc2)

I have decided to port the applicable (aka useful) part of their framework 
to create an open-source Dota2 framework for RL-based AI approaches. Since 
a large part of their framework is used, the same license applies.

## How It Works

Currently the port of pysc2 and the extra development necessary for Dota2 
are a **Work-In-Progress**. A lot of things need to be modified from the SC2 
domain for Dota 2, b/c there is drastic differences between the Blizzard 
API and the Valve API for bot-scripting.

### Significant API Differences

+ Blizzard's API is presented in terms of graphical layers based on game UI.
  As a result, a lot of pysc2 code is about interpreting information that is
  presented at each layer (i.e., minimap, screen, unit-frame, etc.). Dota 2
  API gives us object handles for everything so we don't need to do any of
  this transformation or interpretation.
+ pysc2's approach is to have the agents replicate human-like actions by 
  essentially making clicks on the visual layers (e.g., mouse clicks on the
  minimap/screen), control groups selection via mouse click-and-drag to make
  a rectangle and select all units, etc.). They do make use of some hotkeys
  for unit actions (like train this unit, build this building, etc.). I do
  not believe we want to do this for pydota2 as IMHO it is an unnecessary 
  layer of complication and we have the ability to directly send actions to
  the hero (aka _agent_).

### Machine Learning Thoughts

Reinforcement Learning (in my eyes, remember I'm a noob here still), is very
reminiscent of the typical [OODA Loop](https://en.wikipedia.org/wiki/OODA_loop).

We have observation data about our environment that arrives in the form of
direclty queryable environment API or through CMsgBotWorldState data dumps;
we then have to _interpret_ that information and transform it against our
state space model to determine which state we are in (this is the O**O**DA
_orientation_ phase); we then decide what to do (this can be based on some
optimal value estimation in a refined model, through gradiant descent, or a 
random action if we are still learning); and finally we perform the selected
action in the real-environment and await feedback in terms of new observations
and a reward value. The reward estimation would have to be represented as a 
tuple with immediate reward, near-term reward, and long-term reward evaluation.

Critical to us will be the granularity and abstraction of the state space. The
richness of observations we have available to us is too rich (for example, we
know the location of every single tree that's visible and we could represent
this information in our state space and have separate state for tree XYZ being
there and not being there, and if it is there we could have the action to cut
it down with a quelling blade; but this would lead to a very huge state space
we could not realistically explore and optimize in a timely fashion). Figuring
out the appropriate world state abstraction layer is an important research 
item, and one that will take a lot of refinement. 

### Development Plan

#### Reinforcement Learning Strategy
This is very nebulous currently as I continue to play with various ideas in
my head. Please note, while I have been reading on various machine learning
strategies and approaches, I've only been at it for a month or so on spare 
time and I have yet to write my own environment, policy & value networks, 
loss function, etc. ergo I am **very noob** and possibly have some basic 
and fundamental misconceptions on the topic still. Feel free to correct me
and teach me if you see these.

My current thinking is the following:
1) We are going to need at least 2 separate policy networks (possibly 3) to 
deal with the various facets of the game like `objective thinking`, `lane 
group thinking`, and `independent hero thinking`. In my opinion, these can be
all developed independently and have no reliance on each other (meaning you can
learn one while having the actions of the other 2 hard-coded).
+ `objective thinking` to me is the high-level objective strategy we want to
learn which controls in which part of the map each of our heroes/units should
be and what they should be doing. Ideally it will learn how to perform both, 
offensive and defensive responses to things such as `split push`, `ratting`, 
`deathballing`, etc. Included in this will be collective team actions such as
using Shrines, Roshing, Item Purchasing (i.e., it's not a good idea to have
multiple of certain items on the team), Global Ability Usage, and Courier Usage.
+ `independent hero thinking` is all the strategy and action selection that 
corresponds to a specific hero and his current objective tasking. It only 
considers the hero's nearby localized surroundings for optimal action selection
in the localized state space representation. Concepts that we hopefully learn 
are things like `last hitting`, `maintaining lane equilibrium`, `effective 
item/ability usage`, `fighting and harassing enemy`, `jungling`, `denying`, 
`how creep/tower aggro works`, `neutral stacking\pulling`, `etc`. Included in 
this is the concept of minion/illusion management.
+ `lane group thinking` - in my head I currently am debating if this is a 
necessary layer or something that can be a part of or emerge from the 
`independent hero thinking`. My intention here is that we might want a layer
to represent `laning teams` and the strategies that evolve from mini-groups of
heroes working in a localized environment. Possible strategies here are `ganking`,
`baiting`, `forcing enemy out of lane and XP range`, `kill wombo-combos`, and 
even `defensive manuevers` such as enemy hero blocking for low-health friend 
running away.
2) Proper hero selection that accounts for hero synergies, counter-picks, 
banning certain counter-picks to our team, etc. are all a completely different
part of the whole system. They occur at a different point in time compared to 
actual game play, but are equally important. Accounted in our hero selection
would have to be the concept of hero roles (carry, support, etc.) and the 
initial laning assignments. This whole thing would be its own policy and AI
model.
3) It is my intention and hope that the code we write for #1 can be done with 
a hero-agnostic approach. For example, when we learn `creep blocking` I hope
we can achieve proper results using `model bounding box, turn rate, movement
speed, and current location` as inputs to the neural net, and thus abstract 
the actual knowledge of which hero it is away. Similarly, for ability use I 
hope we can represent abilities as inputs with certain features (i.e., is a 
stun, stuns for X.Y seconds, global, mana cost, raw damage, damage type, is 
passive, is AOE, AOE shape and size, provides buff, provides debuff, is a 
projectile, projectile speed, is channeled, is Aghs upgradable, etc.) and
thus we learn to use effectively an ability, rather than a specific hero's 
ability (thus even making our bots effective in Ability Draft).

#### Code Execution
My intention is that there will exist several ways to train the system and, 
therefore, run the system. The **main** entry points will all exist in the 
`pydota2/pydota2/bin` directory. These include:

1) `proto_ingest.py` - this creates two listening sockets for accepting
   protobuf CMsgBotWorldState dumps from the Dota2 client and simply stores
   them to file in separate directories, 1 .bin file per dump, per team.
   The directories are created in `pydota2/replays/` and are named as 
   `YYYY_MM_DD_HHmm_<team>` where team is either `Dire` or `Radiant`.
   
   The intention for creating these is to allow for crowd-sourced replay
   repository of games (with the hope of eventually getting Valve to support
   the CMsgBotWorldState dumps in actual game replay format :: meaning, I can
   download a professional game, and watch it while dumping the world state 
   every X frames) and thus use professional games as training fodder for AI.
   
   When using this mode you need to run Dota2 with the appropriate launch 
   options.
   
   Necessary Launch Options: 
   `-botworldstatetosocket_radiant 12120 -botworldstatetosocket_dire 12121`
   `-botworldstatetosocket_frames 10 -botworldstatesocket_threaded`
   
   **THIS MODE IS _COMPLETED_**
   
2) `replay_actions.py` - this mode is used to train our AI by parsing the replay
   recorded CMsgBotWorldState dumps acquired ourselves or from shared crowd-
   sourced data and stored in `pydota/replays/`.
   
   The plan here is to train our neural network by looking at the actions taken 
   by the heroes in the replay, comparing them against our policy and value 
   networks, and then by looking into the future frame dumps that occurred 
   evaluate and refine our networks based on the results of those actions as 
   what occurred in game.
   
   While ultimately we will want to train/re-train our agents using `custom`, 
   `self_play` and `human_play` modes, initially as we are figuring out the 
   appropriate world state model to use (_i.e._, what variables to tune, what
   knowledge to hardcode, what reward values to use, etc.) we will need a test
   corpus of data to quickly evaluate various approaches and how they converge.

   **THIS MODE IS A _WORK IN PROGRESS_**
   
   Currently the multi-process replay ingest framework that stores metrics 
   about its progress is complete. We do need to still address how many frames 
   to maintain in memory at the same time as loading a full replay all at once 
   can often-times eat up 2.5Gb of memory easily; therefore, when we are 
   evaluating several replays at the same time on a low-end system we can 
   easily use up all available system RAM.
   
   We next need to create a World State model to base our policy on; create 
   a set of valid Actions that each hero can take at each specific point in 
   time (aka frame) based on what hero they are, what items they have, what 
   abilities they skilled, etc.; write a sane valuation function so we can 
   evaluate actions as being good or bad and thus train our agents.

3) `custom_game_training.py` - this mode is used to train specific layers of
   the multi-layered policy network as well as a testbed for coding specific 
   ideas. Writing AI for Dota2 (a 5v5 real-time game) is ground-breaking work.
   There is a lot of unknowns in terms of how to do it right and even exactly
   what to do in the first place.
   
   Examples of possible custom games to create:
   * Creep Blocking
   * Learning to use a Specific Item/Ability - some items can be hardcoded, 
     but others are hard to code the conditions for optimal use (think Eul's).
   * Last Hitting
   * Jungling

   **THIS MODE IS _NOT YET STARTED_**
   
   The path forward is to leverage work of other individuals that already started
   down this path (with their permissio of course) in terms of creating custom 
   game scenarios and maps to train specific aspects of the game.

4) `self_play.py` - this mode is the main mode for training our system once we
   believe we have something solid in place. It is intended to work similar 
   to how AlphaGo Zero was created in that the AI learns by playing itself
   over and over and over and thus complete the coverage of its state space
   models and the evaluation of various actions so we can optimize decisions.
   
   To be realistic and timely we probably need Valve support for headless 
   high-speed capability to play games so we can run hundreds of thousands of
   games that will be required.

   **THIS MODE IS _NOT YET STARTED_**

5) `human_play.py` - this mode is more reminiscent of the original AlphaGo
   approach, in that supervised learning occurs. We can refine our system by 
   playing progressively better teams of human players to further learn and 
   improve our strategies and understanding of the game. 

   **THIS MODE IS _NOT YET STARTED_**
   
   This mode of training will require the same code base as `self_play.py` in 
   terms of setting up our models, environment, etc. The only difference is 
   that we will be controlling one side of the two-sides in the game (and as 
   a result, we will only need to be pulling world state data through our 
   network protobuf protocol for one side).

6) `unit_tests.py` - this is not really a mode per say, but a series of coded
   unit tests to help ensure that as we make changes to our code we don't 
   accidentally break certain functions/algorithms we have already developed. 
   
   This is inspired by the post [HERE](https://medium.com/@keeper6928/how-to-unit-test-machine-learning-code-57cf6fd81765)

   **THIS MODE IS _NOT YET STARTED_**
   
7) `<other methods>.py` - we might in the future come up with other methods
   of play we want to support (for example: human-assisted play where a human
   makes all the actions and we monitor the decisions and make suggestions or
   simply evaluate the quality and speed of the decisions to score the human).

The way to run these require you either set your PYTHONPATH variable to the
outer-most pydota2 directory explicitly or you set it temporarily for the 
current python run (this is if running in a command shell). Alternatively, you
can run this through an IDE like PyCharm which has option to include the base
directory into the PYTHONPATH for you when running.

#### If using command shell
On Windows:

`:> set PYTHONPATH=.`

`:> python pydota2\\pydota2\\bin\\<one of the 6 above .py files>`

On Linux\MacOS:

`:> PYTHONPATH=. python pydota2/pydota2/bin/<one of the 6 above .py files>`
   
## General TODOs
1) Decide what protobuf information (and any transformations on it or inference
   from it) are necessary to feed as `inputs` into our env model for detection
   of hidden layers.
2) Create a method for evaluating all possible actions each agent can take
   in a given state to enumerate all the transitions to **new_state** that can
   occur and thus complete our policy network.
3) Write our valuation functon for evaluating the goodness of an action. The 
   research here is what information to use as indicators of "good" and "bad" 
   and in what combination. Pure "net_worth" or "KDA" is not sufficient IMHO 
   as we all have seen teams win games that have 0 kills total, or teams come
   from behind a huge net worth deficit through _ratting_ strategies, etc. So
   how to to determine the value of an action (taking into account the effort 
   required to do action) and how far into the future to look in order to 
   evaluate the result of the action might not be immediately visible.
