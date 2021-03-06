import keras

from P300Net.data_preparation import create_data_rep_training, triplet_data_generator_no_dict, \
    get_number_of_samples_per_epoch_batch_mode, train_and_valid_generator

from experiments.P300_RSVP.common import *
from sklearn.utils import shuffle
from keras import backend as K
from keras.models import Model
import scipy

__author__ = 'ORI'

from sys import platform

is_local = True
if platform != "win32":
    is_local = False

import numpy as np
import os
from scipy import stats

rng = np.random.RandomState(42)
from os.path import basename

this_file_names = basename(__file__).split('.')[0]
print (this_file_names)



if is_local:
    data_base_dir = r'C:\Users\ORI\Documents\Thesis\dataset_all'
    experiments_dir = r'C:\Users\ORI\Documents\Thesis\expreiment_results'

else:
    data_base_dir = r'/data_set'
    experiments_dir = r'/results'


def get_only_P300_model(eeg_sample_shape):
    digit_input = Input(shape=eeg_sample_shape)
    x = Flatten(input_shape=eeg_sample_shape)(digit_input)
    x = Dense(40,activation='relu')(x)
    x = Dense(40,activation='relu')(x)
    out = Dense(1, activation='tanh')(x)
    # out = Activation('tanh')(x)


    model = Model(digit_input, out)
    return model


def get_only_P300_model_LSTM(eeg_sample_shape):
    digit_input = Input(shape=eeg_sample_shape)
    # x = Flatten(input_shape=eeg_sample_shape)(digit_input)
    x = LSTM(40,input_shape=eeg_sample_shape,return_sequences=True)(digit_input)
    x = LSTM(40, return_sequences=False)(x)
    # x = Dense(40,activation='relu')(x)
    out = Dense(1, activation='tanh')(x)
    # out = Activation('tanh')(x)


    model = Model(digit_input, out)
    return model

def get_P300_model(only_P300_model, select):
    model = only_P300_model

    def identity_loss_v3(y_true, y_pred):
        y_true_reshaped = K.mean(K.reshape(y_true, (-1, select, 30)), axis=1)
        y_pred_reshaped = K.softmax(K.mean(K.reshape(y_pred, (-1, select, 30)), axis=1))
        final_val = K.mean(K.categorical_crossentropy(y_true_reshaped, y_pred_reshaped))
        return final_val + y_pred * 0

    model.compile(optimizer='rmsprop',
                  loss=identity_loss_v3)
    return model



if __name__ == "__main__":

    all_subjects = ["RSVP_Color116msVPpia.mat","RSVP_Color116msVPpia.mat","RSVP_Color116msVPpia.mat","RSVP_Color116msVPpia.mat","RSVP_Color116msVPpia.mat"];

    for experiment_counter, subject in enumerate(all_subjects):

        file_name = os.path.join(data_base_dir, subject)
        all_data_per_char, target_per_char, train_mode_per_block, all_data_per_char_as_matrix, target_per_char_as_matrix = create_data_rep_training(
            file_name, -200, 800, downsampe_params=8)

        batch_size = 80
        select = 3
        data_generator_batch = triplet_data_generator_no_dict(all_data_per_char_as_matrix[train_mode_per_block == 1],
                                                              target_per_char_as_matrix[train_mode_per_block == 1],
                                                              batch_size=batch_size, select=select, debug_mode=False)





        from keras.models import Sequential

        from keras.layers import merge, Input, Dense, Flatten, Activation, Lambda, LSTM

        eeg_sample_shape = (25, 55)
        only_p300_model_1 = get_only_P300_model(eeg_sample_shape)

        model = get_P300_model(only_p300_model_1, select=select)
        print "after compile"




        # in order to make sure the gradient is also the same, I'm checking the weight of the model
        # for i in range(20):
        #     train_data = data_generator_batch.next()
        #     print i
        test_tags = target_per_char_as_matrix[train_mode_per_block != 1]

        test_data = all_data_per_char_as_matrix[train_mode_per_block != 1].reshape(-1,
                                                                                   all_data_per_char_as_matrix.shape[2],
                                                                                   all_data_per_char_as_matrix.shape[3])

        class LossHistory(keras.callbacks.Callback):
            def on_batch_end(self, batch, logs={}):

                all_prediction_P300Net = model.predict(stats.zscore(test_data, axis=1).astype(np.float32))
                actual = np.argmax(np.mean(all_prediction_P300Net.reshape((-1, 10, 30)), axis=1), axis=1);
                gt = np.argmax(np.mean(test_tags.reshape((-1, 10, 30)), axis=1), axis=1)
                accuracy = np.sum(actual == gt) / float(len(gt))
                print "\n*mid****accuracy: {}\n".format(accuracy)


        history = LossHistory()

        model.fit_generator(data_generator_batch,36000, 20,callbacks=[history]) # train_on_batch(train_data[0], train_data[1])




        print ("stam")
        all_prediction_P300Net = model.predict(stats.zscore(test_data, axis=1).astype(np.float32))




        all_prediction_P300Net = model.predict(stats.zscore(test_data, axis=1).astype(np.float32))
        actual = np.argmax(np.mean(all_prediction_P300Net.reshape((-1, 10, 30)), axis=1), axis=1);
        gt = np.argmax(np.mean(test_tags.reshape((-1, 10, 30)), axis=1), axis=1)
        accuracy = np.sum(actual == gt) / float(len(gt))
        print "accuracy: {}".format(accuracy)







        print ("temp")
