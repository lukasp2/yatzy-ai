import numpy.ma as ma

from collections import deque
from yatzy import Yatzy

# A Yatzy game in which a player trains the neural nets
class TrainingGame(Yatzy):
    def __init__(self, player):
        super().__init__([ player ])
        self.player = player
    
    def playN(self, N):
        self.high_score = 0
        game_scores = deque(maxlen=100)
        for current_play in range(1, N + 1):
            score = self.play(current_play, N)
            game_scores.append(score)
            self.average_score = sum(game_scores) / len(game_scores)
            if self.high_score < score:
                self.high_score = score
            print('\tavg. score:', self.average_score, 'after', current_play, 'games (high score: ' + str(self.high_score) + ')')

    def play(self, current_play = 1, N = 1, verbosity=2):
        self.history.clear_history()
        self.history.initiate_game()
        self.reset_boards()

        if verbosity > 0:
            print("TRAINING GAME", current_play, "/", N, '(played by', 'model)' if self.player.strategy.reroll_strategy == 'model' else 'random generator)')

        for round in range(1, 16):
            if verbosity > 1:
                print("\tROUND", round)
            self.history.game.initiate_play(self.player.score_fields)

            # the player throws all dice
            self.throw_die([ 0, 1, 2, 3, 4 ])

            if verbosity > 1:
                print("\t\tdie: ", end='')

            for reroll_num in range(2):
                # the player makes a decision to throw dice based on the result
                decision = self.player.decide_reroll(self.die)

                if verbosity > 1:
                    print( '[' + ', '.join([ str(self.die[idx]) + 'r' if idx in decision else str(self.die[idx]) for idx in range(len(self.die)) ]), '] -> ', end='')

                # the reroll is added to the history
                reroll = ma.masked_array(self.die, mask=[ 1 if i in decision else 0 for i in range(len(self.die))] )
                self.history.game.play.add_reroll(reroll)

                # throw dice again according to desicion
                self.throw_die(decision)

            if verbosity > 1:        
                print(str(list(self.die)))
            
            # the player makes a decision about what field on the score board should be filled with what value
            field_index, score = self.player.decide_score_logging(self.die)

            if verbosity > 1:
                print("\t\tput", score, "points on", self.idx_to_name(field_index))

            # log the score
            self.set_score_field(self.player, field_index, score)

            # the chosen scoring is saved in the history
            self.history.game.play.add_scoring(field_index, score)

            # save play to history
            self.history.game.commit_play()

        total_score = self.count_points(self.player)

        if verbosity > 0:
            print("\ttotal score:", total_score)

        self.history.commit_game(total_score)

        # train the players models with history
        #self.player.strategy.rerollModel.train(self.history)
        #self.player.strategy.scoreModel.train(self.history)

        return total_score