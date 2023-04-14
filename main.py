from yatzy import Yatzy
from models import ScoreLogModel, RerollModel
from players.random_player import Random
from players.human_player import Human
from players.ai_player import AI
from players.statistical_player import Statistical

config = {
    'players' : [
        Random('Sir Blunder'),
        #Human('You'),
        #AI('Cowboy Beep beep'),
        #Statistical('Rain man'),
    ],
    'num_games' : 1000,
    'models' : {
        'scoreLogModel' : {
            'class' : ScoreLogModel(),
            'load' : True,
            'save' : True,  # WARNING: Saving w/o loading will overwrite current save
        },
        'rerollModel' : {
            'class' : RerollModel(),
            'load' : True,
            'save' : True,  # WARNING: Saving w/o loading will overwrite current save
        },
    },
    'verbosity' : 
        [
        -2, # disable prints and logging (~8:50 min/1000 games)
        -1, # disable prints
        0, # print player statistics in each game
        1, # 0 + print player score logging in each round
        2, # 1 + print all player actions in each round and score board in each game (~9:24 min/1000 games)
        3, # 2 + print all players score distribution after each program run
        ][2],
}

def main(): 
    ## prepare
    for model in config['models']:
        config['models'][model]['class'].prepare(config['models'][model])

    for player in config['players']:
        player.set_config(config)

    ## play
    game = Yatzy(config)
    game.play()

    ## finish
    for model in config['models']:
        config['models'][model]['class'].finish(config['models'][model])

if __name__ == '__main__':
    main()
