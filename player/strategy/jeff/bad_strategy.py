import copy
from math import comb
from typing import List, Tuple

from game.bid import Bid
from player.strategy.strategy import Strategy
from player.strategy.jeff.opponent import Opponent


class BadStrategy(Strategy):
  SAFE_BID_THRESHOLD = 0.7
  CHALLENGE_BID_THRESHOLD = 0.15

  def __init__(self, name):
    self.name = name
    self.my_turn = 0
    self.opponents = []
    self.my_dice = []
    self.valid_bids = {}
    self.total_dice = 0

  def determine_valid_bids(self):
    self.valid_bids.clear()
    for face_value in range(2, 7): # range end is exclusive
      self.valid_bids[face_value] = {}
      for number_of_dice in range(1, self.total_dice + 1):
        bid = Bid(number_of_dice, face_value)
        probability = self.compute_probability(bid)
        self.valid_bids[face_value][number_of_dice] = probability

  def determine_safe_bids_left(self, bid):
    safe_bids = []

    for number_of_dice in range(bid.number_of_dice + 1, self.total_dice + 1):
      if self.valid_bids[bid.face_value][number_of_dice] >= BadStrategy.SAFE_BID_THRESHOLD:
          safe_bids.append(Bid(number_of_dice, bid.face_value))

    for face_value in range(bid.face_value + 1, 7):
      for number_of_dice in range(bid.number_of_dice, self.total_dice + 1):
        if self.valid_bids[face_value][number_of_dice] >= BadStrategy.SAFE_BID_THRESHOLD:
          safe_bids.append(Bid(number_of_dice, face_value))

    return safe_bids

  def calc_needed_probability(self, needed, remaining):
    p_match = 1/3
    prob = 0.0
    for k in range(needed, remaining + 1):
      prob += comb(remaining, k) * (p_match**k) * ((1 - p_match)**(remaining - k))
    
    return prob

  def compute_probability(self, bid) -> float:
    """
    Compute the probability of the given bid with what I know
    """
    if bid is None or self.total_dice == 0:
      return 1.0  # If no bid or no known dice in play

    # Known count from perspective player's dice
    known_count = sum(1 for d in self.my_dice if d == bid.face_value or d == 1)

    # Unknown dice
    unknown_count = self.total_dice - len(self.my_dice)

    if known_count >= bid.number_of_dice:
      return 1.0

    needed = bid.number_of_dice - known_count

    # Probability that a single unknown die matches (face_value or 1): 1/3
    return self.calc_needed_probability(needed, unknown_count)

  def get_next_best_bid(self, current_bid):
    best_prob_diff = 0.0
    best_bid = Bid(1, 1)
    best_bid_prob = 0.0
    
    bid = Bid(1, 2)
    if current_bid is not None:
      bid.number_of_dice = current_bid.number_of_dice
      bid.face_value = current_bid.face_value
    else:
      best_bid = bid
      best_bid_prob = self.valid_bids[2][1]
      best_bid_prob = self.calc_needed_probability(1, self.total_dice - len(self.my_dice))


    # for face_value in range(current_bid.face_value, 7):
    #   for number_of_dice in range(current_bid.number_of_dice + 1, self.total_dice + 1):
    #     if best_probability < self.valid_bids[face_value][number_of_dice]:
    #       best_probability = self.valid_bids[face_value][number_of_dice]
    #       best_bid = Bid(number_of_dice, face_value)
    for number_of_dice in range(bid.number_of_dice + 1, self.total_dice + 1):
      bid_prob = self.valid_bids[bid.face_value][number_of_dice]
      opp_prob = self.calc_needed_probability(number_of_dice, self.total_dice - len(self.my_dice))
      prob_diff = bid_prob - opp_prob
      if best_prob_diff < prob_diff:
        best_prob_diff = prob_diff
        best_bid = Bid(number_of_dice, bid.face_value)
        best_bid_prob = self.valid_bids[bid.face_value][number_of_dice]

    for face_value in range(bid.face_value + 1, 7):
      for number_of_dice in range(bid.number_of_dice, self.total_dice + 1):
        bid_prob = self.valid_bids[face_value][number_of_dice]
        opp_prob = self.calc_needed_probability(number_of_dice, self.total_dice - len(self.my_dice))
        prob_diff = bid_prob - opp_prob
        if best_prob_diff < prob_diff:
          best_prob_diff = prob_diff
          best_bid = Bid(number_of_dice, face_value)
          best_bid_prob = self.valid_bids[face_value][number_of_dice]

    safer_bid = Bid(best_bid.number_of_dice, best_bid.face_value)
    if current_bid is not None and safer_bid.is_valid and safer_bid.is_higher_than(current_bid):
      best_bid_prob = self.valid_bids[safer_bid.face_value][safer_bid.number_of_dice]
      best_bid = safer_bid


    return best_bid, best_bid_prob

  def orient_turns_to_me(self):
    for i in range(0, len(self.opponents)):
      self.opponents[i].turn -= self.my_turn
      if self.opponents[i].turn < 0:
        self.opponents[i].turn += len(self.opponents) + 1
    self.my_turn = 0

  def get_target_index(self, safe_bids_left):
    highest_target = 0.0
    target_index = 1
    for opponent in self.opponents:
      if opponent.target_value > highest_target and opponent.turn <= safe_bids_left:
        highest_target = opponent.target_value
        target_index = opponent.turn

    return target_index * -1

  def challenge_bid(
    self,
    round_history: List[Tuple[str, Bid]],
    current_bid: Bid,
    dice_counts: List[Tuple[str, int]],
    probability_of_truth: float,
    turns_until_my_turn: int,
    my_dice: List[int],
    out_of_turn: bool
  ) -> bool:
    """
  Base class for a strategy. 
  Strategies should implement:
  - challenge_bid(...):
      Returns True if the strategy suggests calling the current bid, False otherwise.
  - make_bid(...):
      Returns a valid higher bid. If the bid is deemed invalid, player is forced to call the last bid.
  """
    if out_of_turn:
      return probability_of_truth < 0.1

    if current_bid is None:
      return False

    _, best_bid_probability = self.get_next_best_bid(current_bid)
    if probability_of_truth < BadStrategy.CHALLENGE_BID_THRESHOLD:
      return 1 - probability_of_truth > best_bid_probability

    return False
    # return probability_of_truth < BadStrategy.CHALLENGE_BID_THRESHOLD
    

  def prepare_for_new_round(
    self,
    dice_counts: List[Tuple[str, int]],
    my_dice: List[int]
  ):
    """
    Any setup to do at the start of the round to execute the strategy effectively.
    """
    self.my_dice = my_dice
    self.opponents.clear()
    self.total_dice = 0
    self.my_turn

    for turn, player_dice in enumerate(dice_counts):
      name = player_dice[0]
      num_dice = player_dice[1]
      if name == self.name:
        self.my_turn = turn
        continue
      self.total_dice += num_dice
      opponent = Opponent(name, turn, num_dice)
      opponent.update_target_value()
      self.opponents.append(opponent)

    self.orient_turns_to_me()
    self.determine_valid_bids()

    return

  def make_bid(
    self,
    round_history: List[Tuple[str, Bid]],
    current_bid: Bid,
    dice_counts: List[Tuple[str, int]],
    turns_until_my_turn: int,
    my_dice: List[int]
  ) -> Bid:
    """
    Make a valid higher bid.
    Example strategy:
      - If no current bid: start at (1,2).
      - If there is a bid: increment face value if possible, else increment number_of_dice.
    """
    bids_left = []
    best_bid, _ = self.get_next_best_bid(current_bid)
    # if current_bid is None:
      # bids_left = self.determine_safe_bids_left(Bid(1, 2))
    # else:
    return best_bid

    # if len(bids_left) == 0:
      # bids_left = self.determine_safe_bids_left(current_bid)
      # return best_bid

    # target_index = self.get_target_index(len(bids_left))
    # return bids_left[target_index]
