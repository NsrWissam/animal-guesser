# reference dataframe to elasticsearch : https://towardsdatascience.com/exporting-pandas-data-to-elasticsearch-724aa4dd8f62
import wikipedia
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import inflect

#Define settings with customized analyzer
settings = {
    "settings":{
          "analysis":{
            "analyzer":{
              "my_analyzer":{ 
               "type":"custom",
               "tokenizer":"standard",
               "filter":[
                  "lowercase",
                  "english_stop",
                  "porter_stem",
                  "english_possessive_stemmer"
               ]
            }
         },
         "filter":{
            "english_stop":{
               "type":"stop",
               "stopwords":"_english_"
            },
            "english_possessive_stemmer": {
                "type":"stemmer",
                "language":"possessive_english"
        }
         }
      }
   },
        "mappings": {
                "properties": {
                    "name": {
                        "type": "keyword"
                    },
                    "words": {
                        "type": "keyword"
                    },
                    "wiki": {
                        "type": "text",
                        "analyzer": "my_analyzer"
                    }
                }
            }
        }

def doc_generator(df):
    df_iter = df.iterrows()
    for index, document in df_iter:
        animal_name = document.animal
        dict_doc = document.to_dict()
        #del dict_doc["animal"]
        yield {
                "_index": 'zoo_raw',
                "_id" : f"{animal_name}",
                "_source": dict_doc,
            }
def remove_words(wordstr, words_to_remove):
  querywords = wordstr.split()
  resultwords  = [word for word in querywords if word.lower() not in words_to_remove]
  return ' '.join(resultwords)

df = pd.read_csv('zoo.data', names=['animal','hair','feathers','eggs','milk','airborne','aquatic','predator','toothed','backbone','breathes','venomous','fins','legs','tail','domestic','catsize','type'])
# Delete these row indexes from dataFrame
df.drop(df[df['animal'] == 'calf' ].index , inplace=True)
df.drop(df[df['animal'] == 'clam' ].index , inplace=True)
df.drop(df[df['animal'] == 'cavy' ].index , inplace=True)
df.drop(df[df['animal'] == 'crab' ].index , inplace=True)
df.drop(df[df['animal'] == 'dogfish' ].index , inplace=True)

animals = df.animal.tolist()
animals[2] = 'Bass (fish)'
animals[3] = 'bearr'
animals[5] = 'bison'
animals[12] = 'Corvus'
animals[13] = 'deerr'
animals[16] = 'duckk'
animals[20] = 'frogg'
animals[24] = 'goatt'
animals[29] = 'hares'
animals[42] = 'mole (animal)'
animals[53] = 'Pike fish'
animals[57] = 'Ferret'
animals[58] = 'Ponyy'
animals[60] = 'Cougar'
animals[61] = 'Felis catus'
animals[64] = 'Rhea (bird)'
animals[67] = 'Pinniped'
animals[70] = 'Chironex fleckeri'
animals[71] = 'skimmer (bird)'
animals[75] = 'sole (fish)'
animals[76] = 'House sparrow'
animals[85] = 'Tuna fish'
animals[86] = 'Vampire bat'
animals[92] = 'earthworm'

animal_names = df.animal.tolist()

library_map = {}

for i, animal in enumerate(animals):
  print(str(i) + ' - ' + animal)
  temp = wikipedia.page(animal)
  print(temp.url)
  print(animal_names[i])
  temp_content = remove_words(temp.content, ENGLISH_STOP_WORDS)
  library_map.update({animal_names[i]:temp_content})
  print('')

num2word = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
doc_df = pd.DataFrame(columns=['animal','words','wiki'])
for i, row in df.iterrows():
    animal_dict = dict.fromkeys(['animal','words', 'wiki'])
    animal_dict['animal'] = row['animal']
    animal_dict['words'] = []
    if row['hair']:
        animal_dict['words'].extend(['hair', 'hairy', 'fur','fury'])
    if row['feathers']:
        animal_dict['words'].extend(['feather'])
    if row['eggs']:
        animal_dict['words'].extend(['egg'])
    if row['milk']:
        animal_dict['words'].extend(['milk'])
    if row['airborne']:
        animal_dict['words'].extend(['airborne','fly', 'glide','float'])
    if row['aquatic']:
        animal_dict['words'].extend(['aquatic','water','swim','float'])
    if row['predator']:
        animal_dict['words'].extend(['predator','hunt','kill'])
    if row['toothed']:
        animal_dict['words'].extend(['tooth'])
    if row['backbone']:
        animal_dict['words'].extend(['backbone','vertebrate','spine'])
    else:
        animal_dict['words'].extend(['invertebrate'])
    if row['breathes']:
        animal_dict['words'].extend(['breath'])
    if row['venomous']:
        animal_dict['words'].extend(['venom','poison'])
    if row['fins']:
        animal_dict['words'].extend(['fin'])
    if row['legs']:
        if row['legs'] == 1:
            animal_dict['words'].extend([num2word[row['legs']]+' leg'])
        else: 
            animal_dict['words'].extend([num2word[row['legs']]+' legs'])
    if row['tail']:
        animal_dict['words'].extend(['tail'])
    if row['domestic']:
        animal_dict['words'].extend(['domestic'])
    if row['type']:
        if row['type'] == 1:
            animal_dict['words'].extend(['mammal'])
        if row['type'] == 2:
            animal_dict['words'].extend(['bird'])
        if row['type'] == 3:
            animal_dict['words'].extend(['reptile'])
        if row['type'] == 4:
            animal_dict['words'].extend(['fish'])
        if row['type'] == 5:
            animal_dict['words'].extend(['amphibian'])
        if row['type'] == 6:
            animal_dict['words'].extend(['bug','insect'])
        if row['type'] == 7:
            animal_dict['words'].extend(['invertibrate'])
    print("processing: " + row['animal'])
    temp_obj = library_map.get(row['animal']).replace(row['animal'].lower(),"")
    temp_obj = temp_obj.replace(",", "").replace(".", "")
    temp_obj = temp_obj.replace("(", "").replace(")", "") #Remove parentheses
    #engine = inflect.engine()
    #plural = engine.plural(str(row['animal']))
    #remove the animal name and all the stopwords from the wikipedia text
    words_to_remove = list(ENGLISH_STOP_WORDS) + [str(row['animal']), str(row['animal'].lower())] + row['animal'].split() + row['animal'].lower().split() 
    #words_to_remove.extend([str(plural), str(plural.lower())]) #Remove the plural of the animal
    #words_to_remove.extend(['-', '==', '====', '–', '===']) #Remove Wikipedia delimiters
    #words_to_remove.extend(["s", "s'", "'s"]) #Remove english linking s'
    #words_to_remove.extend(['species', 'specie', 'animal', 'animals', 'families', 'family']) #Remove unnecessary description (the whole list contains animals)
    temp_obj = remove_words(temp_obj, words_to_remove)
    animal_dict['wiki'] = temp_obj
    doc_df = doc_df.append(animal_dict,True)
    
es = Elasticsearch(hosts=["https://d4e3033cb97744efaf30d6fb0aa64dc9.europe-west1.gcp.cloud.es.io:9243"], http_auth=("elastic","M00PV83HRM8ozH9k6CrXU1wB"))

es.indices.create(index='zoo_raw', body=settings, ignore=400)
    
helpers.bulk(es, doc_generator(doc_df))
print(doc_generator(doc_df))
