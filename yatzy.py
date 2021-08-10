from random import randint
import numpy.ma as ma
import numpy as np
from collections import Counter

from history import History

# Defines a game of Yatzy
class Yatzy:
    def __init__(self, players):
        self.players = players
        self.die = np.array([1, 1, 1, 1, 1])
        self.history = History()

    # plays the game
    def play(self):
        self.reset_boards()

        print('YATZY!')
        for round in range(1, 16):
            print("\tROUND", round)
            for player in self.players:
                self.throw_dice([ 0, 1, 2, 3, 4 ])
                print("\t\tthrow 1", self.die)
                for throw_number in range(1, 3):
                    decision = player.decide_dice_throw(throw_number, self.die)
                    self.throw_dice(decision)
                    print("\t\tthrow", throw_number, self.die)

                field_index, score = player.decide_score_logging(self.die)
                print("\t\tput", score, "points on", self.idx_to_name(field_index))
                self.set_score_field(player, field_index, score)
        
        self.print_score_board()

    # returns a list of scoring options the player has given a certain set of dice.
    # the list contains tuples (field index, points), so (0, 3) means the player can
    # put 3 in the 'ones' field.
    def get_possible_moves(self, score_fields):

        # find highest value dice which occurs at least 'min_occurances' times
        def find_highest_duplicate_dice(die, min_occurances):
            highest_dice = 0
            duplicates = [ k for k, v in Counter(die).items() if v >= min_occurances ]
            if duplicates:
                highest_dice = max(duplicates)
            return highest_dice

        possible_moves = []

        for field_index in range(len(score_fields)):
            if score_fields.mask[field_index] == False:
                points = 0
                if 0 <= field_index <= 5: # singles
                    points = np.count_nonzero(self.die == field_index + 1, axis=0) * (field_index + 1)
                if field_index == 6: # pair
                    points = find_highest_duplicate_dice(self.die, 2) * 2
                if field_index == 7: # two pair
                    dup_1 = find_highest_duplicate_dice(self.die, 2)
                    if dup_1:
                        dice_cpy = [ x for x in self.die if x != dup_1 ]
                        dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                        if dup_2:
                            points = dup_1 * 2 + dup_2 * 2
                if field_index == 8: # three of a kind
                    points = find_highest_duplicate_dice(self.die, 3) * 3
                if field_index == 9: # four of a kind
                    points = find_highest_duplicate_dice(self.die, 4) * 4
                if field_index == 10: # small straigt
                    if np.all(self.die == np.array([1, 2, 3, 4, 5])):
                        points = 15
                if field_index == 11: # large straigt
                    if np.all(self.die == np.array([2, 3, 4, 5, 6])):
                        points = 20
                if field_index == 12: # full house
                    dup_1 = find_highest_duplicate_dice(self.die, 3)
                    if dup_1:
                        dice_cpy = [ x for x in self.die if x != dup_1 ]
                        dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                        if dup_2:
                            points = dup_1 * 3 + dup_2 * 2
                if field_index == 13: # chance
                    points = sum(self.die)
                if field_index == 14: # yatzy
                    if np.all(self.die == self.die[0]):
                        points = 50
                
                possible_moves.append((field_index, points))

        return possible_moves

    # counts the points for the bonus
    def count_bonus_points(self, player):
        return sum(player.score_fields[0:6])

    # returns 50 if the player fulfilled requirements for the bonus
    def get_bonus(self, player):
        return 50 if self.count_bonus_points(player) >= 63 else 0

    # counts the players total score
    def count_points(self, player):
        return sum(player.score_fields.data) + self.get_bonus(player)

    # logs result
    def set_score_field(self, player, index, score):
        player.score_fields.data[index] = float(score)
        player.score_fields.mask[index] = True
        
    # randomizes the values in the self.die on the indexes indicated by the input array.
    def throw_die(self, dice_idx_to_throw):
        for index in dice_idx_to_throw:
            self.die[index] = randint(1,6)

    # prints current state of all players scores
    def print_score_board_2(self):
        print('PLAYER\t\t\t', ''.join([player.name + '\t' for player in self.players]))
        for i in range(14):
            tabs = '\t\t' if 7 <= i <= 12 else '\t\t\t'
            print(self.idx_to_name(i) + tabs, ''.join([str(player.score_fields[i]) + '\t' for player in self.players]))
            if i == 5:
                print('SUM\t\t\t', ''.join([str(self.count_bonus_points(player)) + '\t' for player in self.players]))
                print('BONUS\t\t\t', ''.join([str(self.get_bonus(player)) + '\t' for player in self.players]))
        print('TOTAL\t\t\t', ''.join([str(self.count_points(player)) + '\t' for player in self.players]))        

    # prints current state of one players scores
    def print_score_board(self):
        data = self.history.get_score_board()
        data['plays'].sort(key=lambda item : item['field_index'])

        n = 36
        _str = ''
        _str += ('='*n + ' Score Board ' + '='*n +'\n')
        _str += ('{:16}: {:5} | round - dice (r = reroll)\n'.format('Category', 'Score'))
        _str += ('-'*(2*n + 13) +'\n')

        for ii in range(13):
            play = data['plays'][ii]
            if ii == 6:
                _str += ('-'*(2*n+13) +'\n')
                upper_sum = sum(data['plays'][:6]['score'])
                _str += '{:16}: {:5} |\n'.format('Upper Sum', str(upper_sum))
                _str += '{:16}: {:5} |\n'.format('Bonus', '50' if upper_sum >= 63 else '--')
                _str += ('-'*(2*n+13) +'\n')
                
            score = '--' if play.score == 0 else str(play.score)
            line = '{:16}: {:5} | {:>5} - '.format(self.idx_to_name(ii), score, str(play['round']))
            
            for die_set in data['play']['dice_throws'][:2]:
                line += '{:} -> '.format(''.join(map(str, die_set)))
            line += ''.join(map(str, data['play']['dice_throws'][2]))
            _str += (line +'\n')

        _str += ('='*(2*n+13) +'\n')
        _str += (' '*(n+0) + ' Score: {:5d}\n'.format(data['final_score']))
        _str += ('='*(2*n+13) +'\n')
        return _str

    def reset_boards(self):
        for player in self.players:
            player.score_fields = ma.masked_array([ 0 for i in range(15) ], mask=False)

    # translates a field index into the name of that field
    def idx_to_name(self, field_index):
        return ['aces', 'twos', 'threes', 'fours', 'fives', 
                'sixes', 'pair', 'two pair', 'three of a kind', 
                'four of a kind', 'small straight', 'large straight', 
                'full house', 'chance', 'yatzy'][field_index]
