from models import DiceThrowModel, ScoreLogModel
from training_game import TrainingGame
from player import Player
from strategy import Strategy

def main():
    diceModel = DiceThrowModel()
    scoreModel = ScoreLogModel()

    # 1. create strategies
    rnd_strategy = Strategy('random', diceModel, scoreModel)
    model_strategy = Strategy('model', diceModel, scoreModel, load_models=False)
    
    # 2. play N random games for training
    t = TrainingGame( Player('Frank', rnd_strategy) )
    t.playN(1000)

    # 3. play N model games for training
    t.player.strategy = model_strategy
    t.playN(100)

    # 4. save the state of the models (their weights) for loading later.
    diceModel.save_model()
    scoreModel.save_model()

    # 5. check players average performance over N normal games without training
    print('model has average score of', t.average_score)

    # avg: 68.62 after 1010 games
    # avg: 70.89 after 1200 games
    # avg. 71.52 after 1300 games
    # avg. 72.15 after 1400 games

if __name__ == '__main__':
    main()