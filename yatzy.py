from random import randint

from history import History

# Defines a game of Yatzy
class Yatzy:
    def __init__(self, players):
        self.players = players
        self.die = [1, 1, 1, 1, 1]
        self.history = History()

    # plays the game
    def play(self):
        for player in self.players:
            player.reset_board()

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
        player.score_fields[index] = score
        player.score_fields.mask[index] = True
        
    # randomizes the values in the self.die on the indexes indicated by the input array.
    def throw_dice(self, dice_idx_to_throw):
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

    # translates a field index into the name of that field
    def idx_to_name(self, field_index):
        return ['aces', 'twos', 'threes', 'fours', 'fives', 
                'sixes', 'pair', 'two pair', 'three of a kind', 
                'four of a kind', 'small straight', 'large straight', 
                'full house', 'chance', 'yatzy'][field_index]

    def max_points(self, field_index):
        return [5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50][field_index]