# import data from elasticsearch database and train model

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from sklearn.feature_extraction.text import TfidfVectorizer
import random
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import pickle

es = Elasticsearch(hosts=["https://70fa05be281c4ff8977b2a9e557f7690.westeurope.azure.elastic-cloud.com:9243/"],
                   http_auth=("elastic", "dpucymmIkDh7iOMjbUFFaRqA"))


# load only wiki data from elasticsearch database
def load_wiki_data_to_lib():
    data_dump = helpers.scan(es, query={"query": {"match_all": {}}}, scroll='1m', index='zoo_v4')  # like others so far
    for animal_data in data_dump:
        an_label = animal_data['_source']['name']
        an_info = animal_data['_source']['wiki']
        library_map_wiki.update({an_label: an_info})


# load only zoo data from elasticsearch database
def load_zoo_data_to_lib():
    data_dump = helpers.scan(es, query={"query": {"match_all": {}}}, scroll='1m', index='zoo_v4')
    for animal_data in data_dump:
        an_label = animal_data['_source']['name']
        an_info = animal_data['_source']['words']
        separator = ' '
        an_info_str = separator.join(an_info)
        library_map_zoo.update({an_label: an_info_str})


# load zoo data and wiki data from database
def load_all_data_to_lib():
    data_dump = helpers.scan(es, query={"query": {"match_all": {}}}, scroll='1m', index='zoo_v4')
    for animal_data in data_dump:
        an_label = animal_data['_source']['name']
        an_info_wiki = animal_data['_source']['wiki']
        an_info_zoo = animal_data['_source']['words']
        separator = ' '
        an_info_zoo_str = ' ' + separator.join(an_info_zoo)
        library_map_all.update({an_label: an_info_wiki + an_info_zoo_str})


# translate all words in database towards a vector with tfidvectorizer
def create_vectorizer(dictionary):
    # create the transformation
    vectorizer = TfidfVectorizer()
    # built vocabulary from wikipedia library on selected subjects -> all words that are part of the wikipedia pages (except removed stop words) should have a place in the vector representation
    vectorizer = vectorizer.fit(dictionary.values())
    return vectorizer


def create_name_dict(dictionary):
    count = 0
    name_dict_temp = {}
    for item in dictionary.keys():
        name_dict_temp.update({item: count})
        count = count + 1
    return name_dict_temp


def create_training_xy(dictionary, split_rate):
    print("start creating training data")
    training_xy = []
    # split_rate = 20
    name_dict = create_name_dict(dictionary)
    vectorizer = create_vectorizer(dictionary)
    for item in dictionary:
        # print("split up data of: " + item)
        animal_info = dictionary.get(item)
        number_of_words = len(animal_info.split()) / split_rate
        # print("the lengt of the wordlist for 1 training example = " + str(
           # number_of_words) + ', the total amount of words is: ' + str(len(animal_info.split())))
        count = 0
        new_string = ""
        for word in animal_info.split():
            if count > number_of_words - 2:
                training_xy.append([vectorizer.transform([new_string]), name_dict.get(item)])
                count = 0
                # print(new_string.split()[0:100])
                # print("           ")
                new_string = ""
            else:
                new_string = new_string + word + " "
                count = count + 1
    return training_xy


def get_X_y_training(training_lib):
    # shuffle training set (because dataset is ordered)
    random.shuffle(training_lib)

    training_x = []
    training_y = []

    # after shuffling, split data in X and y values
    for features, label in training_lib:
        training_x.append(features)
        training_y.append(label)

    x_train = np.array(training_x)
    y_train = np.array(training_y)

    columns = x_train[1].todense().shape[1]
    rows = x_train.shape[0]

    x_train_dense = np.zeros((rows, columns))
    for i in range(0, rows):
        x_train_dense[i] = x_train[i].todense()

    return x_train_dense, y_train


def train_models(models, X, y):
    print("-----")
    for model in models:
        model.fit(X, y)
        print("model trained_models_wiki")


# #########################
# Main program
# #########################

# test correctly loaded data
#print(library_map_all.get("wolf"))

library_map_wiki = {}
library_map_zoo = {}
library_map_all = {}

load_zoo_data_to_lib()
load_wiki_data_to_lib()
load_all_data_to_lib()

training_data = create_training_xy(library_map_wiki, 10)

X, y = get_X_y_training(training_data)

# model1 = KNeighborsClassifier()
# model2 = RandomForestClassifier()
model3 = LogisticRegression()
model4 = LinearSVC()
model5 = MLPClassifier()
#
train_models([model3, model4, model5], X, y)
#
# print(model1.score(X, y))
# print(model2.score(X, y))
print(model3.score(X, y))
print(model4.score(X, y))
print(model5.score(X, y))
#
# pickle.dump(model1, open("trained_models_wiki/model1_KNC.p", "wb"))
# pickle.dump(model2, open("trained_models_wiki/model2_RFC.p", "wb"))
pickle.dump(model3, open("trained_models_wiki/model3_LGC.p", "wb"))
pickle.dump(model4, open("trained_models_wiki/model4_LSVC.p", "wb"))
pickle.dump(model5, open("trained_models_wiki/model5_MLPC.p", "wb"))

pickle.dump(create_name_dict(library_map_wiki), open("trained_models_wiki/name_dict.p", "wb"))
vectorizer = TfidfVectorizer()
vectorizer = vectorizer.fit(library_map_wiki.values())
pickle.dump(vectorizer, open("trained_models_wiki/tfidvector.p", "wb"))