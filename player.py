import numpy.ma as ma

# Defines a player in the game (a set of scores and actions to be performed on the scores)
class Player:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.score_fields = ma.masked_array([ 0.0 for i in range(15) ], mask=False, dtype='float32')

    # returns which dice to throw
    def decide_reroll(self, die):
        return self.strategy.decide_reroll(self.score_fields, die)

    # returns which score field to fill with what value
    def decide_score_logging(self, die):
        return self.strategy.decide_score_logging(self.score_fields, die)