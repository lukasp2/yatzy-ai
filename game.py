from random import randint

# Defines a game of Yatzy
class Yatzy:
    def __init__(self, players):
        self.players = players
        self.die = [1, 1, 1, 1, 1]
        
    # for one player only: plays N games and returns player average
    def playN(self, N, verbose=False):
        total_score = 0
        for i in range(N):
            self.play(verbose, i, N)
            total_score += self.count_points(self.players[0])
        return total_score / N

    # plays the game
    def play(self, verbose=False, play_count = 1, tot_plays = 1):
        for player in self.players:
            player.reset_board()

        print('GAME', play_count, '/', tot_plays)
        for round in range(1, 16):
            print("\tROUND", round)
            for player in self.players:
                self.throw_dice([ 0, 1, 2, 3, 4 ])
                print("\t\tthrow 1", self.dice)
                for throw_number in range(2, 4):
                    decision = player.decide_dice_throw(throw_number, self.dice)
                    self.throw_dice(decision)
                    print("\t\tthrow", throw_number, self.dice)

                field_index, score = player.decide_score_logging(self.dice)
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
        return sum(player.score_fields) + self.get_bonus(player)

    # logs result
    def set_score_field(self, player, index, score):
        player.score_fields[index] = score
        player.available_fields[index] = 0
        
    # randomizes the values in the self.dice on the indexes indicated by the input array.
    def throw_dice(self, dice_idx_to_throw):
        for index in dice_idx_to_throw:
            self.die[index] = randint(1,6)

    # prints current set of die
    def print_dice(self):
        print(' '.join(self.dice))

    # prints current state of all players scores
    def print_score_board(self):
        print('PLAYER\t\t\t', ''.join([player.name + '\t' for player in self.players]))
        for i in range(14):
            tabs = '\t\t' if 7 <= i <= 12 else '\t\t\t'
            print(self.idx_to_name(i) + tabs, ''.join([str(player.score_fields[i]) + '\t' for player in self.players]))
            if i == 5:
                print('SUM\t\t\t', ''.join([str(self.count_bonus_points(player)) + '\t' for player in self.players]))
                print('BONUS\t\t\t', ''.join([str(self.get_bonus(player)) + '\t' for player in self.players]))
        print('TOTAL\t\t\t', ''.join([str(self.count_points(player)) + '\t' for player in self.players]))        

    # translates a field index into the name of that field
    def idx_to_name(self, field_index):
        return ['ones', 'twos', 'threes', 'fours', 'fives', 
                'sixes', 'pair', 'two pair', 'three of a kind', 
                'four of a kind', 'small straight', 'large straight', 
                'full house', 'chance', 'yatzy'][field_index]
