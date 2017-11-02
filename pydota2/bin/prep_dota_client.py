# NOTE: This code is to a large degree based on DeepMind work for
#       AI in StarCraft2, just ported towards the Dota 2 game.
#       DeepMind's License is posted below.

#!/usr/bin/python
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

#
# NOTE: This assumes that your Dota2 install was using default
#       install parameters, if not, please modify paths below

"""Move all the bot-code to the appropriate steam/dota2 directories."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys

from pydota2.lib import gfile

from absl import app

BOT_REPO = JoinPath('pydota2', 'bot_code')
DEFAULT_WIN_INSTALL_PATH = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\dota 2 beta\\game\\dota\\scripts\\vscripts'
DEFAULT_LIN_INSTALL_PATH = 'TODO'


def main(unused_argv):
    if sys.platform == 'linux':
        print('Linux')
        CopyDir(BOT_REPO, DEFAULT_LIN_INSTALL_PATH, update=1)
    elif sys.platform[:3] == 'win':
        print('Windows')
        CopyDir(BOT_REPO, DEFAULT_WIN_INSTALL_PATH, update=1)
    else:
        print('Unsupported OS: %s' % sys.platform)


if __name__ == "__main__":
  app.run(main)
