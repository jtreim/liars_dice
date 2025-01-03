# Liar's Dice
A python implementation of Liar's Dice. Players can create strategies to try out against each other!

### Rules
There are some slight differences to playing Liar's Dice IRL. Each player starts with 5 dice, and the game is played in rounds until only one player has dice left.
A round consists of the following:
- Players roll all their dice.
- The current player makes a bid. A valid bid means increasing the number of dice required, increasing the pip count, or both. If a bid increases the number of dice required, the pip count must be the same or greater. If the bid is deemed invalid, the player is forced to call the previous bid. If this occurs on the very first bid, then the player automatically loses a die and play moves on to the next player. As 1's are considered wilds, bids on 1's are not allowed.
- After a valid bid is made, each player is asked in turn order whether they would like to call the bid. If a bid is called, all the dice are counted. If the number of 1's + the number of matching die faces is greater than or equal to the bid that was made, the caller loses a die. Otherwise, the bidder loses a die. This allows for bids out of play, but it does not consider letting players wait for others to call a bid. Each player is only given one chance to call a bid before the next bid is made.
- The round lasts until a player loses a die.

### Okay cool, but what do I do exactly?
All you should need to do is extend the base [Strategy](https://github.com/jtreim/liars_dice/blob/main/player/strategy/strategy.py) class. During the course of play your strategy will be called upon to decide whether to bid, or call a previous bid. The two methods you'll be overriding:

`challenge_bid`: Does the strategy suggest challenging the current bid?
Return `True` if so, `False` otherwise.
Params:
- `round_history`: The list of [Bid](https://github.com/jtreim/liars_dice/blob/main/game/bid.py)s that were made, paired with the name of the player that made them.
- `current_bid`: The bid to consider calling. (See the [Bid](https://github.com/jtreim/liars_dice/blob/main/game/bid.py) class for more info).
- `dice_counts`: The number of dice each player has.
- `probability_of_truth`: The likelihood that the `current_bid` is valid. This is taken using the dice the current player has, and the total number of dice left in the game.
- `turns_until_my_turn`: How many other players need to play until it is your turn to bid. If you are next after the current bidder, this will always be (1 - the number of players left in the game).
- `my_dice`: The face values that you rolled.
- `out_of_turn`: whether calling the current bid would be out of turn order.

`make_bid`: What bid does the strategy recommend making?
Return a valid `Bid`.
Params:
- `round_history`: The list of [Bid](https://github.com/jtreim/liars_dice/blob/main/game/bid.py)s that were made, paired with the name of the player that made them.
- `current_bid`: The last bid that was made. (See the [Bid](https://github.com/jtreim/liars_dice/blob/main/game/bid.py) class for more info).
- `dice_counts`: The number of dice each player has.
- `turns_until_my_turn`: How many other players need to play until it is your turn to bid. If you are the current bidder, this will always be (1 - the number of players left in the game).
- `my_dice`: The face values that you rolled.

#### If you want to prep for the start of each round...

`prepare_for_new_round`: Setup called before a round starts.
Params:
- `dice_counts`: The list of tuples containing the player name and their dice count for the round. This list is organized in the turn order.
- `my_dice`: The face values that you rolled.

If you want other parameters for your strategy on a method, or want to add a method to call, talk with me and we'll see what we can do.

### Testing my strategy
There is a real dumb strategy that you can test against. All it does is increase the bid, and if a bid seems less than 40% likely, the bid gets called. If you want to test your strategy against it, update the [Tournament](https://github.com/jtreim/liars_dice/blob/main/tournament.py) class, and add your strategy to it. For example, import your strategy at the top of the file:

`from player.strategy import strategy, bad_strategy`

and at the bottom add:
```
if __name__ == "__main__":
  default_strategy = strategy.Strategy()

  # Your strategy here
  bs = bad_strategy.BadStrategy()


  # Create players
  players = [
    Player("Alice", default_strategy),
    Player("Bob", default_strategy),
    Player("Charlie", default_strategy),
    Player("Diana", default_strategy),
    Player("Me", bs) # don't forget to use your strategy
  ]

  tournament = Tournament(players)
  # if you want to increase the number of games to run, you can pass that in here.
  # tournament = Tournament(players, 50)

  tournament.run()
```

then it's just running:

`python tournament.py`
