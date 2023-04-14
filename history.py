from copy import deepcopy
from helpers import Helpers

# A class to log the all games so that we can provide the model with data for training
# after the games have been completed. Functions are called in the order 1, 2, 3, 4, 5, 6
# History: [ Game( [ Play( [[ d1, d2, d3, d4, d5 ], * 3], [field_index, score] ), * 15], final_score ),  ... ]
class History:
    def __init__(self):
        self.games = [] # [ Game() * X ]

    # 1. initiate a new game
    def initiate_game(self):
        self.game = self.Game()

    # 6. append the game to history log
    def commit_game(self, final_score):
        self.game.final_score = deepcopy(final_score)
        self.games.append(self.game)

    class Game:
        def __init__(self):
            self.final_score = 0
            self.plays = [] # [ Play() * 15 ]
            self.play = None

        # 2. initiate a play with available fields and score board
        def initiate_play(self, score_fields):
            self.play = self.Play(deepcopy(score_fields))

        class Play:
            def __init__(self, score_card):
                self.score_card = deepcopy(score_card) # [ s1, s2, ..., s15 ] (just the scores)
                self.rerolls = [] # [[ d1, d2, ... d5 ], * 2 ]
                self.score = 0
                self.field_idx = 0

            # 3. add reroll result to the play (two rerolls)
            def add_reroll(self, reroll):
                self.rerolls.append(deepcopy(reroll))

            # 4. add the scoring
            def add_scoring(self, field_idx, score):
                self.field_idx = field_idx
                self.score = score

        # 5. append the play to history log
        def commit_play(self):
            self.plays.append(self.play)

    def clear_history(self):
        self.games.clear()

    # retrieve parts of the history which the model use for training
    def get_reroll_data(self):
        data = {
            "dices" : [],
            "avail_sc_fields" : [],
            "reroll_num" : [],
            "bonus_reached" : [],
            "dice_idx_rerolled" : [],
            "outputs" : [],
        }

        for game in self.games:
            norm_final_score = game.final_score / Helpers.max_score
            for play in game.plays:
                bonus_reached = 1 if Helpers.bonus_reached(play.score_card) else 0
                for reroll_num in range(len(play.rerolls)):
                    data["dices"].append(play.rerolls[reroll_num].data)
                    data["avail_sc_fields"].append([ 1 if Helpers.field_available(play.score_card, field_idx) else 0 for field_idx in range(len(play.score_card)) ])
                    data["reroll_num"].append(reroll_num)
                    data["bonus_reached"].append(bonus_reached)
                    data["dice_idx_rerolled"].append(play.rerolls[reroll_num].mask)
                    data["outputs"].append(norm_final_score)
        return data
    
    # retrieve parts of the history which the model use for training
    def get_score_log_data(self):
        data = {
            "dices" : [],
            "score_cards" : [],
            "bonus_reached" : [],
            "scores" : [],
            "field_idxs" : [],
            "outputs" : [],
        }

        for game in self.games:
            norm_final_score = game.final_score / Helpers.max_score
            for play in game.plays:
                data["dices"].append(play.rerolls[len(play.rerolls) - 1])
                data["score_cards"].append(play.score_card)
                data["bonus_reached"].append(Helpers.bonus_reached(play.score_card))
                data["scores"].append(play.score)
                data["field_idxs"].append(play.field_idx)
                data["outputs"].append(norm_final_score)
        return data

    # for printing nice, verbose, score board
    def get_score_board(self):
        last_game = self.games[-1]
        data = {
            'plays' : [],
            'final_score' : last_game.final_score
        }

        for round, play in enumerate(last_game.plays):
            data['plays'].append({
                'round' : round,
                'field_index' : play.scoring[0],
                'score' : play.scoring[1],
                'dice_throws' : play.dice_throws,
            })

        return data