from collections import Counter
import numpy as np
import numpy.ma as ma

# This class is like a guy watching the game and you can ask him whats going on
class Helpers:
    max_score = 374
    max_scores = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50])

    def __init__(self):
        pass

    # translates a field index into the name of that field
    @staticmethod
    def idx_to_name(field_idx):
        return ['aces', 'twos', 'threes', 'fours', 'fives', 
                'sixes', 'pair', 'two pair', 'three of a kind', 
                'four of a kind', 'small straight', 'large straight', 
                'full house', 'chance', 'yatzy'][field_idx]

    @staticmethod
    def find_highest_duplicate_dice(die, min_occurances):
            duplicates = [ k for k, v in Counter(die).items() if v >= min_occurances ]
            return max(duplicates) if duplicates else 0

    # given a set of die and a field index, counts the score it would give
    @staticmethod
    def count_score(die, field_index):
        points = 0
        if 0 <= field_index <= 5: # singles
            points = np.count_nonzero(die == field_index + 1, axis=0) * (field_index + 1)
        if field_index == 6: # pair
            points = Helpers.find_highest_duplicate_dice(die, 2) * 2
        if field_index == 7: # two pair
            dup_1 = Helpers.find_highest_duplicate_dice(die, 2)
            if dup_1:
                dice_cpy = ma.masked_array([ x for x in die if x != dup_1 ])
                dup_2 = Helpers.find_highest_duplicate_dice(dice_cpy, 2)
                if dup_2:
                    points = dup_1 * 2 + dup_2 * 2
        if field_index == 8: # three of a kind
            points = Helpers.find_highest_duplicate_dice(die, 3) * 3
        if field_index == 9: # four of a kind
            points = Helpers.find_highest_duplicate_dice(die, 4) * 4
        if field_index == 10: # small straigt
            if np.all(sorted(die) == np.array([1, 2, 3, 4, 5])):
                points = 15
        if field_index == 11: # large straigt
            if np.all(sorted(die) == np.array([2, 3, 4, 5, 6])):
                points = 20
        if field_index == 12: # full house
            dup_1 = Helpers.find_highest_duplicate_dice(die, 3)
            if dup_1:
                dice_cpy = ma.masked_array([ x for x in die if x != dup_1 ])
                dup_2 = Helpers.find_highest_duplicate_dice(dice_cpy, 2)
                if dup_2:
                    points = dup_1 * 3 + dup_2 * 2
        if field_index == 13: # chance
            points = sum(die)
        if field_index == 14: # yatzy
            if np.all(die == die[0]):
                points = 50
        return points
    
    # given a set of die and a field index to log the score in, returns the indexes
    # of the die to use for that play
    def get_die_idx_for_play(self, die, field_index):
        if 0 <= field_index <= 5:
            ret = [ index for index in range(len(die)) if die[index] != field_index + 1 ]
        elif field_index == 6: # pair
            ret = [ index for index in range(len(die)) if die[index] != self.find_highest_duplicate_dice(die, 2) ] 
        elif field_index == 7: # two pair
            dup_1 = self.find_highest_duplicate_dice(die, 2)
            dice_cpy = [ x if x != dup_1 else 0 for x in die ]
            dup_2 = self.find_highest_duplicate_dice(dice_cpy, 2)
            ret = [ i for i in range(len(die)) if die[i] != dup_1 and die[i] != dup_2 ]
        elif field_index == 8: # three of a kind
            ret = [ index for index in range(len(die)) if die[index] != self.find_highest_duplicate_dice(die, 3) ] 
        elif field_index == 9: # four of a kind
            ret = [ index for index in range(len(die)) if die[index] != self.find_highest_duplicate_dice(die, 4) ] 
        elif 10 <= field_index <= 14: # small-, large straight, yatzy, full house, chance
            ret = []
        return list(set(ret))

    # returns a list of scoring options the player has given a certain set of dice.
    # the list contains tuples (field index, points), so (0, 3) means the player can
    # put 3 in the 'ones' field.
    @staticmethod
    def get_possible_moves(dices, score_fields):
        possible_moves = []
        for field_index in range(len(score_fields)):
            if Helpers.field_available(score_fields, field_index):
                points = Helpers.count_score(dices, field_index)
                possible_moves.append((field_index, points))

        return possible_moves
    
    @staticmethod
    def bonus_reached(score_card):
        return sum(score_card.data[0:6]) >= 63
    
    @staticmethod
    def field_available(score_card, field_idx):
        return score_card.mask[field_idx] == False and score_card.data[field_idx] == 0