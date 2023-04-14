from helpers import Helpers
from player import Player

class AI(Player):
    def __init__(self, name):
        super().__init__(name)

    def decide_reroll(self, score_fields, dices, throw_num):
        dice_idxs_to_reroll = self.rerollModel.decide_reroll(score_fields, dices, throw_num)
        self.logger.log_rerolls(self.name, dices, dice_idxs_to_reroll, throw_num)
        return dice_idxs_to_reroll

    def decide_score_logging(self, score_fields, dices):
        field_idx = self.scoreLogModel.decide_score_logging(score_fields, dices)
        score = Helpers.count_score(dices, field_idx)
        self.logger.log_scoring(self.name, dices, score, field_idx)
        return field_idx, score
