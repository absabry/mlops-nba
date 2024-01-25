from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay

from sklearn.model_selection import train_test_split
import time
import pandas as pd
from sklearn import preprocessing


df = pd.read_parquet('/Users/karina/Desktop/ML projects/untitled folder/mlops-nba/data/curated/curated_players-20240125__145225.parquet')

def prepare_for_model(df):
    df=df.drop(columns=['filename', 'efficency', 'Rk'])
    le = preprocessing.LabelEncoder()
    for i in ['Player', 'Pos', 'Tm', 'season', 'period' ]:
        df.loc[:,i] = le.fit_transform(df.loc[:,i])
    return df 

def classification_model(df):

    X = df.drop('rising_stars', axis=1)
    y = df['rising_stars']

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 42)
    
    rf = RandomForestClassifier()
    t0 = time.time()
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    training_time = time.time()-t0
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy, training_time