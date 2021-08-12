from collections import Counter
from yatzy import Helpers
import numpy as np
import numpy.ma as ma
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

class Model:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.model = None

    # takes training data and feeds it to the model
    def train(self, inputs, outputs):
        inputs = np.array(inputs, dtype='float32').reshape(-1, self.num_inputs)
        outputs = np.array(outputs).reshape(-1, self.num_outputs)
        self.model.fit(inputs, outputs)

    def save_model(self, filename):
        model_json = self.model.to_json()
        with open('data/' + filename + '.json', 'w') as json_file:
            json_file.write(model_json)
        self.model.save_weights('data/' + filename + '.h5')

    def load_model(self, filename):
        json_file = open('data/' + filename + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = keras.models.model_from_json(loaded_model_json)
        self.model.load_weights('data/' + filename + '.h5')
        self.compile_model()

    def compile_model(self):
        self.model.compile(optimizer="adam", loss='mean_squared_error', metrics=['mean_squared_error'])

    # turns a value into a one-hot, like for the dice value 2, the func
    # call would be to_categorical(6, 1) with return val [0, 0, 0, 0, 1, 0]
    def to_categorical(self, num_classes, category):
        return np.array(tf.keras.utils.to_categorical(category, num_classes=num_classes, dtype=int))

    def categorize_die(self, die):
        categorical_die = ma.masked_array([])
        for dice in die:
            one_hot_dice_val = self.to_categorical(6, dice - 1)
            masked_dice = ma.masked_array(one_hot_dice_val, mask=dice is ma.masked)
            categorical_die = ma.concatenate([categorical_die, masked_dice])
        return categorical_die

    def available_fields(self, score_fields):
        return [ 1 if score is not ma.masked else 0 for score in score_fields ]

    # functions for normalizing the input values to the models
    def normalize_final_scores(self, final_scores):
        return [ final_score / 374 for final_score in final_scores ]

    def normalize_score(self, field_index, score):
        #max_scores = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50])
        max_scores = np.array([4, 6, 9, 12, 14, 17,  16, 15, 18, 22, 13, 17, 20, 60, 25])
        return np.array([score / max_scores[field_index]])

    def normalize_score_fields(self, score_fields):
        #max_scores = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50])
        max_scores = np.array([4, 6, 9, 12, 14, 17,  16, 15, 18, 22, 13, 17, 20, 60, 25])
        return [ score_fields.data[idx] / max_scores[idx] for idx in range(len(score_fields)) ]

# Model predicting which of the 5 die is best to throw again.
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
# output:
#   * (15) expected value for each field
class RerollModel(Model):
    def __init__(self):
        super().__init__(30, 15)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=40, activation='relu'),
            Dense(units=40, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

    def compile_model(self):
        opt = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=[])

    # train model with inputs and outputs from one game
    def train(self, data):
        inputs = [ self.categorize_die(die) for die in data["die"] ]
        outputs = [ self.normalize_score_fields(score_fields) for score_fields in data["outputs"] ]
        super().train(inputs, outputs)
    
    # make a prediction of output based on input
    def predict(self, data):
        die = self.categorize_die(data["die"])
        input_tensor = die
        predicted_output = self.model.predict(input_tensor.reshape(-1, self.num_inputs))[0]
        return predicted_output

    # returns the dice to throw in the form of a list of indexes
    def decide_reroll(self, score_fields, die):
        max_value = 0
        prediction = self.predict({'die' : die})

        # filter predictions that would give zero points and predictions for fields that are unavailable
        for field_index, value in enumerate(prediction):
            if Helpers().count_score(die, field_index) == 0:
                prediction[field_index] = 0

        best_move = 0

        for field_index, value in Helpers().get_possible_moves(die, score_fields):
            if value > max_value:
                max_value = value
                best_move = field_index

        die_to_throw = Helpers().get_die_idx_for_play(die, best_move)

        return die_to_throw

    def save_model(self):
        return super().save_model('RerollModel')

    def load_model(self):
        return super().load_model('RerollModel')

# Model predicting which field to log score in for a set of die
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
# output:
#   * (15) expected value for each field
class ScoreLogModel(Model):
    def __init__(self):
        super().__init__(30, 15)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=40, activation='relu'),
            Dense(units=40, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

    def compile_model(self):
        opt = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=[])

    # train model with inputs and outputs from one game
    def train(self, data):
        inputs = [ self.categorize_die(die) for die in data["die"] ]
        outputs = [ self.normalize_score_fields(score_fields) for score_fields in data["outputs"] ]
        super().train(inputs, outputs)
    
    # make a prediction of output based on input
    def predict(self, data):
        die = self.categorize_die(data["die"])
        input_tensor = die
        predicted_output = self.model.predict(input_tensor.reshape(-1, self.num_inputs))[0]
        return predicted_output

    # returns the best move in the form [field_index, score]
    def decide_score_logging(self, score_fields, die):
        max_value = 0
        prediction = self.predict({'die' : die})

        # filter predictions that would give zero points and predictions for fields that are unavailable
        for field_index, value in enumerate(prediction):
            if Helpers().count_score(die, field_index) == 0:
                prediction[field_index] = 0

        possible_moves = Helpers().get_possible_moves(die, score_fields)
        best_move = possible_moves[0][0]

        for field_index, value in possible_moves: ## its available??
            if value > max_value:
                max_value = value
                best_move = field_index

        return best_move, Helpers().count_score(die, best_move)

    def save_model(self):
        return super().save_model('ScoreLogModel')

    def load_model(self):
        return super().load_model('ScoreLogModel')
