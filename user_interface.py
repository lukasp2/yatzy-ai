from models import DiceThrowModel, ScoreLogModel
from training_game import TrainingGame
from player import Player
from strategy import Strategy

class UserInterface():
    def __init__(self):
        self.diceModel = DiceThrowModel()
        self.scoreModel = ScoreLogModel()

    def help(self):
        # print mode helptext
        pass

    def start(self):
        configs = {
            'random games' : True,
            'load models' : True,
            'model games' : True,
            'num random games' : 2000,
            'num model games' : 10,
            'save models' : True,
        }

        # run ui here and set values in configs ...

        self.run(configs)
        
    def run(self, configs):
        if configs['random games']:
            rnd_strategy = Strategy('random', self.diceModel, self.scoreModel)    
            t = TrainingGame( Player('Frank', rnd_strategy) )
            t.playN(configs['num random games'])

        if configs['model games']:
            model_strategy = Strategy('model', self.diceModel, self.scoreModel, load_models=configs['load models'])
            t = TrainingGame( Player('Frank', model_strategy) )
            t.playN(configs['num model games'])

        if configs['save models']:
            self.diceModel.save_model()
            self.scoreModel.save_model()




