import copy
from math import comb
from typing import List

from utils.color_printer import *
from player.player import Player


class Round:
  """
  A single round of Liar's dice.
  A round lasts from the first bid until a player is challenged.
  """
  def __init__(self, players: List[Player], verbose: bool):
    self.players = players
    self.active_player_index = 0
    self.history = []  # list of (player_name, Bid)
    self.current_bid = None
    self.verbose = verbose

  @property
  def active_player(self):
    if self.active_player_index is None:
      return None
    return self.players[self.active_player_index]

  def next_player_index(self, current_index):
    idx = current_index + 1
    idx = idx % len(self.players)
    return idx

  def prev_player_index(self, current_index):
    idx = current_index - 1
    if idx < 0:
      idx += len(self.players)
    return idx

  def turns_until_player_turn(self, player: Player):
    """
    Calculate how many turns until `player`'s turn comes up again 
    in a cyclic order of alive players, starting from active player.
    """
    if self.active_player is None:
      return 0

    if self.active_player == player:
      # If asking about active player, turns until their next turn is 
      # the number of other players.
      return len(self.players) - 1

    # Otherwise, find player's position relative to active_player in turn order
    player_index = self.players.index(player)
    if player_index > self.active_player_index:
      return player_index - self.active_player_index - 1
    
    return len(self.players) - (self.active_player_index - player_index) - 1

  def count_matching_dice(self, dice: List[int], face_value: int) -> int:
    """
    Count how many dice match the face_value or are 1 (wild).
    """
    return sum(1 for d in dice if d == face_value or d == 1)

  def compute_probability(self, perspective_player) -> float:
    """
    Compute probability that the current bid is true from the perspective of a given player.
    If perspective_player is None, use the active player of the round.
    """
    if self.current_bid is None or perspective_player is None:
      return 1.0  # If no bid or no perspective player, trivial probability

    face_value = self.current_bid.face_value
    required = self.current_bid.number_of_dice

    # Total dice in play
    total_dice = sum(p.num_dice for p in self.players)

    # Known count from perspective player's dice
    known_count = sum(1 for d in perspective_player.dice if d == face_value or d == 1)

    # Unknown dice
    unknown_count = total_dice - len(perspective_player.dice)

    if known_count >= required:
      return 1.0

    needed = required - known_count

    # Probability that a single unknown die matches (face_value or 1): 1/3
    p_match = 1/3

    # Compute probability: at least needed out of unknown_count match
    prob = 0.0
    for k in range(needed, unknown_count + 1):
      prob += comb(unknown_count, k) * (p_match**k) * ((1 - p_match)**(unknown_count - k))

    return prob

  def resolve_call(self, all_dice, bidder, challenger, out_of_turn_call, probability) -> Player:
    if self.verbose:
      print(f"{challenger.name} {ColorPrinter.MAGENTA_TEXT}calls{ColorPrinter.RESET_TEXT}.")
      ColorPrinter.cprint(Color.CYAN, "-------------------------")
    bidder.stats.bids_called += 1
    challenger.stats.calls.append(probability)
    if out_of_turn_call:
      challenger.stats.calls_out_of_turn += 1
    matching_dice = self.count_matching_dice(all_dice, self.current_bid.face_value)
    loser = None
    winner = None
    color_code = ""
    if matching_dice >= self.current_bid.number_of_dice:
      winner = bidder
      loser = challenger
      bidder.stats.successful_bids += 1
      color_code = ColorPrinter.GREEN_TEXT
    else:
      winner = challenger
      loser = bidder
      challenger.stats.successful_calls += 1
      color_code = ColorPrinter.RED_TEXT
    if self.verbose:
      print(f"Total matching dice: {color_code}{matching_dice}{ColorPrinter.RESET_TEXT}. {loser.name} loses a die.")
    return winner, loser

  def bid_is_valid(self, bid) -> bool:
    total_dice = sum(p.num_dice for p in self.players)
    return bid.number_of_dice <= total_dice and bid.is_higher_than(self.current_bid)

  def reset(self):
    self.current_bid = None
    self.history = []

  def play(self):
    self.reset()
    if self.active_player is None or len(self.players) == 0 or self.active_player_index is None:
      # Shouldn't get here...
      return None

    # Roll dice
    dice_counts = []
    all_dice = []
    for p in self.players:
      p.roll_dice()
      dice_counts.append((p.name, len(p.dice)))
      all_dice.extend(p.dice)
      if self.verbose:
        print(f"{p.name}'s {ColorPrinter.BLACK_TEXT}dice:{ColorPrinter.RESET_TEXT} {p.dice}")
    
    if self.verbose:
      ColorPrinter.cprint(Color.CYAN, "-------------------------")

    loser = None
    while loser is None:
      # get the next bid
      bid = self.active_player.strategy.make_bid(
        copy.deepcopy(self.history),
        copy.deepcopy(self.current_bid),
        copy.deepcopy(dice_counts),
        (len(self.players) - 1),
        copy.deepcopy(self.active_player.dice),
      )
      
      # if the new bid isn't valid, force them to call the last bid
      if not self.bid_is_valid(bid):
        prev_player = self.players[self.prev_player_index(self.active_player_index)]
        return self.resolve_call(all_dice, prev_player, self.active_player, False, self.compute_probability(self.active_player))

      self.history.append((self.active_player.name, bid))
      self.current_bid = bid
      self.active_player.stats.bids += 1
      if self.verbose:
        print(f"{self.active_player.name} {ColorPrinter.BLACK_TEXT}bids{ColorPrinter.RESET_TEXT} {bid}{ColorPrinter.BLACK_TEXT}.{ColorPrinter.RESET_TEXT}")

      # otherwise, check to see if any players will challenge it
      player_to_call_index = self.next_player_index(self.active_player_index)
      for n in range(0, len(self.players) - 1):
        player_to_call = self.players[player_to_call_index]
        out_of_turn = n > 0
        probability = self.compute_probability(player_to_call)
        if player_to_call.strategy.challenge_bid(
          copy.deepcopy(self.history),
          copy.deepcopy(self.current_bid),
          copy.deepcopy(dice_counts),
          probability,
          self.turns_until_player_turn(player_to_call),
          copy.deepcopy(player_to_call.dice),
          out_of_turn
        ):
          return self.resolve_call(all_dice, self.active_player, player_to_call, out_of_turn, probability)

        player_to_call_index = (player_to_call_index + 1) % len(self.players)

      # no one challenged it, move on to the next round
      self.current_bid = bid
      self.active_player_index = self.next_player_index(self.active_player_index)
