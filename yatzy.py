import numpy as np
from logger import Logger

class Yatzy:
    dices = np.array([1, 1, 1, 1, 1])

    def __init__(self, configs):
        self.configs = configs
        self.logger = Logger(configs['verbosity'])

    def play(self):
        players = self.configs['players']
        self.logger.log_players(players)

        for current_play in range(1, self.configs['num_games'] + 1):
            self.logger.log_game_num(self.configs['num_games'], current_play)

            for player in players:
                player.prepare()

            for round in range(1, 16):
                self.logger.log_round_num(round)
                
                for player in players:
                    player.play(self.dices)

            for player in players:
                player.finish()

            self.logger.log_score_board(players)
            self.logger.log_stats(players)

        self.logger.log_score_distribution(players)
        self.logger.write_highscores_to_file(players)