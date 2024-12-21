from enum import Enum

class Color(Enum):
  BLACK = 1
  RED = 2
  GREEN = 3
  YELLOW = 4
  BLUE = 5
  MAGENTA = 6
  CYAN = 7
  WHITE = 8

class ColorPrinter:
  BLACK_TEXT = "\033[90m"
  RED_TEXT = "\033[91m"
  GREEN_TEXT = "\033[92m"
  YELLOW_TEXT = "\033[93m"
  BLUE_TEXT = "\033[94m"
  MAGENTA_TEXT = "\033[95m"
  CYAN_TEXT = "\033[96m"
  WHITE_TEXT = "\033[97m"
  RESET_TEXT = "\033[0m"

  @staticmethod
  def get_print_code(color):
    if color == Color.BLACK:
      return ColorPrinter.BLACK_TEXT
    if color == Color.RED:
      return ColorPrinter.RED_TEXT
    if color == Color.GREEN:
      return ColorPrinter.GREEN_TEXT
    if color == Color.YELLOW:
      return ColorPrinter.YELLOW_TEXT
    if color == Color.BLUE:
      return ColorPrinter.BLUE_TEXT
    if color == Color.MAGENTA:
      return ColorPrinter.MAGENTA_TEXT
    if color == Color.CYAN:
      return ColorPrinter.CYAN_TEXT
    if color == Color.WHITE:
      return ColorPrinter.WHITE_TEXT

  @staticmethod
  def cprint(color, text):
    print(f"{ColorPrinter.get_print_code(color)}{text}{ColorPrinter.RESET_TEXT}")
