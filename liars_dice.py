import copy
import random
from typing import List

from utils.color_printer import ColorPrinter, Color
from player.player import Player
from game.round import Round
from player.strategy.strategy import Strategy


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
        """
        Returns a shuffled copy of self.players.
        """
        shuffled_list = copy.deepcopy(self.players)
        random.shuffle(shuffled_list)
        return shuffled_list

    def on_turn_detail(self, message: str):
        """
        This callback prints out every detail of each turn.
        You can add more logic here (e.g., save to a log file).
        """
        if self.verbose:
            print(message)

    def play_game(self):
        starting_player = 0
        current_players = self.shuffle_players()
        standings = []

        while len([p for p in current_players if p.is_alive]) > 1:
            self.round_number += 1
            if self.verbose:
                print(f"\n\n----- {ColorPrinter.BLUE_TEXT}Round {self.round_number}{ColorPrinter.RESET_TEXT} -----")

            # Create a Round object, passing in a callback that we can use to log turn details
            round_obj = Round(
                players=self.get_active_players(starting_player, current_players),
                verbose=self.verbose,
                turn_callback=self.on_turn_detail  # pass our printer callback
            )

            round_winner, round_loser = round_obj.play()

            # The Round returns (winner, loser); loser loses a die
            round_loser.num_dice -= 1
            if not round_loser.is_alive:
                current_players.remove(round_loser)
                standings.insert(0, round_loser)
                if self.verbose:
                    msg = f"{round_loser.name} has been eliminated."
                    ColorPrinter.cprint(Color.YELLOW, msg)

            # The next round starts with whoever won the last round
            starting_player = current_players.index(round_winner)

        # The last one standing is the final winner
        if len(current_players) != 1:
            ColorPrinter.cprint(Color.RED, "********* Unknown Error: Unable to determine winner! **********")
        else:
            # Insert the final winner at the front of standings
            standings.insert(0, current_players[0])
            # Update each player's stats with final placement
            for placing, player in enumerate(standings):
                player.stats.performance.append(placing)
                player.stats.dice_left.append(player.num_dice)

            if self.verbose:
                self.print_standings(standings)
            return standings

    def print_standings(self, standings):
        """
        Print final standings after the game ends.
        """
        print(f"\n\n---------- {ColorPrinter.CYAN_TEXT}Game Over!{ColorPrinter.RESET_TEXT} ----------")
        placement = 1
        for player in standings:
            if placement == 1:
                print(f"{ColorPrinter.GREEN_TEXT}Winner{ColorPrinter.RESET_TEXT}: {player.name} "
                      f"{ColorPrinter.BLACK_TEXT}({player.num_dice} dice remaining){ColorPrinter.RESET_TEXT}")
                print(player.stats)
            elif placement != len(standings):
                print(f"{placement}: {player.name}")
                print(player.stats)
            else:
                print(f"{ColorPrinter.RED_TEXT}{placement}{ColorPrinter.RESET_TEXT}: {player.name}")
                print(player.stats)
            placement += 1


if __name__ == "__main__":
    default_strategy = Strategy()
    # Create players
    players = [
        Player("Alice", default_strategy),
        Player("Bob", default_strategy),
        Player("Charlie", default_strategy),
        Player("Diana", default_strategy)
    ]
    game = LiarDiceGame(players, verbose=True)
    game.play_game()
