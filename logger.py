import datetime
import subprocess
import json 
from helpers import Helpers
import itertools

class Logger:
    def __init__(self, verbosity):
        self.verbosity = verbosity
        self.logfile = 'yatzy.log'
        self.highscore_file = 'scoreboard.json'
        self.__reroll_log_msg = ''

    def log(self, message, msg_verbosity):
        if self.verbosity < -1:
            return
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        with open(self.logfile, 'a') as f:
            f.write(f'{timestamp}> {message}')
        
        if self.verbosity >= msg_verbosity:
            print(message, end='')
        pass

    def log_players(self, players):
        if self.verbosity < -1:
            return
        self.log('players: ' + ', '.join([player.name + ' (' + player.get_name() + ')' for player in players]) + '\n', 1)

    def log_game_num(self, tot_games, curr_game):
        if self.verbosity < -1:
            return
        self.log('\n', 1)
        self.log('GAME ' + str(curr_game) + "/" + str(tot_games) + '\n', 1)
    
    def log_round_num(self, curr_round):
        if self.verbosity < -1:
            return
        if curr_round != 1:
            self.log('\n', 1)
        self.log('\tROUND ' + str(curr_round) + '\n', 1)

    def log_rerolls(self, player_name, dices, dice_idxs_to_reroll, throw_num):
        if self.verbosity < -1:
            return
        if throw_num == 1:
            self.log('\tplayer:\t\t\t' + player_name + '\n', 2)
            self.__reroll_log_msg = "\tdices:\t\t\t"
        self.__reroll_log_msg += '[' + ', '.join([ str(dices[idx]) + 'r' if idx in dice_idxs_to_reroll else str(dices[idx]) for idx in range(len(dices)) ]) + '] -> '

    def log_scoring(self, player_name, dices, score, field_idx):
        if self.verbosity < -1:
            return
        self.__reroll_log_msg += str(list(dices)) + '\n'
        self.log(self.__reroll_log_msg, 2)
        self.log('\t' + player_name + ' put ' + str(score) + ' points on ' + Helpers.idx_to_name(field_idx) + '\n', 1)

    def log_stats(self, players):
        if self.verbosity < -1:
            return
        self.log('\tPLAYER\t\t\t' + ''.join([player.name + '\t' for player in players]) + '\n', 0)
        #self.log('\tcur. score\t\t' + ''.join([str(int(player.count_points())) + '\t\t' for player in players]) + '\n', 0)
        self.log('\tavg. score\t\t' + ''.join([str(int(sum(player.game_scores) / len(player.game_scores))) + '\t\t' for player in players]) + '\n', 0)
        self.log('\thigh score\t\t' + ''.join([str(int(max(player.game_scores))) + '\t\t' for player in players]) + '\n', 0)

    def log_score_board(self, players):
        if self.verbosity < -1:
            return
        self.log('\n', 2)
        self.log('\tPLAYER\t\t\t' + ''.join([player.name + '\t' for player in players]) + '\n', 2)
        for i in range(15):
            tabs = '\t\t' if 7 <= i <= 12 else '\t\t\t'
            self.log('\t' + Helpers().idx_to_name(i) + tabs + ''.join([str(int(player.score_fields.data[i])) + '\t\t' for player in players]) + '\n', 2)
            if i == 5:
                self.log('\tSUM\t\t\t' + ''.join([str(int(player.count_bonus_points())) + '\t\t' for player in players]) + '\n', 2)
                self.log('\tBONUS\t\t\t' + ''.join([str(player.get_bonus()) + '\t\t' for player in players]) + '\n', 2)
        self.log('\tTOTAL\t\t\t' + ''.join([str(int(player.count_points())) + '\t\t' for player in players]) + '\n', 2)
        self.log('\n', 2)

    def log_score_distribution(self, players):
        games_per_hashtag = len(players[0].game_scores) / 1000
        for player in players:
            self.log('\n', 3)
            self.log('\t' + player.name + '\n', 3)
            counter = list(itertools.repeat(0, 38))
            for score in player.game_scores:
                idx = int(score / 10)
                counter[idx] += 1

            for i in reversed(range(len(counter))):
                a = i * 10
                b = a + 9 
                games_with_this_score = counter[i]
                num_hashtags = int(games_with_this_score / games_per_hashtag)
                self.log('\t' + str(a).rjust(3, "O") + '-' + str(b).rjust(3, "O") + ': ' + '#' * min(num_hashtags, 150) + '\n', 3)

    def write_highscores_to_file(self, players):
        def get_git_commit():
            try:
                output = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT)
                commit_hash = output.decode('utf-8').strip()
                return commit_hash
            except subprocess.CalledProcessError:
                return 'n/a'

        try:
            with open(self.highscore_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        except json.decoder.JSONDecodeError:
            data = {}

        commit = get_git_commit()
        date = datetime.date.today().strftime('%Y-%m-%d')
        for player in players:
            high_score = max(player.game_scores)
            avg_score = sum(player.game_scores) / len(player.game_scores)
            if player.get_name() not in data:
                data[player.get_name()] = []

            entry = {}
            entry['highscore'] = int(high_score)
            entry['player'] = player.name
            entry['average'] = int(avg_score)
            entry['num_games'] = len(player.game_scores)
            entry['date'] = date
            entry['commit'] = commit

            data[player.get_name()].append(entry)
            data[player.get_name()].sort(key=lambda x: x['highscore'], reverse=True)
            data[player.get_name()] = data[player.get_name()][:5]

        with open(self.highscore_file, 'w') as f:
            json.dump(data, f, indent=4)