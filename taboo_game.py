#Import wikipedia library
import wikipedia
from Func import remove_words, taboo_words, find_similarity
from Recorder import recognize_speech_from_mic, SpeakText 
#Import english stop words to be removed
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
#Import NLP library for Term Frequency times Inverse Document Frequency
#So that the length of the description has no impact on the average count
#and in order to downscale weights for words that occur in many descriptions
from sklearn.feature_extraction.text import TfidfVectorizer
import inflect
import random
import speech_recognition as sr

#Add animals you want to add to the dictionary to test your description 
#NOT all wiki pages are one on one to be found by the animal name
animals = ['Wolf', 'Panda', 'Kangaroo', 'Elephant', 'Penguin']
animals2 = ['Antelope', 'Bison', 'Cheetah', 'Dolphin', 'Elephant',
                  'Giraffe', 'Cat', 'Gorilla', 'Hamster',
                  'Leopard', 'Lion', 'Lynx', 'Platypus', 'Raccoon', 'Reindeer', 'Squirrel','Wolf']

library_map = {}

print('Loading data from wikipedia...')
for animal in animals2:
    temp = wikipedia.page(animal)
    print(temp.url)
    print(temp.title)
    temp_content = remove_words(temp.content, ENGLISH_STOP_WORDS)
    library_map.update({animal:temp_content})


#Create the transformation
vectorizer = TfidfVectorizer()
#Built vocabulary from wikipedia library on selected subjects
#All words that are part of the wikipedia pages (except removed stop words) should have a place in the vector representation
vectorizer = vectorizer.fit(library_map.values())


filtered_text = {}

#Clean the wikipedia description
for item in library_map:
    temp_obj = library_map.get(item)
    temp_obj = temp_obj.replace(",", "").replace(".", "") #Remove dot and commas
    temp_obj = temp_obj.replace("(", "").replace(")", "") #Remove parentheses
    temp_obj = temp_obj.replace(item.lower(),"") #Remove the animal name
    engine = inflect.engine()
    plural = engine.plural(str(item))
    words_to_remove = list(ENGLISH_STOP_WORDS) #Remove stopwords    
    words_to_remove.extend(['-', '==', '====', '–', '===']) #Remove Wikipedia delimiters
    words_to_remove.extend([str(item), str(item.lower())]) #Remove the animal
    words_to_remove.extend([str(plural), str(plural.lower())]) #Remove the plural of the animal
    words_to_remove.extend(["s", "s'", "'s"]) #Remove english linking s'
    words_to_remove.extend(['species', 'specie', 'animal', 'animals']) #Remove unnecessary description (the whole list contains animals)
    temp_obj = remove_words(temp_obj, words_to_remove)
    #Store all cleaned descriptions in a dictionary
    filtered_text.update({item:temp_obj})


 #Above a vector is built for all vocabulary in the selected wikipedia pages
#However, now we want a vector for each subject seperately so we can compare new description of a 
#specific animal with the different wiki-pages
vector_dictionary = {}

for item in filtered_text:
    text = filtered_text.get(item)
    #Remove Taboo words
    description = remove_words(text, taboo_words(filtered_text, item))
    vector_dictionary.update({item:vectorizer.transform([description])})

SpeakText('Hi, welcome to Taboo game! Please pick a card.')
card = random.choice(animals2)
word1 = taboo_words(filtered_text, card)[0]
word2 = taboo_words(filtered_text, card)[1]
word3 = taboo_words(filtered_text, card)[2]
print('The card you have to make the agent guess is a ' + card + ' and you cannot say the words: ' + word1 + ', ' + word2 + ' and ' + word3+ '.')
SpeakText('The card you have to make the agent guess is a ' + card + ' and you cannot say the words ' + word1 + ' ' + word2 + ' and ' + word3)
SpeakText("Let's play!")

#Create recognizer and mic instances
recognizer = sr.Recognizer()
microphone = sr.Microphone()

NUM_GUESSES = 3
PROMPT_LIMIT = 5

memory_guess = []
guess_turn=0

print('Describe!')
SpeakText('Describe!')
for j in range(PROMPT_LIMIT):
    description = recognize_speech_from_mic(recognizer, microphone)
    if description["transcription"]:
        break
    if not description["success"]:
        break
    print("I didn't catch that. What did you say?")
    SpeakText("I didn't catch that. What did you say?")


for i in range(NUM_GUESSES):
    
# if there was an error, stop the game
    if description["error"]:
        print("ERROR: {}".format(description["error"]))
        break

# show the user the transcription
    print("You said: {}".format(description["transcription"]))
        
    #find the similarity percentage
    guess = find_similarity(vectorizer.transform([description["transcription"]]), vector_dictionary)
    
    #retrieve the sorted list with the first item having the highest similarity percentage
    list_guess = list(guess.keys())
        
    #if the first item has already been proposed, propose the second one 
    if list_guess[0] in memory_guess:
        guess_turn = list_guess[1]
        print('Is it a {}?'.format(list_guess[1]))
        SpeakText('Is it a {}?'.format(list_guess[1]))
    else:
        guess_turn = list_guess[0]
        print('Is it a {}?'.format(list_guess[0]))
        SpeakText('Is it a {}?'.format(list_guess[0]))
    
    memory_guess.append(guess_turn)

    
    for j in range(PROMPT_LIMIT):
        print('Waiting for your answer: ')
        answer = recognize_speech_from_mic(recognizer, microphone)
        if answer["transcription"]:
            break
        if not answer["success"]:
            break
        print("I didn't catch that. What did you say?")
        SpeakText("I didn't catch that. What did you say?")

        # if there was an error, stop the game
    if answer["error"]:
        print("ERROR: {}".format(answer["error"]))
        break

    # show the user the transcription
    print("{}".format(answer["transcription"])) 

    # determine if guess is correct and if any attempts remain
    guess_is_correct = answer["transcription"] == 'yes'
    agent_has_more_attempts = i < NUM_GUESSES - 1

    # determine if the user has won the game
    # if not, repeat the loop if user has more attempts
    # if no attempts left, the user loses the game
    if guess_is_correct:
        print("Correct! I won!")
        SpeakText("Correct! I won!")
        break
    elif agent_has_more_attempts:
        if answer["transcription"]:
            #if not correct and agent has more attempts, add the additional information provided after the 'no'
            more_info = answer["transcription"].split()
            #The first word of the answer will be 'no', so we don't take it and start with the second word
            add_more_info = " ".join(more_info[1:])
            description["transcription"] = description["transcription"] + " " + add_more_info
        print("Incorrect. Ok I'll try again.")
        SpeakText("Incorrect. Ok I'll try again.")
    else:
        print("Oh I lost.")
        SpeakText("Oh I lost.")
        break
