from random import randint

class Strategy:
    def __init__(self, strategy, diceModel, scoreModel, load_models=False):
        self.strategy = strategy
        self.diceModel = diceModel
        self.scoreModel = scoreModel
        
        if load_models:
            diceModel.load_model()
            scoreModel.load_model()
    
    def decide_dice_throw(self, score_fields, throw_number, dice):
        if self.strategy == 'random':
            # 1. randomize amount of dice, X, [0 <= X <= 5]
            amt_of_dice = randint(0,5) 

            # 2. return list of dice indexes to throw [0 .. X]
            return list(range(amt_of_dice)) 

        elif self.strategy == 'model':
            return self.diceModel.decide_dice_throw(score_fields, throw_number, dice)
        
        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass

    def decide_score_logging(self, score_fields, possible_moves):
        if self.strategy == 'random': 
            random_move = possible_moves[ randint(0, len(possible_moves) - 1) ]

            return random_move

        elif self.strategy == 'model':
            return self.scoreModel.decide_score_logging(score_fields, possible_moves)

        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass
        