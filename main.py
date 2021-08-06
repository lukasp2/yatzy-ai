from training_game import TrainingGame
from neural_net import DiceThrowModel, ScoreLogModel
from player import Player
from game import Yatzy

# 1. create models
diceModel = DiceThrowModel()
scoreModel = ScoreLogModel()

# 1.5 (situational) load saved weights into the models
#diceModel.load_model()
#scoreModel.load_model()

# 2. create random desicion player and play N games for training models with random desicions
t = TrainingGame([ Player('Frank', 'random', diceModel, scoreModel) ])
t.playN(10000)

# 3. switch random player to model player and play N games for training models with the models own history
t.players = [ Player('Jerry', 'model', diceModel, scoreModel) ]
t.playN(1000)

# 4. (situational) save the state of the models (their weights) for loading later. will overwrite existing saves.
diceModel.save_model()
scoreModel.save_model()

# 5. check players average performance over N normal games without training
yatzy = Yatzy(t.players)
avg_score = yatzy.playN(3)
print('model has average score of', avg_score)
