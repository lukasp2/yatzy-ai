from collections import Counter
import numpy as np
import numpy.ma as ma
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
                self.rerolls = [] # [[ d1, d2, ... d5 ], * 2 ]
                self.scoring = [] # [ field_index, score ]

            # 3. add reroll result to the play (two rerolls)
            def add_reroll(self, reroll):
                self.rerolls.append(deepcopy(reroll))

            # 4. add the scoring
            def add_scoring(self, field_index, score):
                self.scoring = [ deepcopy(field_index), deepcopy(score) ]

        # 5. append the play to history log
        def commit_play(self):
            self.plays.append(self.play)

    def clear_history(self):
        self.games.clear()

    # retrieve parts of the history which the model use for training
    def get_reroll_data(self):
        data = {
            "die" : [],
            "outputs" : []
        }

        for game in self.games:
            for play in game.plays:
                for reroll_num in range(len(play.rerolls)):
                    data["die"].append(play.rerolls[reroll_num])
                    data["outputs"].append(np.array([ self.count_score(play.rerolls[reroll_num], i) for i in range(15) ]))
        return data
    
    # retrieve parts of the history which the model use for training
    def get_score_log_data(self):
        data = {
            "field_indexes" : [],
            "scores" : [],
            "score_fields" : [],
            "outputs" : []
        }

        for game in self.games:
            for play in game.plays:
                data["field_indexes"].append(play.scoring[0]) # field index of current option
                data["scores"].append(play.scoring[1]) # score of current option
                data["score_fields"].append(play.score_fields[:6])
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


    def count_score(self, die, field_index):
        def find_highest_duplicate_dice(die, min_occurances):
            duplicates = [ k for k, v in Counter(die.data).items() if v >= min_occurances ]
            highest_dice = max(duplicates) if duplicates else 0
            return highest_dice

        points = 0
        if 0 <= field_index <= 5: # singles
            points = np.count_nonzero(die == field_index + 1, axis=0) * (field_index + 1)
        if field_index == 6: # pair
            points = find_highest_duplicate_dice(die, 2) * 2
        if field_index == 7: # two pair
            dup_1 = find_highest_duplicate_dice(die, 2)
            if dup_1:
                dice_cpy = ma.masked_array([ x for x in die if x != dup_1 ], mask=False)
                dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                if dup_2:
                    points = dup_1 * 2 + dup_2 * 2
        if field_index == 8: # three of a kind
            points = find_highest_duplicate_dice(die, 3) * 3
        if field_index == 9: # four of a kind
            points = find_highest_duplicate_dice(die, 4) * 4
        if field_index == 10: # small straigt
            if np.all(die == np.array([1, 2, 3, 4, 5])):
                points = 15
        if field_index == 11: # large straigt
            if np.all(die == np.array([2, 3, 4, 5, 6])):
                points = 20
        if field_index == 12: # full house
            dup_1 = find_highest_duplicate_dice(die, 3)
            if dup_1:
                dice_cpy = ma.masked_array([ x for x in die if x != dup_1 ], mask=False)
                dup_2 = find_highest_duplicate_dice(dice_cpy, 2)
                if dup_2:
                    points = dup_1 * 3 + dup_2 * 2
        if field_index == 13: # chance
            points = sum(die)
        if field_index == 14: # yatzy
            if np.all(die == die[0]):
                points = 50
        return points