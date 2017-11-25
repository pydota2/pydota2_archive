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
"""Basic Location class."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import random


class Location(collections.namedtuple("Location", ["x", "y", "z"])):
  """A basic Location class."""
  __slots__ = ()

  @classmethod
  def build(cls, obj):
    """Build a Location from an object that has properties `x`, `y` and `z`."""
    return cls(obj.x, obj.y, obj.z)

  @classmethod
  def unit_rand(cls):
    """Return a Location with x, y chosen randomly with 0 <= x < 1, 0 <= y < 1."""
    return cls(random.random(), random.random(), 0)
    
  @classmethod
  def uniform_rand(cls):
    """Return a Location with x, y chosen randomly with -1.0 <= x < 1.0, -1.0 <= y < 1.0"""
    return cls(random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), 0)

  def assign_to(self, obj):
    """Assign `x`, `y` and `z` to an object that has properties `x`, `y`, and `z`."""
    obj.x = self.x
    obj.y = self.y
    obj.z = self.z

  def dist(self, other):
    """Distance to some other point."""
    dx = self.x - other.x
    dy = self.y - other.y
    return math.sqrt(dx**2 + dy**2)

  def dist_sq(self, other):
    """Distance squared to some other point."""
    dx = self.x - other.x
    dy = self.y - other.y
    return dx**2 + dy**2

  def round(self):
    """Round `x` and `y` to integers."""
    return Location(int(round(self.x)), int(round(self.y)), int(round(self.z)))

  def floor(self):
    """Round `x` and `y` down to integers."""
    return Location(int(math.floor(self.x)), int(math.floor(self.y)), self.z)

  def ceil(self):
    """Round `x` and `y` up to integers."""
    return Location(int(math.ceil(self.x)), int(math.ceil(self.y)), self.z)

  def abs(self):
    """Take the absolute value of `x` and `y`."""
    return Location(abs(self.x), abs(self.y), self.z)

  def len(self):
    """Length of the vector to this point."""
    return math.sqrt(self.x**2 + self.y**2)

  def scale(self, target_len):
    """Scale the vector to have the target length."""
    return self * (target_len / self.len())

  def scale_max_size(self, max_size):
    """Scale this value, keeping aspect ratio, but fitting inside `max_size`."""
    return self * (max_size / self).min_dim()

  def scale_min_size(self, min_size):
    """Scale this value, keeping aspect ratio, but fitting around `min_size`."""
    return self * (min_size / self).max_dim()

  def min_dim(self):
    return min(self.x, self.y)

  def max_dim(self):
    return max(self.x, self.y)

  def transpose(self):
    """Flip x and y."""
    return Location(self.y, self.x, self.z)

  def rotate_deg(self, angle):
    return self.rotate_rad(math.radians(angle))

  def rotate_rad(self, angle):
    return Location(self.x * math.cos(angle) - self.y * math.sin(angle),
                 self.x * math.sin(angle) + self.y * math.cos(angle),
                 self.z)

  def rotate_rand(self, angle=180):
    return self.rotate_deg(random.randint(-angle, angle))

  def contained_circle(self, loc, radius):
    """Is this location inside the circle defined by (`loc`, `radius`)?"""
    return self.dist(loc) < radius

  def __str__(self):
    return "%.6f,%.6f,%.6f" % self

  def __neg__(self):
    return Location(-self.x, -self.y, self.z)

  def __add__(self, loc_or_val):
    if isinstance(loc_or_val, Location):
      return Location(self.x + loc_or_val.x, self.y + loc_or_val.y, self.z)
    else:
      return Location(self.x + loc_or_val, self.y + loc_or_val, self.z)

  def __sub__(self, loc_or_val):
    if isinstance(loc_or_val, Location):
      return Location(self.x - loc_or_val.x, self.y - loc_or_val.y, self.z)
    else:
      return Location(self.x - loc_or_val, self.y - loc_or_val, self.z)

  def __mul__(self, loc_or_val):
    if isinstance(loc_or_val, Location):
      return Location(self.x * loc_or_val.x, self.y * loc_or_val.y, self.z)
    else:
      return Location(self.x * loc_or_val, self.y * loc_or_val, self.z)

  def __truediv__(self, loc_or_val):
    if isinstance(loc_or_val, Location):
      return Location(self.x / loc_or_val.x, self.y / loc_or_val.y, self.z)
    else:
      return Location(self.x / loc_or_val, self.y / loc_or_val, self.z)

  def __floordiv__(self, loc_or_val):
    if isinstance(loc_or_val, Location):
      return Location(int(self.x // loc_or_val.x), int(self.y // loc_or_val.y), int(self.z))
    else:
      return Location(int(self.x // loc_or_val), int(self.y // loc_or_val), int(self.z))

  __div__ = __truediv__

center = Location(0, 0, 0)