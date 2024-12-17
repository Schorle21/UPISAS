from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd 


def get_data_from_elastic():
    es = Elasticsearch(host='localhost',port=9200)

    query = {
        "query": {
                "match_all": {}
            }
    }
        
        # Scan function to get all the data. 
    rel = scan(client=es,             
               query=query,                                     
               scroll='1m',
               index='final_metrics_data',
               raise_on_error=True,
               preserve_order=False,
               clear_scroll=True)

    # Keep response in a list.
    result = list(rel)
    temp = []

    # We need only '_source', which has all the fields required.
    # This elimantes the elasticsearch metdata like _id, _type, _index.

    print("raw data:")

    for hit in result:
        temp.append(hit['_source'])
        
    # Create a dataframe..
    df = pd.DataFrame(temp)
    
    # Convert columns to appropriate data types (e.g., float)
    df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
    df['model_processing_time'] = pd.to_numeric(df['model_processing_time'], errors='coerce')
    df['image_processing_time'] = pd.to_numeric(df['image_processing_time'], errors='coerce')
    df['absolute_time_from_start'] = pd.to_numeric(df['absolute_time_from_start'], errors='coerce')
    
    # Check the dataframe after conversion
    print("DataFrame after type conversion:")
    print(df.head())
    
    return df