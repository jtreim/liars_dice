import random

from player.player_stats import PlayerStats
from player.strategy.strategy import Strategy


class Player:
  """
  Represents a player with a strategy.
  The dice are assigned by the game each round.
  """
  def __init__(self, name: str, strategy: Strategy, num_dice: int = 5):
    self.name = name
    self.dice = []
    self.num_dice = num_dice
    self.strategy = strategy
    self.stats = PlayerStats()

  def roll_dice(self):
    if self.is_alive:
      self.dice = [random.randint(1, 6) for _ in range(self.num_dice)]
    else:
      self.dice = []

  @property
  def is_alive(self):
    return self.num_dice > 0
