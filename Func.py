import operator
import collections
import inflect
#Import english stop words to be removed
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
#Import NLP library for Term Frequency times Inverse Document Frequency
#So that the length of the description has no impact on the average count
#and in order to downscale weights for words that occur in many descriptions
from sklearn.feature_extraction.text import TfidfVectorizer
#Import the NLP library for finding cosine similarities between descriptions
from sklearn.metrics.pairwise import cosine_similarity as cossim
 #Import the SpeechRecognition library for the player to describe the word to be guessed

 #Define a function to easily remove words from wikipedia description
def remove_words(wordstr, words_to_remove):
    querywords = wordstr.split()

    resultwords  = [word for word in querywords if word.lower() not in words_to_remove]
    return ' '.join(resultwords)

 #Select the Taboo words, the top 3 occuring words in each description
def taboo_words(filtered_text, animal):
    counts = dict()
    engine = inflect.engine()
    selected_words = []
    to_remove = []
    full_text = filtered_text.get(animal)
    words = full_text.split()
    #Compute the most recurring words in the description
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    #Sort the dictionary to get the top three recurring words at the top
    sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = collections.OrderedDict(sorted_counts)
    #Remove words with less than 2 characters (often missplit alone letters or numbers)
    for w in list(sorted_dict.keys()):
        #w.split()
        if len(w)>2:
            selected_words.append(w)
    #Words appearing a lot in all descriptions
    to_remove.extend(['areas', 'years', 'males', 'females', 'used', 'occur'])
    selected_words = [w for w in selected_words if w.lower() not in to_remove]
    #Take the top 3 words
    return selected_words[:3]

#Function that gives as answer the item with the highest similarity percentage
def find_similarity(description, vector_dictionary):
    similarities = {}
    perc = {}
    total = 0
    #Compute cosine similarities
    for item in vector_dictionary:
        temp_sim = cossim(vector_dictionary.get(item).toarray(),description.toarray())
        similarities.update({item:temp_sim})
        total = total + temp_sim
    #Compute similarities as percentage 
    for item in similarities:
        perc.update({item:int(similarities.get(item)/total*100)})
    #Sort dic by items with highest similarity percentage  
    sorted_perc = sorted(perc.items(), key=operator.itemgetter(1), reverse=True)
    sorted_dict = dict(sorted_perc)

  
    return sorted_dict