from collections import Counter
from typing import List
import itertools

from helpers import Helpers
from player import Player

# This strategy decides based on the statistically best option
class Statistical(Player):
    def __init__(self, name):
        super().__init__(name)

    def calc_singles(self, field_idx: int, dices: List[int], num_rerolls: int):
        num_dice = len(dices)
        dice_val = field_idx + 1
        curr_occs = dices.count(dice_val)
        if curr_occs == num_dice:
            return [ tuple(1, num_dice * dice_val) ]
        res = []
        for occs in range(curr_occs + 1, num_dice + 1):
            goal_dice = list(itertools.repeat(dice_val, occs))
            diff = self.__diff_dice(dices, goal_dice)
            prob = self.__roll_prob(diff, num_rerolls)
            res.append(tuple(prob, occs * dice_val))
        return res

    def calc_pair(self, dices: List[int], num_rerolls: int):
        num_dice = len(dices)
        max_d = max(dices)
        res = []

        dupl = Helpers.find_highest_duplicate_dice(dices, 2)
        # calculate for the highest duplicate value
        if dupl != 0:
            diff = [ max_d ]
            diff += list(itertools.repeat(-1, num_dice - 2))
            prob = self.__roll_prob(diff, num_rerolls)
            res.append(tuple(dupl, dupl * 2))

        # calculate for the highest dice value
        if max_d != dupl:
            diff = [ max_d ]
            diff += list(itertools.repeat(-1, num_dice - 2))
            prob = self.__roll_prob(diff, num_rerolls)
            res.append(tuple(prob, max_d * 2))

        # calculate for the dice value 6
        if max_d != 6:
            diff = [6, 6] + list(itertools.repeat(-1, num_dice - 2))
            prob = self.__roll_prob(diff, num_rerolls)
            res.append(tuple(prob, 12))
        return res

    def calc_two_pair(self, dices: List[int], num_rerolls: int):
        pass

    def calc_three_oak(self, dices: List[int], num_rerolls: int):
        pass

    def calc_four_oak(self, dices: List[int], num_rerolls: int):
        pass

    def calc_small_straight(self, dices: List[int], num_rerolls: int):
        diff = self.__diff_dice(dices, [1, 2, 3, 4, 5])
        prob = self.__roll_prob(diff, num_rerolls)
        return [ tuple(prob, 15) ]

    def calc_large_straight(self, dices: List[int], num_rerolls: int):
        diff = self.__diff_dice(dices, [2, 3, 4, 5, 6])
        prob = self.__roll_prob(diff, num_rerolls)
        return [ tuple(prob, 20) ]

    def calc_full_house(self, dices: List[int], num_rerolls: int):
        pass

    def calc_chance(self, dices: List[int], num_rerolls: int):
        return [ tuple(1, sum(dices)) ]

    def calc_yatzy(self, dices: List[int], num_rerolls: int):
        max_occurances = max(Counter(dices).values())
        missing_for_yatzy = len(dices) - max_occurances
        diff = list(itertools.repeat(1, max_occurances))
        diff += list(itertools.repeat(-1, missing_for_yatzy))
        prob = self.__roll_prob(diff, num_rerolls)
        return [ tuple(prob, 50) ]

    # Calculates which of your current dice you would need to reroll
    # in order to get a set of goal dices.
    # Ex. curr_dice = [6, 6, 2, 3, 1], goal_dice = [6, 6, 6], res = [6, -1, -1]
    def __diff_dice(self, curr_dice: List[int], goal_dice: List[int]) -> List[int]:
        result = []
        curr_c = Counter(curr_dice)
        goal_c = Counter(goal_dice)
        
        for dice_val, count in goal_c.items():
            result += list(itertools.repeat(dice_val, count - curr_c[dice_val]))

        if result:
            for i in range(len(curr_dice) - len(goal_dice)):
                result.append(-1)

        return result

    # Returns probability of getting a set of dice with num_rerolls
    # Ex. [6, -1, -1]: "prob. of getting (at least) a six with 3 dice"
    def __roll_prob(self, dice: List[int], num_rerolls : int) -> float:
        pass

    # returns a list of tuples containing $probability of getting $score
    # [ (probability, score),  (probability-, score+), (probability--, score++) ]
    # Ex. for field 6 if you already have two sixes and two throws left:
    # [ (100%, 12), (67%, 18), (25%, 24) ]
    def get_probabilities(self, field_idx: int, dices: List[int], num_rerolls: int):
        if 0 <= field_idx <= 5:
            return self.calc_singles(field_idx, dices, num_rerolls)
        if field_idx == 6:
            return self.calc_pair(dices, num_rerolls)
        if field_idx == 7:
            return self.calc_two_pair(dices, num_rerolls)
        if field_idx == 8: # three of a kind
            pass
        if field_idx == 9: # four of a kind
            pass
        if field_idx == 10: # small straight
            pass
        if field_idx == 11: # large straight
            pass
        if field_idx == 12: # full house
            pass
        if field_idx == 13: # chance
            pass
        if field_idx == 14: # yatzy
            pass

    def decide_reroll(self, score_fields, dices, throw_num):
        # 1. For each available field in score_fields, calculate the probabilities
        # of getting each variation of that field with regards to the throw_num.
        # Store the probability together with its field score. Example:
        # "Getting another six while already having two sixes with 2 rerolls left = 67%"
        # alternatives = [(field_idx, score, prob), (field_idx, score, prob) ..., (field_idx, score, prob)]
        alternatives = []
        for field_idx in range(len(score_fields)):
            if Helpers.field_available(score_fields, field_idx):
                alternatives.append(self.get_probabilities(field_idx, dices, throw_num))
                
        # 2. Feed the numbers into the ScoreLogModel to get the expected game final 
        # score for each alternative. Example:
        # "Logging 3 sixes on field:sixes = 290 final score"
        for alternative in alternatives:
            alternative.append(self.decide_score_logging(score_fields, ))
 
        # 3. Now we have a series of probabilities of rewards. We can use the concept
        # of expected value to compare the alternatives. E(A) = P(A) * R(A)
        # E(A) = 67% * 290 = 194. Iterate over alternatives and maximize E(A).
        idxs_to_reroll = None
        
        self.logger.log_rerolls(self.name, dices, idxs_to_reroll, throw_num)
        return None

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
            if field_idx < 6 and points / (field_idx+1) >= 3:
                ea += ((field_idx+1) / 21) * 50
            ea = ea / max_score
            ra = ea / pa

            if ra > max_ra:
                max_ra = ra
                best_move = (field_idx, points)

        self.logger.log_scoring(self.name, dices, best_move[1], best_move[0])
        return best_move
