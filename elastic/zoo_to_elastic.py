# reference dataframe to elasticsearch : https://towardsdatascience.com/exporting-pandas-data-to-elasticsearch-724aa4dd8f62
import pandas as pd
import sys
print(sys.path)
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def doc_generator(df):
    df_iter = df.iterrows()
    for index, document in df_iter:
        yield {
                "_index": 'zoo_v1',
                "_id" : f"{index}",
                "_source": document.to_dict(),
            }

zoo_names = ['animal','hair','feathers','eggs','milk','airborne','aquatic','predator','toothed','backbone','breathes','venomous','fins','legs','tail','domestic','catsize','type']
df = pd.read_csv('zoo.data', names=zoo_names)

num2word = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten'}
doc_df = pd.DataFrame(columns=['animal','words'])

for index, row in df.iterrows():
    animal_dict = dict.fromkeys(['animal','words'])
    
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
    doc_df = doc_df.append(animal_dict,True)

es = Elasticsearch(hosts=["https://70fa05be281c4ff8977b2a9e557f7690.westeurope.azure.elastic-cloud.com:9243/"], http_auth=("elastic","dpucymmIkDh7iOMjbUFFaRqA"))

#es.indices.create(index='zoo_v1', ignore=400)
    
helpers.bulk(es, doc_generator(doc_df))
