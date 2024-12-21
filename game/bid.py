class Bid:
  """
  A class representing a bid in Liar's Dice.
  A bid consists of a number_of_dice and a face_value (2-6),
  since '1' is treated as wild, we don't need to separate those out.
  """
  def __init__(self, number_of_dice: int, face_value: int):
    self.number_of_dice = number_of_dice
    self.face_value = face_value  # 2 through 6 for the face guessed

  def __repr__(self):
    return f"({self.number_of_dice} x {self.face_value})"

  def is_higher_than(self, other: 'Bid') -> bool:
    """
    Check if this bid is strictly higher than another bid according to standard Liar's Dice rules.
    """
    if other is None:
      return True
    
    if self.number_of_dice > other.number_of_dice and self.face_value >= other.face_value:
      return True
    
    return self.number_of_dice == other.number_of_dice and self.face_value > other.face_value
