from training_game import TrainingGame
from neural_net import DiceThrowModel, ScoreLogModel
from player import Player
from game import Yatzy

# 1. create models
diceModel = DiceThrowModel()
scoreModel = ScoreLogModel()

# 2. create random desicion player, play N games, and train models with random desicions
t = TrainingGame([ Player('Frank', 'random', diceModel, scoreModel) ])
t.playN(10000)

# 3. switch random player to model player, play N games, and train models with the models own history
t.players = [ Player('Jerry', 'model', diceModel, scoreModel) ]
t.playN(1000)

# 4. check players average performance over N normal games without training
yatzy = Yatzy(t.players)
avg_score = yatzy.playN(1)
print('model has average score of', avg_score)
