import csv
import re
import os
from tqdm import tqdm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import pandas as pd
import pickle
from scipy.special import softmax
import numpy as np

def model_train():
    csv_path = r'ML/Dataset/'
    model_path = r'ML/'


    train = pd.read_csv(csv_path+'train.csv')
    test = pd.read_csv(csv_path+'test.csv')
    trainX = train['text'].to_numpy()
    trainY = train['category'].to_numpy()
    testX = test['text'].to_numpy()
    testY = test['category'].to_numpy()

    def hashingvector (docs_train, y_train, docs_test, ngram_range, ):

        hashingvector = HashingVectorizer(stop_words = "english",
                                    analyzer = 'word',
                                    lowercase = True,
                                    ngram_range = ngram_range)
        
        X_train = hashingvector.fit_transform(docs_train)
        # with open('encoder_pytesseract.pickle', 'wb') as handle:
        with open(model_path+'encoder_pytesseract.pickle', 'wb') as handle:
            pickle.dump(hashingvector, handle, protocol=pickle.HIGHEST_PROTOCOL)
        X_test = hashingvector.transform(docs_test)
        print(X_train)
        
        clf = SGDClassifier(loss = "hinge", penalty = "l1")
        
        clf.fit(X_train, y_train)

        # with open('model_pytesseract.pickle', 'wb') as handle:
        with open(model_path+'model_pytesseract.pickle', 'wb') as handle:
            pickle.dump(clf, handle, protocol=pickle.HIGHEST_PROTOCOL)

        prediction = softmax(clf.decision_function(X_test), axis=1)
        # prediction = clf.predict(X_test)
        return prediction

    predY = hashingvector(trainX, trainY, testX, (1,1))
    predY = np.argmax(predY, axis=1)

    # print(predY)
    print(accuracy_score(predY, testY))
    # # Ngram accuracy is 78% 

    print(confusion_matrix(predY, testY, labels=None, sample_weight=None, normalize=None))

if '__main__' == __name__ :
    model_train()