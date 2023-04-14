from helpers import Helpers
import numpy as np
import numpy.ma as ma
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from keras.models import load_model
import abc

class Model:
    def __init__(self, num_inputs, num_outputs):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

    def _fit(self, inputs, outputs):
        inputs = np.array(inputs, dtype='float32').reshape(-1, self.num_inputs)
        outputs = np.array(outputs).reshape(-1, self.num_outputs)
        self.model.fit(inputs, outputs, verbose=0, epochs=75, batch_size=64)

    def _predict(self, input):
        return self.model.predict(input.reshape(-1, self.num_inputs), verbose=0)[0][0]

    @abc.abstractmethod
    def _compile_model(self):
        pass

    def prepare(self, config):
        if config['load']:
            self.model = load_model('data/' + self.name + '.h5')
        self._compile_model()

    def finish(self, config):
        if config['save']:
            self.model.save('data/' + self.name + '.h5')

    # turns a value into a one-hot, like for the dice value 2, the func
    # call would be to_categorical(6, 1) with return val [0, 1, 0, 0, 0, 0]
    def _to_categorical(self, num_classes, category):
        return ma.masked_array(tf.keras.utils.to_categorical(category, num_classes=num_classes, dtype=int))

    def _categorize_field_idx(self, field_idx):
        return self._to_categorical(15, field_idx)
    
    def _categorize_reroll_num(self, reroll_num):
        return self._to_categorical(2, reroll_num)

    def _categorize_die(self, dices):
        categ_dices = ma.masked_array([])
        for dice in dices:
            categ_dices = np.ma.concatenate([categ_dices, self._to_categorical(6, dice - 1)])
        return categ_dices

    def _normalize_score_fields(self, score_fields):
        return ma.masked_array([ score_fields.data[idx] / Helpers.max_scores[idx] for idx in range(len(score_fields)) ])

# Model predicting game final score for logging the score in a
# specific field with a certain set of die
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
#   * (15) available score card fields as boolean values
#   * (2) reroll number as one-hot value [1, 0] / [0, 1]
#   * (1) bonus is reached as one boolean value
#   * (5) dice indexes thrown as boolean values 
# output:
#   * (1) normalized prediction of game final score
class RerollModel(Model):
    def __init__(self):
        super().__init__(53, 1)
        self.name = 'RerollModel'
        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=160, activation='relu'), # 3N + 1
            Dense(units=120, activation='relu'),
            Dense(units=80, activation='relu'),
            Dense(units=40, activation='relu'),
            Dense(units=10, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])
    
    def _compile_model(self):
        opt = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=['mae'])

    def decide_reroll(self, score_fields, dices, reroll_num):
        #print("decide_reroll()")
        dices = self._categorize_die(dices)
        avail_sc_fields = [ 1 if Helpers.field_available(score_fields, i) else 0 for i in range(len(score_fields)) ]
        reroll_num = self._to_categorical(2, reroll_num - 1)
        bonus = [1] if Helpers.bonus_reached(score_fields) else [0]

        input = ma.masked_array(np.concatenate([dices, avail_sc_fields, reroll_num, bonus]))

        best_prediction = 0
        best_reroll_idxs = []
        for i in range(2**5):
            reroll_idxs_str = bin(i)[2:].zfill(5)
            reroll_idxs = [int(digit) for digit in reroll_idxs_str]
            #print("decide_reroll()::", reroll_idxs)
            tmp_input = ma.masked_array(np.concatenate([input, reroll_idxs]))
            
            prediction = self._predict(tmp_input)

            if prediction > best_prediction:
                best_prediction = prediction
                best_reroll_idxs = reroll_idxs

        return best_reroll_idxs

    def train(self, history):
        #print("RerollModel::train()")
        inputs = []
        outputs = []

        data = history.get_reroll_data()
        for i in range(len(data["reroll_num"])):
            dices = self._categorize_die(data["dices"][i])
            avail_sc_fields = ma.masked_array( data["avail_sc_fields"][i] )
            reroll_num = self._categorize_reroll_num(data["reroll_num"][i])
            bonus = ma.masked_array([ data["bonus_reached"][i] ])
            idxs_rerolled = ma.masked_array( data["dice_idx_rerolled"][i] )

            '''
            print("dices", dices)
            print("avail_sc_fields", avail_sc_fields)
            print("reroll_num", reroll_num)
            print("bonus", bonus)
            print("idxs_rerolled", idxs_rerolled)
            print()
            '''

            input = ma.masked_array(np.concatenate([dices, avail_sc_fields, reroll_num, bonus, idxs_rerolled]))
            input.mask = [False] * len(input)
            output = [ data["outputs"][i] ]

            inputs.append(input)
            outputs.append(output)

        self._fit(input, output)

# Model predicting game final score for logging the score in a
# specific field with a certain set of die
# input: 
#   * (30) 5 die as one-hot values: [d1, d2, d3, d4, d5] * [x, x, x, x, x, x]
#   * (15) normalized score card
#   * (1) boolean: if bonus has been reached
#   * (1) normalized score to log 
#   * (15) field to log the score in as one-hot value: [x, * 15]
# output:
#   * (1) normalized prediction of game final score if score is logged in that field
class ScoreLogModel(Model):
    def __init__(self):
        super().__init__(62, 1) 
        self.name = 'ScoreLogModel'
        # TODO: consider dropout layers to prevent overfitting?
        self.model = Sequential([
            Dense(units=self.num_inputs, input_shape=(self.num_inputs,), activation='relu'),
            Dense(units=187, activation='relu'), # 3N + 1
            Dense(units=140, activation='relu'),
            Dense(units=100, activation='relu'),
            Dense(units=60, activation='relu'),
            Dense(units=20, activation='relu'),
            Dense(units=10, activation='relu'),
            Dense(units=self.num_outputs, activation='linear'),
        ])

    def _compile_model(self):
        opt = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=['mae'])

    # returns the best move in the form [field_index, score]
    def decide_score_logging(self, score_fields, dices):
        '''
        print("decide_score_logging()")
        print("dices", dices)
        print("scores", scores)
        '''
        categ_dices = self._categorize_die(dices)
        scores = self._normalize_score_fields(score_fields)
        bonus = [1] if Helpers.bonus_reached(score_fields) else [0]
        input = ma.masked_array(np.concatenate([categ_dices, scores, bonus]))

        best_prediction = -1
        best_field_idx = 0
        for field_idx in range(len(score_fields)):
            if not Helpers.field_available(score_fields, field_idx):
                continue

            score = [ Helpers.count_score(dices, field_idx) / Helpers.max_scores[field_idx] ]
            categ_field_idx = self._to_categorical(15, field_idx)
            tmp_input = ma.masked_array(np.concatenate([input, score, categ_field_idx]))

            prediction = self._predict(tmp_input)
            '''
            print("score:", Helpers.count_score(dices, field_idx), "on", Helpers.idx_to_name(field_idx)) 
            print("prediction", prediction, "best:", best_prediction)
            print("---")
            '''

            if prediction > best_prediction:
                best_prediction = prediction
                best_field_idx = field_idx

        return best_field_idx

    # train model with inputs and outputs from one game
    def train(self, history):
        #print("ScoreLogModel::train()")
        inputs = []
        outputs = []

        data = history.get_score_log_data()
        for i in range(len(data["dices"])):
            dices = self._categorize_die(data["dices"][i])
            score_fields = ma.masked_array(self._normalize_score_fields(data["score_cards"][i]))
            bonus = ma.masked_array([ 1 if data["bonus_reached"][i] else 0 ])
            score = ma.masked_array([ data["scores"][i] / Helpers.max_scores[data["field_idxs"][i]] ])
            field_idx = self._categorize_field_idx(data["field_idxs"][i])
 
            '''
            print("dices", dices)
            print("score_fields", score_fields)
            print("bonus", bonus)
            print("score", score)
            print("field_idx", field_idx)
            print("")
            '''

            input = ma.masked_array(np.concatenate([dices, score_fields, bonus, score, field_idx]))
            input.mask = np.ma.concatenate([[False] * len(dices),
                                            [False] * len(score_fields),
                                            [False],
                                            [False],
                                            [False] * len(field_idx)],
                                            axis=0)
            output = [ data["outputs"][i] / Helpers.max_score ]
            
            inputs.append(input)
            outputs.append(output)
        self._fit(input, output)