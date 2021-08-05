import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
import re
import pandas as pd
from sklearn.datasets import load_files
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import os

true = pd.read_csv('True.csv')
fake = pd.read_csv('Fake.csv')

true['label'] = 0
fake['label'] = 1

def lemmatize(doc):
    document = doc.split()
    document = [stemmer.lemmatize(word) for word in document]
    document = ' '.join(document)
    return document

if 'news' not in os.listdir():
    os.mkdir('news')
    os.mkdir('./news/fake')
    os.mkdir('./news/true')

    df = pd.concat([true, fake], ignore_index=True)
    df.drop_duplicates(inplace=True)

    stemmer = WordNetLemmatizer()

    df['text'] = df['text'].apply(lambda x: re.sub(r'\W', ' ', x))
    df['text'] = df['text'].apply(lambda x: re.sub(r'\s+[a-zA-Z]\s+', ' ', x))
    df['text'] = df['text'].apply(lambda x: re.sub(r'\^[a-zA-Z]\s+', ' ', x))
    df['text'] = df['text'].apply(lambda x: x.lower())
    df['text'] = df['text'].apply(lambda x: lemmatize(x))

    labels=[]
    for x in df['label'].values:
        if x == 1:
            labels.append(1)
        if x == 0:
            labels.append(0)

    documents=[]
    for l in df['text'].values:
        documents.append(l)

    for i in range(0,len(documents)):
        if labels[i] == 1:
            with open(f'./news/true/{i}.txt',mode='w',encoding='utf-8') as c:
                c.write(documents[i])
        if labels[i] == 0:
            with open(f'./news/fake/{i}.txt',mode='w',encoding='utf-8') as c:
                c.write(documents[i])

if 'news' in os.listdir():
    newsdata = load_files('news')
    X, y = newsdata.data, newsdata.target
    documents = [d for d in X]
    vectorizer = TfidfVectorizer(max_features=3000)
    vec = vectorizer.fit_transform(documents).toarray()

    X_train, X_test, y_train, y_test = train_test_split(vec, y, test_size=0.2, random_state=42)

    nb = MultinomialNB()
    nb.fit(X_train,y_train)

    # print("Score of train data:", nb.score(X_train, y_train))
    # print("Score of test data:", nb.score(X_test, y_test))

    print(nb.predict(vectorizer.transform(['Godzilla dancing in tokio'])))





