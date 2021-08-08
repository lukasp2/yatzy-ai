from models import DiceThrowModel, ScoreLogModel
from training_game import TrainingGame
from player import Player
from strategy import Strategy
import warnings

def main():
    diceModel = DiceThrowModel()
    scoreModel = ScoreLogModel()

    # 1. create strategies
    rnd_strategy = Strategy('random', diceModel, scoreModel)
    model_strategy = Strategy('model', diceModel, scoreModel, load_models=False)
    
    # 2. play N games for training
    t = TrainingGame( Player('Frank', rnd_strategy) )
    t.playN(1000)

    # 3. play N model games for training
    t.player.strategy = model_strategy
    t.playN(1000)

    # 4. save the state of the models (their weights) for loading later.
    diceModel.save_model()
    scoreModel.save_model()

if __name__ == '__main__':
    warnings.simplefilter('error', UserWarning)
    main()