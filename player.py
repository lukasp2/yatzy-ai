import numpy.ma as ma
from random import randint
from history import History
from helpers import Helpers
import abc
from logger import Logger

class Player:
    @abc.abstractmethod
    def __init__(self, name):
        self.name = name
        self.score_fields = ma.masked_array([ 0 for i in range(15) ], mask=False, dtype='float32')
        self.history = History()
        self.game_scores = []
        #self.high_score = 0
        #self.num_games = 0
        #self.avg_score = 0
        self.log_msg = ""
        self.logger = None

    def set_config(self, config):
        self.config = config
        self.scoreLogModel = config['models']['scoreLogModel']['class']
        self.rerollModel = config['models']['rerollModel']['class']
        self.logger = Logger(config['verbosity'])

    def play(self, die):
        self.history.game.initiate_play(self.score_fields)
        self.__throw_dice(die, [ 0, 1, 2, 3, 4 ])

        for throw_num in range(1, 3):
            dice_idxs_to_throw = self.decide_reroll(self.score_fields, die, throw_num)
            reroll = ma.masked_array(die, mask=[ 1 if i in dice_idxs_to_throw else 0 for i in range(len(die))] )
            self.history.game.play.add_reroll(reroll)

            self.__throw_dice(die, dice_idxs_to_throw)

        field_index, score = self.decide_score_logging(self.score_fields, die)
        self.__set_score_field(field_index, score)
        self.history.game.play.add_scoring(field_index, score)
        self.history.game.commit_play()

    # game preparations
    def prepare(self):
        self.score_fields = ma.masked_array([ 0 for i in range(15) ], mask=False, dtype='float32')
        self.history.clear_history()
        self.history.initiate_game()

    # game finishing touches 
    def finish(self):
        score = self.count_points()
        self.history.commit_game(score)
        self.game_scores.append(score)

        #self.avg_score = ((self.num_games * self.avg_score) + score) / (self.num_games + 1)
        #self.num_games += 1
        #if self.high_score < score:
        #    self.high_score = score

        if self.config['models']['scoreLogModel']['save']:
            self.scoreLogModel.train(self.history)
        if self.config['models']['rerollModel']['save']:
            self.rerollModel.train(self.history)

    def __throw_dice(self, die, dice_idxs_to_throw):
        for index in dice_idxs_to_throw:
            die[index] = randint(1,6)

    def __set_score_field(self, idx, score):
        self.score_fields.data[idx] = float(score)
        self.score_fields.mask[idx] = True

    def count_bonus_points(self):
        return sum(self.score_fields.data[0:6])

    def get_bonus(self):
        return 50 if self.count_bonus_points() >= 63 else 0

    def count_points(self):
        return sum(self.score_fields.data) + self.get_bonus()

    @abc.abstractmethod
    def decide_reroll(self, score_fields, die, throw_num) -> list:
        pass

    @abc.abstractmethod
    def decide_score_logging(self, score_fields, die) -> int:
        pass

    @abc.abstractmethod
    def get_name(self):
        return self.__class__.__name__.lower()

    # PRINTS
    def print_rerolls(self, dices, dice_idxs_to_reroll, throw_num):
        if throw_num == 1:
            self.log_msg = "\tdices:\t\t\t"
        self.log_msg += '[' + ', '.join([ str(dices[idx]) + 'r' if idx in dice_idxs_to_reroll else str(dices[idx]) for idx in range(len(dices)) ]) + '] -> '

    def print_score_log(self, dices, score, field_idx):
        self.log_msg += str(list(dices)) + '\n'
        self.logger.log(self.log_msg, 2)
        self.logger.log('\t' + self.name + ' put ' + str(score) + ' points on ' + Helpers.idx_to_name(field_idx) + '\n', 2)
        self.logger.log('\n', 2)
