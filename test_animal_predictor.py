import predict_animal_on_model

Predictor = predict_animal_on_model.AnimalPredictor()

test_strings = {}
print(Predictor.name_dict.keys())

test_strings.update({'bass': 'fish freshwater marine black spotted'})
test_strings.update({'cat': 'domestic animal pet small long tail nine lives bad luck'})
test_strings.update({'penguin': 'black and white happy feet movie'})
test_strings.update({'reindeer': 'santa claus north big antlers'})

for key in test_strings:
    found = False
    number_of_guesses = 1
    guessed_animals = []
    while not found:
        result = Predictor.get_prediction_ranking_exclude_wrong_animals(test_strings.get(key), guessed_animals)
        print(result)
        prediction = list(result.keys())[0]
        if prediction == key:
            found = True
            print("found correct animal based on string after attempt: " + str(number_of_guesses))
            print('prediction = ' + prediction + ', with a certitude of: ' + str(int(result.get(prediction))) + '%')
        else:
            number_of_guesses = number_of_guesses + 1
            guessed_animals.append(prediction)






# test_strings = []
# test_strings.append("bird")
# test_strings.append("pink bird")
# test_strings.append("pink bird one foot")
# test_strings.append("pink bird one foot africa")
#
# for test in test_strings:
#     print(test)
#     print(Predictor.get_prediction_ranking(test))
#     print("-------")
#
# test_strings = []
# test_strings.append("bird")
# test_strings.append("black and white bird")
# test_strings.append("black and white bird south pole")
# test_strings.append("black and white bird south pole lives in colonies")
# test_strings.append("black and white flightless bird south pole lives in colonies")
# test_strings.append("Southern Hemisphere cold climates such as Antarctica south flightless colonies movie happy feet emperor king")
#
# guessed_animals = []
#
# for test in test_strings:
#     print(test)
#     result1 = Predictor.get_prediction_ranking_exclude_wrong_animals(test, guessed_animals)
#     print(result1)
#     result2 = Predictor.get_prediction_ranking(test)
#     print(result2)
#     guessed_animals.append(list(result1.keys())[0])
#     print("-------")