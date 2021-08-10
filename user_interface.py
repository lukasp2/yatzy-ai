from models import RerollModel, ScoreLogModel
from training_game import TrainingGame
from player import Player
from strategy import Strategy

class UserInterface():
    def __init__(self):
        self.rerollModel = RerollModel()
        self.scoreModel = ScoreLogModel()

    def help(self):
        # print mode helptext
        pass

    def start(self):
        configs = { 
            'random games' : True,
            'load models' : False,
            'model games' : False,
            'num random games' : 10000,
            'num model games' : 0,
            'save models' : True,
            'reroll_strategy' : 'model',
            'score_strategy' : 'model',
        }

        # run ui here and set values in configs ...

        self.run(configs)
        
    def run(self, configs):
        if configs['random games']:
            rnd_strategy = Strategy('random', 'random', self.rerollModel, self.scoreModel)    
            t = TrainingGame( Player('Frank', rnd_strategy) )
            t.playN(configs['num random games'])

        if configs['model games']:
            model_strategy = Strategy(configs['reroll_strategy'], configs['score_strategy'], self.rerollModel, self.scoreModel, load_models=configs['load models'])
            t = TrainingGame( Player('Frank', model_strategy) )
            t.playN(configs['num model games'])

        if configs['save models']:
            self.rerollModel.save_model()
            self.scoreModel.save_model()




