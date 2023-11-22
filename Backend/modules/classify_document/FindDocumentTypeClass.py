import shutil
import pickle
from scipy.special import softmax
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import json
import sys
import pandas as pd
import os
from configparser import ConfigParser

#### Environment ####
enivronment = 'production'
# enivronment = 'development'
#### Environment ####

configur = ConfigParser()
config_file_obj = configur.read('config.ini')
model_path = configur.get(enivronment,'find_doc_type_model')
encoder_path = configur.get(enivronment,'find_doc_type_encoder')

class FindDocumentType():

    def __init__(self,doc_text) -> None:
        self.text = doc_text
    
    def finddocumenttype(self) : 
        try:
            text = [self.text]
            prediction_data_df = pd.DataFrame()

            with open(model_path, 'rb') as handle:
                clf = pickle.load(handle)
            with open(encoder_path, 'rb') as handle:
                encoder = pickle.load(handle)

            string = text
            

            X_test = encoder.transform(string)
            scores = softmax(clf.decision_function(X_test)[0])
            prediction_data_dict = {}
            
            # {0 : 'Coutume',1:'Cremerie',2:'LCG',3:'Pimeurs d_issy',4:'Reynaud'}
            prediction_data_dict['Coutume'] = scores[0]
            prediction_data_dict['Cremerie'] = scores[1]
            prediction_data_dict['LCG'] = scores[2]
            prediction_data_dict['Pimeurs_d_issy'] = scores[3]
            prediction_data_dict['Reynaud'] = scores[4]
            # print(prediction_data_dict)
            # print('********************')
            return prediction_data_dict
        
        except Exception as e:
            print(json.dumps({"Error": str(e)}))

