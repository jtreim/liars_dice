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
All you should need to do is extend the base [Strategy](https://github.com/jtreim/liars_dice/blob/main/strategy.py) class. During the course of play your strategy will be called upon to decide whether to bid, or call a previous bid. The two methods you'll be overriding:

`challenge_bid`: Does the strategy suggest challenging the current bid?
Return `True` if so, `False` otherwise.
Params:
- `round_history`: The list of bids that were made, paired with the name of the player that made them.
- `current_bid`: The bid to consider calling. (See the [Bid](https://github.com/jtreim/liars_dice/blob/main/bid.py) for more info).
- `dice_counts`: The number of dice each player has.
- `probability_of_truth`: The likelihood that the `current_bid` is valid. This is taken using the dice the current player has, and the total number of dice left in the game.
- `turns_until_my_turn`: How many other players need to play until it is your turn to bid. If you are next after the current bidder, this will always be (1 - the number of players left in the game).
- `my_dice`: The face values that you rolled.
- `out_of_turn`: whether calling the current bid would be out of turn order.

`make_bid`: What bid does the strategy recommend making?
Return a valid `Bid`.
Params:
- `round_history`: The list of bids that were made, paired with the name of the player that made them.
- `current_bid`: The last bid that was made. (See the [Bid](https://github.com/jtreim/liars_dice/blob/main/bid.py) for more info).
- `dice_counts`: The number of dice each player has.
- `turns_until_my_turn`: How many other players need to play until it is your turn to bid. If you are next after the current bidder, this will always be (1 - the number of players left in the game).
- - `my_dice`: The face values that you rolled.

If you want other inputs for your strategy to consider on bidding/calling, talk with me and we'll see what we can do.
