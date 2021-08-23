from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import zlib,pickle,re
import redis


compressed_df = zlib.compress(pickle.dumps(pd.DataFrame()))


def lemmatize(doc: str) -> str:
    """
    Function that lemmatizes given document with WordNetLemmatizer from nltk lib
    :param doc:Document to be lemmatizet
    :return: Lemmatizet document
    """
    document = doc.split()
    document = [stemmer.lemmatize(word).lower() for word in document]
    document = ' '.join(document)
    return document


def preprocess_text(dataframe: pd.DataFrame()) -> pd.DataFrame():
    """
    Function preprocess text contained in dataframe by deleting
    special signs, single characters at beginning of sentences,single characters
    inside of sentences, brings all words to lower case and lemmatizes them.
    :param dataframe: Dataframe with 'text' field to be preprocessed
    :return: Preprocessed dataframe
    """
    dataframe['text'] = dataframe['text'].apply(lambda x: re.sub(r'\W', ' ', x))
    dataframe['text'] = dataframe['text'].apply(lambda x: re.sub(r'\s+[a-zA-Z]\s+', ' ', x))
    dataframe['text'] = dataframe['text'].apply(lambda x: re.sub(r'\^[a-zA-Z]\s+', ' ', x))
    dataframe['text'] = dataframe['text'].apply(lambda x: lemmatize(x))
    dataframe.drop_duplicates(inplace=True)
    return dataframe


def compress(dataframe: pd.DataFrame) -> compressed_df:
    """
    Function compresses given dataframe for redis-friendly format
    :param dataframe: Dataframe to be compressed
    :return: Compressed dataframe
    """
    return zlib.compress(pickle.dumps(dataframe))


def decompress(dataframe: compressed_df) -> pd.DataFrame:
    """
    Function decompresses given dataframe to make it accesible by user
    :param dataframe: Dataframe pickled and compressed
    :return: Decompressed dataframe
    """
    return pickle.loads(zlib.decompress(dataframe))


if __name__ == '__main__':
    redis_con = redis.Redis()
    stemmer = WordNetLemmatizer()

    frontend_dev = decompress(redis_con.get('frontend developer'))
    dev_ops = decompress(redis_con.get('dev ops'))
    soft_eng = decompress(redis_con.get('software engineer'))
    tester = decompress(redis_con.get('tester'))
    data_scientist = decompress(redis_con.get('data scientist'))

    df = pd.concat([soft_eng,tester,data_scientist,frontend_dev,dev_ops])
    preprocess_text(df)



    X,y = df.text,df.label
    vectorizer = TfidfVectorizer(max_features=3000)
    vec = vectorizer.fit_transform(df['text']).toarray()
    X_train, X_test, y_train, y_test = train_test_split(vec, y, test_size=0.2,
                                                        random_state=42)

    nb = MultinomialNB()
    nb.fit(X_train, y_train)


    with open('text_classifier', 'wb') as picklefile:
        pickle.dump(nb,picklefile)

    with open('vectorizer', 'wb') as picklefile:
        pickle.dump(vectorizer,picklefile)