import shutil
import pickle
from scipy.special import softmax
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import json
import sys
import pandas as pd
import os

try:
    text_file_path = 'ML/Train_txt/'
    for subfolder in os.listdir(text_file_path) :
        print('********************')
        print(subfolder)
        for text_file in os.listdir(text_file_path+subfolder):
            print(text_file)
            with open (text_file_path+subfolder+'/'+text_file) as txt_file_obj :
                text = txt_file_obj.readlines()
                txt_file_obj.close()
                print(text_file)

            prediction_data_df = pd.DataFrame()

            with open('ML/model_pytesseract.pickle', 'rb') as handle:
                clf = pickle.load(handle)
            with open('ML/encoder_pytesseract.pickle', 'rb') as handle:
                encoder = pickle.load(handle)

            string = text
            
            X_test = encoder.transform(string)

            scores = softmax(clf.decision_function(X_test)[0])

            # print(json.dumps(list(scores)))
            # score = max(list(scores))
            #   category_index =  pd.Series(list(scores)).idxmax()
            prediction_data_dict = {}
            # prediction_data_dict['text'] = text
            prediction_data_dict['Coutume'] = scores[0]
            prediction_data_dict['Cremerie'] = scores[1]
            prediction_data_dict['LCG'] = scores[2]
            prediction_data_dict['Pimeurs d_issy'] = scores[3]
            prediction_data_dict['Reynaud'] = scores[4]
            print(prediction_data_dict)
            # prediction_data_df = prediction_data_df.append(prediction_data_dict,ignore_index = True)
            # prediction_data_df.to_csv(csv_path+'prediction_data.csv',mode='a',index=False,header=False)
            print('********************')
        break
except Exception as e:
  print(json.dumps({"Error": str(e)}))

