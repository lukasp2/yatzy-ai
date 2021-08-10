from random import randint

class Strategy:
    def __init__(self, strategy, rerollModel, scoreModel, load_models=False):
        self.strategy = strategy
        self.rerollModel = rerollModel
        self.scoreModel = scoreModel
        
        if load_models:
            rerollModel.load_model()
            scoreModel.load_model()
    
    def decide_dice_throw(self, score_fields, reroll_num, dice):
        if self.strategy == 'random':
            # 1. randomize amount of dice, X, [0 <= X <= 5]
            amt_of_dice = randint(0,5) 

            # 2. return list of dice indexes to throw [0 .. X]
            return list(range(amt_of_dice)) 

        elif self.strategy == 'model':
            return self.rerollModel.decide_reroll(score_fields, reroll_num, dice)
        
        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass

    def decide_score_logging(self, score_fields, possible_moves):
        if self.strategy == 'random': 
            top_moves = sorted(possible_moves, key=lambda item: item[1])[-3:]
            random_move = top_moves[ randint(0, len(top_moves) - 1) ]
            return random_move

        elif self.strategy == 'model':
            return self.scoreModel.decide_score_logging(score_fields, possible_moves)

        elif self.strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass
        