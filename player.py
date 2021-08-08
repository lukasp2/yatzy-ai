from collections import Counter
from random import randint
import numpy.ma as ma

# Defines a player in the game (a set of scores and actions to be performed on the scores)
class Player:
    def __init__(self, name, strategy):
        self.name = name
        self.strategy = strategy
        self.score_fields = ma.masked_array([ 0 for i in range(15) ], mask=False) # contains scores

    # returns a list of scoring options the player has given a certain set of dice.
    # the list contains tuples (field index, points), so (0, 3) means the player can
    # put 3 in the 'ones' field.
    def get_possible_moves(self, dice):

        # find highest value dice which occurs at least 'min_occurances' times
        def find_highest_duplicate_dice(dice, min_occurances):
            highest_dice = 0
            duplicates = [ k for k, v in Counter(dice).items() if v >= min_occurances ]
            if duplicates:
                highest_dice = max(duplicates)
            return highest_dice

        possible_moves = []

        for field_index in range(len(self.score_fields)):
            if self.score_fields.mask[field_index] == False:
                points = 0
                if 0 <= field_index <= 5: # singles
                    points = dice.count(field_index + 1) * (field_index + 1)
                if field_index == 6: # pair
                    points = find_highest_duplicate_dice(dice, 2) * 2
                if field_index == 7: # two pair
                    dup_1 = find_highest_duplicate_dice(dice, 2)
                    if dup_1:
                        dice_cpy = [ x for x in dice if x != dup_1 ]
                        dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                        if dup_2:
                            points = dup_1 * 2 + dup_2 * 2
                if field_index == 8: # three of a kind
                    points = find_highest_duplicate_dice(dice, 3) * 3
                if field_index == 9: # four of a kind
                    points = find_highest_duplicate_dice(dice, 4) * 4
                if field_index == 10: # small straigt
                    if dice == [1, 2, 3, 4, 5]:
                        points = 15
                if field_index == 11: # large straigt
                    if dice == [2, 3, 4, 5, 6]:
                        points = 20
                if field_index == 12: # full house
                    dup_1 = find_highest_duplicate_dice(dice, 3)
                    if dup_1:
                        dice_cpy = [ x for x in dice if x != dup_1 ]
                        dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                        if dup_2:
                            points = dup_1 * 3 + dup_2 * 2
                if field_index == 13: # chance
                    points = sum(dice)
                if field_index == 14: # yatzy
                    if dice.count(dice[0]) == 5:
                        points = 50
                
                possible_moves.append((field_index, points))

        return possible_moves

    def reset_board(self):
        self.score_fields = ma.masked_array([ 0 for i in range(15) ], mask=False)

    # returns which dice to throw
    def decide_dice_throw(self, throw_number, dice):
        return self.strategy.decide_dice_throw(self.score_fields, throw_number, dice)

    # returns which score field to fill with what value
    def decide_score_logging(self, dice):
        return self.strategy.decide_score_logging(dice, self.score_fields, self.get_possible_moves(dice))