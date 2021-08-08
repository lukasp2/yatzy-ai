import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.python.keras.layers.core import Dropout

class Model:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.model = None

    # takes training data and feeds it to the model
    def train(self, inputs, outputs):
        inputs = np.array(inputs).reshape(-1, self.num_inputs)
        outputs = np.array(outputs).reshape(-1, self.num_outputs)
        self.model.fit(inputs, outputs)

    def save_model(self, filename):
        model_json = self.model.to_json()
        with open(filename + ".json", "w") as json_file:
            json_file.write(model_json)
        self.model.save_weights(filename + ".h5")

    def load_model(self, filename):
        json_file = open(filename + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = keras.models.model_from_json(loaded_model_json)
        self.model.load_weights(filename + '.h5')
        self.compile_model()

    def compile_model(self):
        self.model.compile(optimizer="adam", loss='mean_squared_error', metrics=['mean_squared_error'])

    # turns a value into a one-hot, like for the dice value 2, the func
    # call would be to_categorical(6, 1) with return val [0, 0, 0, 0, 1, 0]
    def to_categorical(self, num_classes, category):
        return list(tf.keras.utils.to_categorical(category, num_classes=num_classes, dtype=int))

    # to_categorical_lst(3, [0, 1, 2]) -> [[0,0,1], [0,1,0], [1,0,0]
    def to_categorical_lst(self, num_classes, lst):
        categorical_lst = []
        for value in lst:
            categorical_lst.append(self.to_categorical(num_classes, value))
        return categorical_lst

    def categorize_die(self, die):
        categorical_die = []
        for dice in die:
            if dice == 0:
                categorical_die += [0,0,0,0,0,0]
            else:
                categorical_die += self.to_categorical(6, dice - 1)
        return categorical_die

    # functions for normalizing the input values to the models
    def normalize_final_scores(self, final_scores):
        return [ final_score / 374.0 for final_score in final_scores ]

    def normalize_score_fields(self, score_fields):
        return [ score / 50.0 for score in score_fields ]

# Model predicting which of the 5 die is best to throw again.
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
#   * (3) throw number [0..2] as a one-hot value: [x, x, x]
#   * (15) Player.score_fields: [s1, s2, ..., s15]
#   * (15) Player.available_fields: [a1, a2, ..., a15]
# output:
#   * (1) expected final score of the game for this input
class DiceThrowModel(Model):
    def __init__(self, load=False):
        super().__init__(63, 1)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=63, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

        if load:
            self.load_model()

    # train model with inputs and outputs from one game
    # number of dice throws are 15 * 3, thus one game consists of 45 batches
    def train(self, history):
        data = history.getDiceThrowData()
        die = [ self.categorize_die(die) for die in data["die"] ]
        throw_number = [ self.to_categorical(3, throw_number) for throw_number in data["throw_number"] ]
        score_fields = [ self.normalize_score_fields(score_field) for score_field in data["score_fields"] ]
        available_fields = data["available_fields"]

        inputs = [[die[i] + throw_number[i] + score_fields[i] + available_fields[i]] for i in range(len(die))]
        outputs = self.normalize_final_scores(data["outputs"])

        super().train(inputs, outputs)
    
    # make a prediction of output based on input
    def predict(self, data, index = 0):
        die = self.categorize_die(data["die"])
        throw_number = self.to_categorical(3, data["throw_number"])
        score_fields = self.normalize_score_fields(data["score_fields"])
        available_fields = data["available_fields"]

        inputs = die + throw_number + score_fields + available_fields
        predicted_output = self.model.predict(np.array(inputs).reshape(-1, self.num_inputs))[0][index]
        return predicted_output

    # returns the dice to throw in the form of a list of indexes
    def decide_dice_throw(self, score_fields, available_fields, throw_number, dice):
        max_value = 0
        best_move = [0, 1, 2, 3, 4]

        # looping through all 32 ways to select any number of die from 5 die (2^5)
        for i in range(32):
            inputs = {}
            # using a binary counter going from 00000 ... 11111 as a way to select
            # all combinations of dice, each combination stored in 'move'
            inputs["die"] = [ a * b for a, b in zip(dice, list(map(int, bin(i)[2:].zfill(5)))) ]
            inputs["throw_number"] = throw_number
            inputs["score_fields"] = score_fields
            inputs["available_fields"] = available_fields
            value = self.predict(inputs)

            if value > max_value:
                max_value = value
                best_move = inputs["die"]

        dice_to_throw = [ i for i in range(len(best_move)) if best_move[i] == 0 ]

        return dice_to_throw

    def save_model(self):
        return super().save_model('DiceThrowModel')

    def load_model(self):
        return super().load_model('DiceThrowModel')

# Model predicting best field to pick on the score board given a set of die.
# input: 
#   * (15) score field: field_index as one-hot value
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
#   * (15) Player.score_fields: [s1, s2, ..., s15]
#   * (15) Player.available_fields: [a1, a2, ..., a15]
# output:
#   * (1) expected final score of the game for this input
class ScoreLogModel(Model):
    def __init__(self, load=False):
        super().__init__(75, 1)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=64, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

        if load:
            self.load_model()
        
    # train model with inputs and outputs
    def train(self, history):
        data = history.getScoreLogData()
        field_indexes = [ self.to_categorical(15, field_index) for field_index in data["field_indexes"] ]
        die = [ self.categorize_die(die) for die in data["die"] ]
        score_fields = [ self.normalize_score_fields(score_field) for score_field in data["score_fields"] ]
        available_fields = data["available_fields"]

        inputs = [ field_indexes[i] + die[i] + score_fields[i] + available_fields[i] for i in range(len(die))]
        outputs = self.normalize_final_scores(data["outputs"])
        super().train(inputs, outputs)

    # make a prediction of output based on input
    def predict(self, data, index = 0):
        field_index = self.to_categorical(15, data["field_index"])
        die = self.categorize_die(data["die"])
        score_fields = self.normalize_score_fields(data["score_fields"])
        available_fields = data["available_fields"]

        inputs = field_index + die + score_fields + available_fields
        predicted_output = self.model.predict(np.array(inputs).reshape(-1, self.num_inputs))[0][index]
        return predicted_output

    # returns the best move in the form [field_index, score]
    def decide_score_logging(self, die, score_fields, available_fields, possible_moves):
        max_value = 0
        best_move = possible_moves[0]

        for move in possible_moves:
            inputs = {}
            inputs["field_index"] = move[0]
            inputs["die"] = die
            inputs["score_fields"] = score_fields
            inputs["available_fields"] = available_fields
            value = self.predict(inputs)

            if value > max_value:
                max_value = value
                best_move = move

        return best_move
  
    def save_model(self):
        return super().save_model('ScoreLogModel')

    def load_model(self):
        return super().load_model('ScoreLogModel')