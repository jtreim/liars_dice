from game.bid import Bid

class Opponent:
  def __init__(self, name, turn, num_dice):
    self.name = name
    self.turn = turn
    self.num_dice = num_dice
    self.target_value = 0.0
    self.bids = []

  def update_target_value(self, last_bid=None):
    if last_bid is not None:
      self.bids.append(last_bid)
