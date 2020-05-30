from sklearn.feature_extraction.text import TfidfVectorizer
import random
import numpy as np

from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

import pickle

model1 = KNeighborsClassifier()
model2 = RandomForestClassifier()
model3 = LogisticRegression()
model4 = LinearSVC()
model5 = MLPClassifier()

# model1 = pickle.load(open("trained_models_wiki/model1_KNC.p", "rb"))
# model2 = pickle.load(open("trained_models_wiki/model2_RFC.p", "rb"))
model3 = pickle.load(open("trained_models_wiki/model3_LGC.p", "rb"))
model4 = pickle.load(open("trained_models_wiki/model4_LSVC.p", "rb"))
model5 = pickle.load(open("trained_models_wiki/model5_MLPC.p", "rb"))

name_dict = pickle.load(open("trained_models_wiki/name_dict.p", "rb"))
vectorizer = pickle.load(open("trained_models_wiki/tfidvector.p", "rb"))


def get_prediction_ranking_2(test_phrase, models):
    # TODO
    results_tot = np.zeros(len(name_dict.keys()))
    for model in models:
        prediction = model.predict_proba(test_phrase)[0]
        for j in range(1, 6):
            i = 0
            highest = 0
            index = 0
            for probab in prediction:
                if probab > highest:
                    highest = probab
                    index = i
                i = i + 1
            prediction[index] = 0
            results_tot[index] = results_tot[index] + (6 - j)
    ranking = {}
    for j in range(1, 6):
        i = 0
        highest = 0
        index = 0
        for result in results_tot:
            if result > highest:
                highest = result
                index = i
            i = i + 1
        results_tot[index] = 0
        ranking.update({list(name_dict.keys())[index]: highest})

    return ranking


test = vectorizer.transform(["pink bird one foot"]).todense()
print(get_prediction_ranking_2(test, [model3, model5]))
print(list(name_dict.keys())[int(model4.predict(test))])

test = vectorizer.transform(["lobster river"]).todense()
print(get_prediction_ranking_2(test, [model3, model5]))
print(list(name_dict.keys())[int(model4.predict(test))])

test = vectorizer.transform(["black and white bird"]).todense()
print(get_prediction_ranking_2(test, [model3, model5]))
print(list(name_dict.keys())[int(model4.predict(test))])

test = vectorizer.transform(["cat"]).todense()
print(get_prediction_ranking_2(test, [model3, model5]))
print(list(name_dict.keys())[int(model4.predict(test))])

print(list(name_dict.keys()))


