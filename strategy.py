from random import randint

from models import DiceThrowModel
from models import ScoreLogModel

class Strategy:
    def __init__(self, strategy, load_models=False):
        self.strategy = strategy
        
        if strategy == 'model':
            self.diceModel = DiceThrowModel(load=load_models)
            self.scoreModel = ScoreLogModel(load=load_models)
    
    def decide_dice_throw(self, score_fields, available_fields, throw_number, dice):
        if self.strategy == 'random':
            # 1. randomize amount of dice, X, [0 <= X <= 5]
            amt_of_dice = randint(0,5) 

            # 2. return list of dice indexes to throw [0 .. X]
            return list(range(amt_of_dice)) 

        elif self.strategy == 'model':
            return self.diceModel.decide_dice_throw(score_fields, available_fields, throw_number, dice)
        
        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass

    def decide_score_logging(self, die, score_fields, available_fields, possible_moves):
        if self.strategy == 'random': 
            random_move = possible_moves[ randint(0, len(possible_moves) - 1) ]

            return random_move

        elif self.strategy == 'model':
            return self.scoreModel.decide_score_logging(die, score_fields, available_fields, possible_moves)

        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass
        