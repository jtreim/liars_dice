import copy
import random
from typing import List

from utils.color_printer import ColorPrinter, Color
from player.player import Player
from game.round import Round
from player.strategy.strategy import Strategy
from player.strategy.jeff.bad_strategy import BadStrategy


class LiarDiceGame:
  def __init__(self, players: List[Player], verbose=False):
    self.players = players
    self.round_number = 0
    self.verbose = verbose

  def get_active_players(self, starting_player, player_list):
    """
    Gets the list of players for the next round.
    Organized in turn order, beginning with the player to start the round
    """
    active_players = []
    for i in range(0, len(player_list)):
      idx = (i + starting_player) % len(player_list)
      if player_list[idx].is_alive:
        active_players.append(player_list[idx])
    return active_players

  def shuffle_players(self):
    shuffled_list = copy.deepcopy(self.players)
    random.shuffle(shuffled_list)
    return shuffled_list

  def play_game(self):
    starting_player = 0
    current_players = self.shuffle_players()
    standings = []

    while len([p for p in current_players if p.is_alive]) > 1:
      self.round_number += 1
      if self.verbose:
        print(f"\n\n----- {ColorPrinter.BLUE_TEXT}Round {self.round_number}{ColorPrinter.RESET_TEXT} -----")
      round = Round(self.get_active_players(starting_player, current_players), self.verbose)
      round_winner, round_loser = round.play()
      round_loser.num_dice -= 1
      if not round_loser.is_alive:
        current_players.remove(round_loser)
        standings.insert(0, round_loser)
        if self.verbose:
          msg = "{} has been eliminated.".format(round_loser.name)
          ColorPrinter.cprint(Color.YELLOW, msg)

      # start next round with whoever won the last round
      starting_player = current_players.index(round_winner)

    # The last one standing won
    if len(current_players) != 1:
      ColorPrinter.cprint(Color.RED, "********* Unknown Error: Unable to determine winner! **********")
    else:
      standings.insert(0, current_players[0])

      # update all the player stats with their results
      for placing, player in enumerate(standings):
        player.stats.performance.append(placing)
        player.stats.dice_left.append(player.num_dice)

      if self.verbose:
        self.print_standings(standings)
      return standings

  def print_standings(self, standings):
    print(f"\n\n---------- {ColorPrinter.CYAN_TEXT}Game Over!{ColorPrinter.RESET_TEXT} ----------")
    placement = 1
    for player in standings:
      if placement == 1:
        print(f"{ColorPrinter.GREEN_TEXT}Winner{ColorPrinter.RESET_TEXT}: {player.name} {ColorPrinter.BLACK_TEXT}({player.num_dice} dice remaining){ColorPrinter.RESET_TEXT}")
        print(player.stats)
      elif placement != len(standings):
        print(f"{placement}: {player.name}")
        print(player.stats)
      else:
        print(f"{ColorPrinter.RED_TEXT}{placement}{ColorPrinter.RESET_TEXT}: {player.name}")
        print(player.stats)
      placement += 1


if __name__ == "__main__":
  # Create players
  players = [
    Player("Alice", Strategy),
    Player("Bob", Strategy),
    Player("Charlie", Strategy),
    Player("Diana", Strategy),
    Player("Jeff", BadStrategy)
  ]
  game = LiarDiceGame(players, verbose=True)
  game.play_game()