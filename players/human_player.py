from collections import Counter

from helpers import Helpers
from player import Player
from logger import Logger

# This strategy lets you give the input
class Human(Player):
    def __init__(self, name):
        super().__init__(name)

    def print_score_card_with_options(self, score_card, dices=[]):
        yellow = '\x1b[33m'
        white = '\x1b[37m'

        for field_idx in range(len(score_card)):
            field_name = Helpers.idx_to_name(field_idx)
            tabs = '\t' if 8 <= field_idx <= 11 else '\t\t'

            logged_score = score_card.data[field_idx]
            potential_score = Helpers.count_score(dices, field_idx)
            field_crossed = score_card.mask[field_idx] == True
            field_scored = score_card.data[field_idx] != 0

            if field_idx == 6:
                self.logger.log('\tBONUS\t\t\t' + ('50' if sum(score_card.data[:6]) >= 63 else '0') + '\t(' + f'{int(sum(score_card.data[:6])) - 63}' + ')' + '\n', self.config['verbosity'], 0)

            self.logger.log(f'\t({field_idx + 1}) {field_name}' + tabs, 0)
            if field_crossed or field_scored or len(dices) == 0:
                self.logger.log(white + str(int(logged_score)), 0)
                if logged_score >= (field_idx + 1) * 3 and 0 <= field_idx <= 5:
                    self.logger.log('\t(+' + str(int(logged_score - (field_idx + 1) * 3)) + ')', 0)
                elif 0 <= field_idx <= 5:
                    self.logger.log('\t(-' + str(int((field_idx + 1) * 3 - logged_score)) + ')', 0)
                self.logger.log('', 0)
            elif int(potential_score) == 0:
                self.logger.log(yellow + '-' + white + '\n', 0)
            else:
                self.logger.log(yellow + str(int(potential_score)), 0)
                if potential_score >= (field_idx + 1) * 3 and 0 <= field_idx <= 5:
                    self.logger.log('\t(+' + str(int(potential_score - (field_idx + 1) * 3)) + ')', 0)
                elif 0 <= field_idx <= 5:
                    self.logger.log('\t(-' + str(int((field_idx + 1) * 3 - potential_score)) + ')', 0)
                self.logger.log(white + '\n', 0)

    def get_reroll_idxs():
        values_to_reroll = Counter(list(map(int, input('\tEnter values to reroll:  ').split())))            
        return values_to_reroll

    def decide_reroll(self, score_fields, dices, throw_num):
        self.logger.log('\tthrow:\t\t\t' + str(throw_num) + '\n', 0)
        self.logger.log('\tdices:\t\t\t' + ' '.join(list(map(str, dices.data))) + '\n', 0)

        values_to_reroll = []
        while True:
            try:
                self.logger.log('\tEnter values to reroll:  ', 0)
                values_to_reroll = Counter(list(map(int, input().split())))            
                break
            except Exception as e:
                self.logger.log('Invalid input, try again.', 0)

        idxs_to_reroll = []
        for i in range(len(dices)):
            if dices[i] in values_to_reroll and values_to_reroll[dices[i]] > 0:
                idxs_to_reroll.append(i)
                values_to_reroll[dices[i]] -= 1

        return idxs_to_reroll

    def decide_score_logging(self, score_fields, dices):
        self.print_score_card_with_options(score_fields, dices)
        self.logger.log('\n\tdices:\t\t\t' + ' '.join(list(map(str, dices.data))) + '\n', 0)
        field_idx = 0
        while True:
            try:
                self.logger.log('\tEnter field index of the field you wish to log score in: ', 0)
                field_idx = int(input()) - 1
                assert 1 <= field_idx <= 15
                break
            except Exception as e:
                self.logger.log('Invalid input, try again.\n', 0)
        score = Helpers.count_score(dices, field_idx)
        return field_idx, score
