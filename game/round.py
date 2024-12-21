import copy
from math import comb
from typing import List, Tuple

from utils.color_printer import *
from player.player import Player
from game.bid import Bid


class Round:
    """
    A single round of Liar's Dice.
    A round lasts from the first bid until a player is challenged.
    """
    def __init__(self, players: List[Player], verbose: bool, turn_callback=None):
        """
        :param players: The active players in turn order for this round.
        :param verbose: Whether to print minimal or no info. 
        :param turn_callback: A function that takes a string. Use it to log/print every turn detail.
        """
        self.players = players
        self.active_player_index = 0
        self.history = []  # list of (player_name, Bid)
        self.current_bid = None
        self.verbose = verbose
        self.turn_callback = turn_callback

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
        in a cyclic order of players, starting from the active player.
        """
        if self.active_player is None:
            return 0

        if self.active_player == player:
            return len(self.players) - 1

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
        p_match = 1 / 3  # Probability that a random die is either the face_value or 1

        prob = 0.0
        for k in range(needed, unknown_count + 1):
            prob += comb(unknown_count, k) * (p_match ** k) * ((1 - p_match) ** (unknown_count - k))
        return prob

    def resolve_call(self, all_dice, bidder, challenger, out_of_turn_call, probability) -> Tuple[Player, Player]:
        """
        Returns (winner, loser) of the call.
        """
        if self.verbose and self.turn_callback:
            self.turn_callback(
                f"{challenger.name} calls bluff"
                f"{' (out-of-turn)' if out_of_turn_call else ''}.\n"
                f"Probability (challenger perspective): {probability:.3f}\n"
            )

        bidder.stats.bids_called += 1
        challenger.stats.calls.append(probability)
        if out_of_turn_call:
            challenger.stats.calls_out_of_turn += 1

        matching_dice = self.count_matching_dice(all_dice, self.current_bid.face_value)
        loser = None
        winner = None

        if matching_dice >= self.current_bid.number_of_dice:
            # Bid is true
            winner = bidder
            loser = challenger
            bidder.stats.successful_bids += 1
            if self.verbose and self.turn_callback:
                self.turn_callback(
                    f"Bid is TRUE: {matching_dice} dice match needed {self.current_bid.number_of_dice}.\n"
                    f"{challenger.name} loses a die.\n"
                )
        else:
            # Bid is false
            winner = challenger
            loser = bidder
            challenger.stats.successful_calls += 1
            if self.verbose and self.turn_callback:
                self.turn_callback(
                    f"Bid is FALSE: {matching_dice} dice match needed {self.current_bid.number_of_dice}.\n"
                    f"{bidder.name} loses a die.\n"
                )

        return winner, loser

    def bid_is_valid(self, bid: Bid) -> bool:
        total_dice = sum(p.num_dice for p in self.players)
        # Must be strictly higher than current_bid and cannot exceed total dice
        return (bid.number_of_dice <= total_dice) and bid.is_higher_than(self.current_bid)

    def reset(self):
        self.current_bid = None
        self.history = []

    def play(self):
        """
        Executes the round from first bid until a call is resolved.
        Returns (winner, loser) for the round, so the game can update dice.
        """
        self.reset()
        if self.active_player is None or len(self.players) == 0 or self.active_player_index is None:
            return None, None

        # Roll dice
        dice_counts = []
        all_dice = []
        for p in self.players:
            p.roll_dice()
            dice_counts.append((p.name, len(p.dice)))
            all_dice.extend(p.dice)
            # Show the dice if verbose
            if self.verbose and self.turn_callback:
                self.turn_callback(f"{p.name}'s dice: {p.dice}")

        if self.verbose and self.turn_callback:
            self.turn_callback("--------- Round Start ---------\n")

        loser = None
        winner = None

        while loser is None:
            # --- ACTIVE PLAYER MAKES A BID ---
            # Before making the bid, let's compute the probability from the active player's perspective
            active_prob = self.compute_probability(self.active_player)

            # Print all parameters that will be passed to make_bid
            if self.verbose and self.turn_callback:
                self.turn_callback(
                    f"--- {self.active_player.name}'s TURN to BID ---\n"
                    f"Round History (copy): {copy.deepcopy(self.history)}\n"
                    f"Current Bid: {copy.deepcopy(self.current_bid)}\n"
                    f"Dice Counts: {dice_counts}\n"
                    f"Probability (active player's perspective): {active_prob:.3f}\n"
                    f"My Dice: {self.active_player.dice}\n"
                    f"Turns Until My Next Turn: {(len(self.players) - 1)}\n"
                )

            new_bid = self.active_player.strategy.make_bid(
                copy.deepcopy(self.history),
                copy.deepcopy(self.current_bid),
                copy.deepcopy(dice_counts),
                (len(self.players) - 1),
                copy.deepcopy(self.active_player.dice),
            )

            # If the new bid is invalid, interpret that as calling the last bid
            if not self.bid_is_valid(new_bid):
                prev_player = self.players[self.prev_player_index(self.active_player_index)]
                if self.verbose and self.turn_callback:
                    self.turn_callback(
                        f"{self.active_player.name} tried an INVALID bid {new_bid}. "
                        f"Forcing a call on {prev_player.name}'s bid.\n"
                    )
                winner, loser = self.resolve_call(
                    all_dice, 
                    prev_player, 
                    self.active_player, 
                    out_of_turn_call=False,
                    probability=active_prob  # Probability from active player's perspective
                )
                break

            # Otherwise, a valid bid is placed
            self.history.append((self.active_player.name, new_bid))
            self.current_bid = new_bid
            self.active_player.stats.bids += 1

            if self.verbose and self.turn_callback:
                self.turn_callback(f"{self.active_player.name} BIDS {new_bid}.\n")

            # --- ASK OTHER PLAYERS IF THEY WANT TO CALL ---
            player_to_call_index = self.next_player_index(self.active_player_index)
            for n in range(0, len(self.players) - 1):
                player_to_call = self.players[player_to_call_index]
                out_of_turn = (n > 0)  # first check is in-turn for next player, subsequent are out-of-turn
                probability = self.compute_probability(player_to_call)

                # Print all parameters we are about to pass to the challenger's strategy
                if self.verbose and self.turn_callback:
                    self.turn_callback(
                        f"--- {player_to_call.name}'s CHANCE to CALL ---\n"
                        f"Round History (copy): {copy.deepcopy(self.history)}\n"
                        f"Current Bid: {copy.deepcopy(self.current_bid)}\n"
                        f"Dice Counts: {dice_counts}\n"
                        f"Probability (their perspective): {probability:.3f}\n"
                        f"My Dice: {player_to_call.dice}\n"
                        f"Out-of-turn? {out_of_turn}\n"
                        f"Turns Until My Turn: {self.turns_until_player_turn(player_to_call)}\n"
                    )

                do_call = player_to_call.strategy.challenge_bid(
                    copy.deepcopy(self.history),
                    copy.deepcopy(self.current_bid),
                    copy.deepcopy(dice_counts),
                    probability,
                    self.turns_until_player_turn(player_to_call),
                    copy.deepcopy(player_to_call.dice),
                    out_of_turn
                )

                if do_call:
                    winner, loser = self.resolve_call(all_dice, self.active_player, player_to_call, out_of_turn, probability)
                    break

                player_to_call_index = self.next_player_index(player_to_call_index)

            if loser is not None:
                break

            # No one called; move active player to next
            self.active_player_index = self.next_player_index(self.active_player_index)

        # Return (winner, loser) so the game can handle dice removal
        return winner, loser
