from sklearn.feature_extraction.text import TfidfVectorizer
import random
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression

import pickle


class AnimalPredictor():
    def __init__(self):
        self.model3 = LogisticRegression()
        self.model4 = LinearSVC()
        self.model5 = MLPClassifier()

        self.loading_dir = 'trained_models_clean/'

        self.model3 = pickle.load(open(self.loading_dir + "model3_LGC.p", "rb"))
        self.model4 = pickle.load(open(self.loading_dir + "model4_LSVC.p", "rb"))
        self.model5 = pickle.load(open(self.loading_dir + "model5_MLPC.p", "rb"))

        self.name_dict = pickle.load(open(self.loading_dir + "name_dict.p", "rb"))
        self.vectorizer = pickle.load(open(self.loading_dir + "tfidvector.p", "rb"))

        self.models_with_proba = [self.model3, self.model5]
        self.models_wo_proba = [self.model4]

    def tranfsform_string_to_vec(self, word_string):
        transformed_vec = self.vectorizer.transform([word_string]).todense()
        return transformed_vec

    def get_prediction_ranking(self, test_phrase_string):
        test_phrase_vec = self.tranfsform_string_to_vec(test_phrase_string)
        models_prob = np.zeros(len(list(self.name_dict.keys())))
        for model in self.models_with_proba:
            values = list(model.predict_proba(test_phrase_vec)[0])
            models_prob = models_prob + values

        for model in self.models_wo_proba:
            animal = model.predict(test_phrase_vec)
            models_prob[animal] = models_prob[animal] + 0.03

        probab_tot = dict(zip(list(self.name_dict.keys()), models_prob))
        ranking = sorted(probab_tot.items(), key=lambda x: x[1], reverse=True)
        som = 0
        for i in range(0, 5):
            som = som + ranking[i][1]

        ranking_dict = {}
        for i in range(0, 5):
            ranking_dict.update({ranking[i][0]: ranking[i][1] / som * 100})

        return ranking_dict

    def get_prediction_ranking_exclude_wrong_animals(self, test_phrase_string, wrong_animals):
        test_phrase_vec = self.tranfsform_string_to_vec(test_phrase_string)
        models_prob = np.zeros(len(list(self.name_dict.keys())))
        for model in self.models_with_proba:
            values = list(model.predict_proba(test_phrase_vec)[0])
            models_prob = models_prob + values

        for model in self.models_wo_proba:
            animal = model.predict(test_phrase_vec)
            models_prob[animal] = models_prob[animal] + 0.03

        probab_tot = dict(zip(list(self.name_dict.keys()), models_prob))

        for animal_to_remove in wrong_animals:
            probab_tot.pop(animal_to_remove)
            print("guessed wrong: " + animal_to_remove)

        ranking = sorted(probab_tot.items(), key=lambda x: x[1], reverse=True)
        som = 0
        for i in range(0, 5):
            som = som + ranking[i][1]

        ranking_dict = {}
        for i in range(0, 5):
            ranking_dict.update({ranking[i][0]: ranking[i][1] / som * 100})

        return ranking_dict
