import numpy as np
import tensorflow as tf
from copy import deepcopy

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

        # 2. initiate a play with available fields and score board
        def initiate_play(self, score_fields):
            self.play = self.Play(deepcopy(score_fields))

        class Play:
            def __init__(self, score_fields):
                self.score_fields = deepcopy(score_fields) # [ s1, s2, ..., s15 ] (just the scores)
                self.dice_throws = [] # [[ d1, d2, ... d5 ], * 3 ]
                self.scoring = [] # [ field_index, score ]

            # 3. add dice throw result to the play (three results will be added)
            def add_dice(self, dice):
                self.dice_throws.append(deepcopy(dice))

            # 4. add the scoring
            def add_scoring(self, field_index, score):
                self.scoring = [ deepcopy(field_index), deepcopy(score) ]

        # 5. append the play to history log
        def commit_play(self):
            self.plays.append(self.play)

    def clear_history(self):
        self.games.clear()

    # retrieve parts of the history which the model use for training
    def get_dice_throw_data(self):
        data = {
            "die" : [],
            "throw_number" : [],
            "score_fields" : [],
            "outputs" : []
        }

        for game in self.games:
            for play in game.plays:
                for throw_number in range(len(play.dice_throws)):
                    data["die"].append(play.dice_throws[throw_number])
                    data["throw_number"].append ( throw_number )
                    data["score_fields"].append(play.score_fields)
                    data["outputs"].append(game.final_score)

        return data
    
    # retrieve parts of the history which the model use for training
    def get_score_log_data(self):
        data = {
            "field_indexes" : [],
            "die" : [],
            "score_fields" : [],
            "outputs" : []
        }

        for game in self.games:
            for play in game.plays:
                data["field_indexes"].append( play.scoring[0] ) # field index of current option
                data["die"].append(play.dice_throws[-1])
                data["score_fields"].append(play.score_fields)
                data["outputs"].append(game.final_score)

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
