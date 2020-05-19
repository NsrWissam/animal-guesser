import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import numpy as np
import json 
from operator import itemgetter

#Defining the elasticsearch object
es = Elasticsearch(hosts=["https://70fa05be281c4ff8977b2a9e557f7690.westeurope.azure.elastic-cloud.com:9243/"], http_auth=("elastic","dpucymmIkDh7iOMjbUFFaRqA"))

#Function to define the query
def search_func(search_query):

    search_object = {
    "query":{
        "query_string":{
         "query": search_query
            }
        }
    }
    return json.dumps(search_object)

#Examples of queries
query1 = "trunk Africa"
query2 = "big mammal with a trunk living in Africa it has horns and weights several tons"
query3 = "red insect with black spots"
query4 = "it is a red beetle with black spots it has six legs it can fly"
query5 = "wild pig"
query6 = "it's a wild pig we can find it in our forests in Europe"

#Different responses to the queries based on the index chosen 
#To be noted that zoo_v2 and zoo_v3 have the same analyzer (the one by default)
#zoo_v4 has a custom analyzer based on the english language (remove stopwords, algorithmic stemmer including possessive words) 
response_basic= es.search(index='zoo_v2', body=search_func(query4))
response_standard = es.search(index='zoo_v3', body=search_func(query4))
response_improved = es.search(index='zoo_v4', body=search_func(query4))

#Show the first result, the one with the highest score for the 3 indexes
for hit, hit1, hit2 in zip(response_basic['hits']['hits'], response_standard['hits']['hits'], response_improved['hits']['hits']):
    print("Score for zoo_v2 index:")
    print(hit['_id'], '  ', hit['_score'])
    print("Score for zoo_v3 index:")
    print(hit1['_source']['animal'], '  ', hit1['_score'])
    print("Score for zoo_v4 index:")
    print(hit2['_source']['name'], '  ', hit2['_score'])
    break