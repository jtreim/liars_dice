class PlayerStats:
  def __init__(self):
    self.performance = []
    self.bids = 0
    self.calls = []
    self.bids_called = 0
    self.successful_bids = 0
    self.successful_calls = 0
    self.calls_out_of_turn = 0
    self.dice_left = []

  @property
  def wins(self):
    return sum(1 for p in self.performance if p == 0)

  @property
  def avg_performance(self):
    if len(self.performance) > 0:
      return round((sum(self.performance) + len(self.performance)) / len(self.performance), 2)
    return None

  @property
  def games(self):
    return len(self.performance)

  @property
  def avg_call_probability(self):
    if len(self.calls) > 0:
      return round(sum(self.calls) / len(self.calls), 2)
    return 0

  @property
  def call_accuracy(self):
    if len(self.calls) > 0:
      return round(self.successful_calls / len(self.calls), 2)
    return 1

  @property
  def bid_accuracy(self):
    if self.bids_called > 0:
      return round(self.successful_bids / self.bids_called, 2)
    return 1
  
  @property
  def winning_dice(self):
    return [dice for dice in self.dice_left if dice > 0]

  @property
  def avg_dice_left(self):
    if len(self.winning_dice) > 0:
      return round(sum(self.winning_dice) / len(self.winning_dice))
    return 0

  def update(self, other: 'PlayerStats'):
    self.performance.extend(other.performance)
    self.bids += other.bids
    self.calls.extend(other.calls)
    self.bids_called += other.bids_called
    self.successful_bids += other.successful_bids
    self.successful_calls += other.successful_calls
    self.calls_out_of_turn += other.calls_out_of_turn
    self.dice_left.extend(other.dice_left)

  def reset(self):
    self.performance = []
    self.bids = 0
    self.calls = []
    self.bids_called = 0
    self.successful_bids = 0
    self.successful_calls = 0
    self.calls_out_of_turn = 0
    self.dice_left = []

  def __repr__(self):
    return f"""-------------- {self.games} Games --------------
| performance -- w: {self.wins}, avg: {self.avg_performance}
| bids -- Total: {self.bids}, c: {self.bids_called}, s: {self.successful_bids}, acc: {self.bid_accuracy},
| calls -- Total: {len(self.calls)}, oot: {self.calls_out_of_turn}, s: {self.successful_calls}, avg: {self.avg_call_probability}, acc: {self.call_accuracy},
| dice left -- Total: {self.avg_dice_left}
-------------------------------------
"""