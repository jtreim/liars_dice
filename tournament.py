import copy
from typing import List

from player.strategy.jeff import bad_strategy
from utils.color_printer import *
from liars_dice import LiarDiceGame
from player.player import Player
from player.strategy import strategy

class Tournament:
  def __init__(self, players: List[Player], num_games=10000):
    self.num_games = num_games
    self.player_map = {}
    self.players = players
    for player in players:
      self.player_map[player.name] = player

  def run(self):
    for i in range(0, self.num_games):
      game = LiarDiceGame(copy.deepcopy(self.players))
      standings = game.play_game()
      for s in standings:
        self.player_map.get(s.name).stats = s.stats
    
    ColorPrinter.cprint(Color.CYAN, "\n******************** RESULTS ********************")
    for player in list(self.player_map.values()):
      ColorPrinter.cprint(Color.BLUE, player.name)
      print(player.stats)


if __name__ == "__main__":
  # Create players
  players = [
    Player("Alice", strategy.Strategy),
    Player("Bob", strategy.Strategy),
    Player("Charlie", strategy.Strategy),
    Player("Diana", strategy.Strategy),
    Player("Jeff", bad_strategy.BadStrategy)
  ]

  tournament = Tournament(players)
  tournament.run()
