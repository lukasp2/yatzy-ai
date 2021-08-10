import numpy as np
import numpy.ma as ma

# Defines a player in the game (a set of scores and actions to be performed on the scores)
class Player:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.score_fields = ma.masked_array([ 0.0 for i in range(15) ], mask=False, dtype='float32')

    # returns which dice to throw
    def decide_reroll(self, die, reroll_num):
        return self.strategy.decide_reroll(die, reroll_num, self.score_fields)

    # returns which score field to fill with what value
    def decide_score_logging(self, game):
        possible_moves = game.get_possible_moves(self.score_fields)
        return self.strategy.decide_score_logging(self.score_fields, possible_moves)