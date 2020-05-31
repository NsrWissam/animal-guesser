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


def get_proba_per_model(test_phrase, models):
    for model in models:
        i=0
        for probab in model.predict_proba(test_phrase)[0]:
            print(list(name_dict.keys())[i]+ ": " + str(round(probab*100,2)) + " %")
            i = i+1
        print("")


def get_prediction_ranking(test_prhase, models_with_proba, models_wo_proba):
    models_prob = np.zeros(len(list(name_dict.keys())))
    for model in models_with_proba:
        values = list(model.predict_proba(test_prhase)[0])
        models_prob = models_prob + values

    for model in models_wo_proba:
        animal = model.predict(test_prhase)
        models_prob[animal] = models_prob[animal] + 0.03

    probab_tot = dict(zip(list(name_dict.keys()), models_prob))
    ranking = sorted(probab_tot.items(), key=lambda x: x[1], reverse=True)
    som = 0
    for i in range(0, 5):
        som = som + ranking[i][1]

    ranking_dict = {}
    for i in range(0, 5):
        ranking_dict.update({ranking[i][0]: ranking[i][1]/som*100})

    return ranking_dict


test_strings = []
test_strings.append("bird")
test_strings.append("pink bird")
test_strings.append("pink bird one foot")
test_strings.append("pink bird one foot africa")

for test in test_strings:
    print(test)
    transformed = vectorizer.transform([test]).todense()
    print(get_prediction_ranking(transformed, [model3, model5], [model4]))
    print("")
    print("-------")

test_strings = []
test_strings.append("bird")
test_strings.append("black and white bird")
test_strings.append("black and white bird south pole")
test_strings.append("black and white bird south pole lives in colonies")
test_strings.append("black and white flightless bird south pole lives in colonies")
test_strings.append("Southern Hemisphere cold climates such as Antarctica south flightless colonies movie happy feet emperor king")

# The largest living species is the emperor penguin (Aptenodytes forsteri):[1] on average, adults are about 1.1 m (3 ft 7 in) tall and weigh 35 kg (77 lb). The smallest penguin species is the little blue penguin (Eudyptula minor), also kn

for test in test_strings:
    print(test)
    transformed = vectorizer.transform([test]).todense()
    print(get_prediction_ranking(transformed, [model3, model5], [model4]))
    print("")
    print("-------")


