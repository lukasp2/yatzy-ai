from player import Player
from helpers import Helpers

from random import randint
import random
import math 

class Random(Player):
    def __init__(self, name):
        super().__init__(name)
        self.val_1 = 0
        self.val_2 = 0

    def biased_random_index(self, dices_set):
        n = len(dices_set)
        if n == 0:
            return None
        if n == 1:
            return 0
        weights = [math.exp(i / n) for i in range(n)]
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        return random.choices(range(n), weights=weights)[0]

    def decide_reroll_old(self, score_fields, dices, throw_num):
        # randomize number between 1-5
        minimum = 1
        if (score_fields.data[0] != 0 and score_fields.data[1] != 0):
            # ... or 3-5 if 1's and 2's are already logged as score.
            minimum = 3
        rnd_dice_threshhold = randint(minimum-1,5)

        # pick all dice values below that randomized number and reroll them
        dice_idxs_to_reroll = [] 
        for i in range(len(dices)):
            if dices[i] < rnd_dice_threshhold:
                dice_idxs_to_reroll.append(i)

        self.logger.log_rerolls(self.name, dices, dice_idxs_to_reroll, throw_num)
        return dice_idxs_to_reroll

    def decide_reroll(self, score_fields, dices, throw_num):
        dices_set = sorted(list(set(dices)))

        if throw_num == 1:
            rand_idx_1 = self.biased_random_index(dices_set) #randint(0, len(dices_set) - 1)
            self.val_1 = dices_set[rand_idx_1]

            # 10% of the time, keep two values
            self.val_2 = -1
            keep_two_values = randint(0,10) > 9 and len(dices_set) > 1
            if keep_two_values:
                rand_idx_2 = (rand_idx_1 - 1) if rand_idx_1 > 0 else (rand_idx_1 + 1)
                self.val_2 = dices_set[rand_idx_2]

        idxs_to_reroll = []
        for i in range(len(dices)):
            if dices[i] != self.val_1 and dices[i] != self.val_2:
                idxs_to_reroll.append(i)

        self.logger.log_rerolls(self.name, dices, idxs_to_reroll, throw_num)
        return idxs_to_reroll

    def decide_score_logging_old(self, score_fields, dices):
        normalized_moves = [ (move[0], move[1] / Helpers.max_scores[move[0]]) for move in Helpers.get_possible_moves(dices, score_fields) ]
        top_moves = sorted(normalized_moves, key=lambda item: item[1])[-2:]
        field_idx = top_moves[ randint(0, len(top_moves) - 1) ][0]
        score = Helpers.count_score(dices, field_idx)
        return field_idx, score

    def decide_score_logging(self, score_fields, dices):
        # stores the probabilities of rolling all yatzy dice combinations
        field_probabilites = [ 0.0322, 0.0322, 0.0322, 0.0322, 0.0322, 0.0322,
                              15/72, # pair
                              5/72, # two pair
                              0.2516, # 3 oak
                              5 * (6/6) * (1/6) * (1/6) * (1/6), # 4 oak
                              (5/6) * (4/6) * (3/6) * (2/6) * (1/6), # s straight
                              (5/6) * (4/6) * (3/6) * (2/6) * (1/6), # l straight
                              25/324, # full house
                              1, # chance
                              6/6**5, # yatzy
                              ]

        max_ra = -1
        best_move = None
        for field_idx, points in Helpers.get_possible_moves(dices, score_fields):
            # Maximize reward, R(A), by dividing value (normalized), E(A), 
            # by probability, P(A). R(A) = E(A) / P(A)
            pa = field_probabilites[field_idx]
            ea = points 
            max_score = Helpers.max_scores[field_idx]
            if field_idx < 6 and points / (field_idx+1) < 3:
                ea = 0
            if field_idx < 6 and points / (field_idx+1) >= 3:
                ea += ((field_idx+1) / 21) * 50
                max_score -= (field_idx+1) * 2
            ea = ea / max_score
            ra = ea / pa

            if ra > max_ra:
                max_ra = ra
                best_move = (field_idx, points)

        self.logger.log_scoring(self.name, dices, best_move[1], best_move[0])
        return best_move
