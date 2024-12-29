from typing import List, Tuple

from game.bid import Bid


class Strategy:
  def __init__(self, name):
    self.name = name

  """
  Base class for a strategy. 
  Strategies should implement:
  - challenge_bid(...):
      Returns True if the strategy suggests calling the current bid, False otherwise.
  - make_bid(...):
      Returns a valid higher bid. If the bid is deemed invalid, player is forced to call the last bid.
  """
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
    # Out-of-turn players can only call if they strongly suspect bluff,
    # or pass otherwise. Let's do a simple heuristic:
    # If probability < 0.4, call, else pass.
    return probability_of_truth < 0.4

  def prepare_for_new_round(
    self,
    dice_counts: List[Tuple[str, int]],
    my_dice: List[int]
  ):
    """
    Any setup to do at the start of the round to execute the strategy effectively.
    """
    # Any other setup desired for new rounds can be done here.
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
    if current_bid is None:
      return Bid(1, 2)
    else:
      if current_bid.face_value < 6:
        return Bid(current_bid.number_of_dice, current_bid.face_value + 1)
      else:
        return Bid(current_bid.number_of_dice + 1, current_bid.face_value)
