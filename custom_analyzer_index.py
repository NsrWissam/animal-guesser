import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import numpy as np
import json 
from operator import itemgetter

#Define the elasticsearch object
es = Elasticsearch(hosts=["https://70fa05be281c4ff8977b2a9e557f7690.westeurope.azure.elastic-cloud.com:9243/"], http_auth=("elastic","dpucymmIkDh7iOMjbUFFaRqA"))

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

#Function creating the index in elasticsearch
def create_index(es_object, index_name):
  created = False
  # index settings
  try:
      if not es_object.indices.exists(index_name):
          # Ignore 400 means to ignore "Index Already Exist" error.
          es_object.indices.create(index=index_name, body=settings, ignore=400)
          print('Created Index')
      created = True
  except Exception as ex:
      print(str(ex))
  finally:
      return created

#Get away trick to get the data by actually retrieving them from elasticsearch and storing them in a df
response = es.search(index='zoo_v2', body={}, size=94)
elastic_docs = response["hits"]["hits"]
#Get the words and wiki field
df_source = pd.concat(map(pd.DataFrame.from_dict, elastic_docs), axis=1)['_source'].T
df_source = df_source.reset_index(drop=True)
#Get the id field to get the name
df_idx = pd.DataFrame.from_dict(elastic_docs)['_id']
#Merge them together to get the final df with the animal name, the words and the wiki fields
df = pd.concat([df_idx, df_source], axis=1)

#############################################################
###### CREATION OF THE INDEX  WITH CUSTOMIZED ANALYZER ######
#############################################################

for index, content in df.iterrows():
  if es is not None:
    if create_index(es, 'zoo_v4'):
      es.index(index='zoo_v4', doc_type='_doc', body={"name": content._id, "words": content.words, "wiki": content.wiki})
      print('Data indexed successfully')