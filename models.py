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
        max_scores = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50])
        return np.array([score / max_scores[field_index]])

    def normalize_score_fields(self, score_fields):
        max_scores = np.array([5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 15, 20, 28, 30, 50])
        return [ score_fields.data[idx] / max_scores[idx] for idx in range(len(score_fields)) ]

# Model predicting which of the 5 die is best to throw again.
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
#   * (2) reroll number [0..2] as a one-hot value: [x, x]
#   * (15) available score fields: [s1, s2, ..., s15] 1 = available
# output:
#   * (1) expected final score of the game for this input
class RerollModel(Model):
    def __init__(self):
        super().__init__(47, 1)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=42, activation='relu'),
            Dense(units=42, activation='relu'),
            Dense(units=42, activation='relu'),
            Dense(units=42, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

    # train model with inputs and outputs from one game
    # number of dice throws are 15 * 3, thus one game consists of 45 batches
    def train(self, history):
        data = history.get_reroll_data()
        die = [ self.categorize_die(die) for die in data["die"] ]
        reroll_num = [ self.to_categorical(2, reroll_num) for reroll_num in data["reroll_num"] ]
        available_fields = [ self.available_fields(score_fields) for score_fields in data["score_fields"] ]

        outputs = [ self.normalize_score(item[0], item[1]) for item in data["outputs"] ]
        inputs = [ ma.concatenate([die[i], reroll_num[i], available_fields[i]]) for i in range(len(die)) ]
        
        #print('models.py: RerollModel:train() inputs:')
        #[ print('die', data["die"][i], '\nreroll num', data['reroll_num'][i], '\nscore fields', data['score_fields'][i], '\noutput:', data['outputs'][i], '\n') for i in range(len(die)) ]

        super().train(inputs, outputs)
    
    # make a prediction of output based on input
    def predict(self, data, index = 0):
        die = self.categorize_die(data["die"])
        reroll_num = self.to_categorical(2, data["reroll_num"])
        score_fields = self.normalize_score_fields(data["score_fields"])

        input_tensor = ma.concatenate([die, reroll_num, score_fields])
        predicted_output = self.model.predict(input_tensor.reshape(-1, self.num_inputs))[0][index]    
        return predicted_output

    # returns the dice to throw in the form of a list of indexes
    def decide_reroll(self, score_fields, reroll_num, dice):
        max_value = 0
        best_move = ma.masked_array([0, 1, 2, 3, 4], mask=False)

        # looping through all 32 ways to select any number of die from 5 die (2^5)
        for i in range(32):
            # using a mask to select all possible combinations of dice
            mask = list(map(int, bin(i)[2:].zfill(5)))
            inputs = { 
                "die" : ma.masked_array(dice, mask=mask),
                "reroll_num" : reroll_num,
                "score_fields" : score_fields,
            }
            value = self.predict(inputs)
            if value > max_value:
                max_value = value
                best_move = inputs["die"]

        die_to_throw = np.array([ idx for idx in range(len(best_move)) if best_move[idx] is not ma.masked ])
        return die_to_throw

    def save_model(self):
        return super().save_model('RerollModel')

    def load_model(self):
        return super().load_model('RerollModel')

# Model predicting best field to pick on the score board
# input: 
#   * (15) score field: field_index as one-hot value
#   * (1) score value
#   * (6) Player.score_fields: [s1, s2, ..., s6] # change to [0..5]?
# output:
#   * (1) expected final score of the game for this input
class ScoreLogModel(Model):
    def __init__(self):
        super().__init__(22, 1)

        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=20, activation='relu'),
            Dense(units=20, activation='relu'),
            Dense(units=20, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

        self.compile_model()

    # train model with inputs and outputs
    def train(self, history):
        data = history.get_score_log_data()
        field_indexes = [ self.to_categorical(15, field_index) for field_index in data["field_indexes"] ]
        scores = [ self.normalize_score(field_index, score) for field_index, score in zip(data["field_indexes"], data["scores"]) ]
        score_fields = [ self.normalize_score_fields(score_field) for score_field in data["score_fields"] ]
        inputs = [ ma.concatenate([field_indexes[i], scores[i], score_fields[i]]) for i in range(len(scores)) ]
        outputs = self.normalize_final_scores(data["outputs"])
        super().train(inputs, outputs)

    # make a prediction of output based on input
    def predict(self, data, index = 0):
        field_index = self.to_categorical(15, data["field_index"])
        score = self.normalize_score(data["field_index"], data["score"])
        score_fields = self.normalize_score_fields(data["score_fields"])

        input_tensor = ma.concatenate([field_index, score, score_fields])
        predicted_output = self.model.predict(input_tensor.reshape(-1, self.num_inputs))[0][index]
        return predicted_output

    # returns the best move in the form [field_index, score]
    def decide_score_logging(self, score_fields, possible_moves):
        max_value = 0
        best_move = possible_moves[0]

        for move in possible_moves:
            inputs = {
                "field_index" : move[0],
                "score" : move[1],
                "score_fields" : score_fields[:6],
            }
            value = self.predict(inputs)

            if value > max_value:
                max_value = value
                best_move = move

        return best_move
  
    def save_model(self):
        return super().save_model('ScoreLogModel')

    def load_model(self):
        return super().load_model('ScoreLogModel')
