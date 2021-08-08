from strategy import Strategy
from training_game import TrainingGame
from player import Player

# 1. create random desicion player and play N games for training models with random desicions
t = TrainingGame( Player('Frank', Strategy('random')) )
#t.playN(10000)

# 3. switch strategy of the player and play N games for training models with the models own history
t.player.strategy = Strategy('model', load_models=True)
t.playN(1000)

# 4. (situational) save the state of the models (their weights) for loading later.
t.player.strategy.diceModel.save_model()
t.player.strategy.scoreModel.save_model()

# 5. check players average performance over N normal games without training
print('model has average score of', t.average_score)
