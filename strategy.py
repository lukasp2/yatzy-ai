from collections import Counter
from random import randint
from yatzy import Helpers
import numpy as np

class Strategy:
    def __init__(self, reroll_strategy, score_strategy, rerollModel, scoreModel, load_models=False):
        self.reroll_strategy = reroll_strategy
        self.score_strategy = score_strategy
        self.rerollModel = rerollModel
        self.scoreModel = scoreModel
        
        if load_models:
            rerollModel.load_model()
            scoreModel.load_model()

    def decide_reroll(self, score_fields, die):
        if self.reroll_strategy == 'random':
            # 1. randomize amount of dice, X, [0 <= X <= 5]
            amt_of_dice = randint(0,5) 

            # 2. return list of dice indexes to throw [0 .. X]
            return list(range(amt_of_dice)) 

        elif self.reroll_strategy == 'model':
            return self.rerollModel.decide_reroll(score_fields, die)
        
        elif self.reroll_strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.reroll_strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass

    def decide_score_logging(self, score_fields, die):
        if self.score_strategy == 'random':
            max_scores = np.array([3, 6, 9, 12, 15, 18, 12, 22, 18, 24, 15, 20, 28, 30, 50])
            normalized_moves = [ (move[0], move[1] / max_scores[move[0]]) for move in Helpers().get_possible_moves(die, score_fields) ]
            top_moves = sorted(normalized_moves, key=lambda item: item[1])[-2:]
            random_norm_move = top_moves[ randint(0, len(top_moves) - 1) ]
            random_move = [ random_norm_move[0], int(random_norm_move[1] * max_scores[random_norm_move[0]]) ]
            return random_move

        elif self.score_strategy == 'model':
            return self.scoreModel.decide_score_logging(score_fields, die)

        elif self.score_strategy == 'human':
            # TODO: this strategy lets you give the input
            pass

        elif self.score_strategy == 'statistical':
            # TODO: this strategy decides based on the statistically best option
            pass
        