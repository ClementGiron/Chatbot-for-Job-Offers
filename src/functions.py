from geopy import distance
from geopy import Point
import re
import unicodedata
import numpy as np
from stop_words import get_stop_words
from nltk.stem.snowball import FrenchStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd


stemmer = FrenchStemmer()
stop_words = get_stop_words('fr')
stop_words = [e.upper() for e in stop_words]
stop_words.append("BR")


def tokenize(text):
    """Returns the array of tokens of the text.

        Keyword arguments:
        text -- A string
        """
    global stop_words
    text = text.replace("'", "")
    pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    pattern2 = re.compile('www(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    text = pattern.sub('', text)
    text = pattern2.sub('', text)
    text = text.replace("(", "").replace(")","")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore")
    text = text.decode("utf-8")
    tokens = re.compile('\w+').findall(text.upper())
    tokens = [stemmer.stem(e) for e in tokens if ((not (e in stop_words)) and (len(e)>2) and (e[0].isalpha()))]

    return tokens


def tokenize2(text):
    """Returns the array of tokens of the text.

        Keyword arguments:
        text -- A string
        """
    global stop_words
    if type(text) == float:
        print(text)
    text = text.replace("/", " ")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore")
    text = text.decode("utf-8")
    tokens = re.compile('\w+').findall(text.upper())
    tokens = [stemmer.stem(e) for e in tokens if ((not (e in stop_words)) and (len(e)>2) and (e[0].isalpha()))]

    return tokens


def bool_partiel(prop):
    """Returns true if prop contanins "partiel".

        Keyword arguments:
        prop -- A string
        """
    tok = tokenize(prop)
    return ('partiel' in tok)


def bool_plein(prop):
    """Returns true if prop contanins "plein".

        Keyword arguments:
        prop -- A string
        """
    tok = tokenize(prop)
    return ('plein' in tok)


def quel_temps(prop):
    """Returns the type of work the user requested.

        Keyword arguments:
        prop -- The user request
        """
    partiel = bool_partiel(prop)
    plein = bool_plein(prop)

    if (partiel + plein == 1):
        return("Temps partiel"*partiel + "Temps plein"*plein)
    else:
        return "Faux"


def calcule_distance(long1lat1, long2, lat2):
    """Returns the distance in kilometers between the two coordinates.

        Keyword arguments:
        long1lat1 -- The longitude and latitude of the first point
        long2 -- The longitude of the second point
        lat2 -- The latitude of the second point
        """
    p1 = Point(long1lat1)
    p2 = Point(long2 + " " + lat2)
    return distance.distance(p1,p2).kilometers


def TF_IDF_matrix(dataframe):
    """Returns the TF-IDF matrix of dataframe.

        Keyword arguments:
        dataframe -- The pandas dataframe of the job offers
        """
    dataframe["desc_propre"] = dataframe["desc"].apply(lambda w : ' '.join(tokenize(w)))
    countvec = CountVectorizer()
    count = countvec.fit_transform(dataframe.desc_propre)
    vectorizer = TfidfVectorizer(vocabulary=countvec.get_feature_names())
    word_list = countvec.get_feature_names()
    return pd.DataFrame(vectorizer.fit_transform(dataframe.desc_propre).toarray(), columns=vectorizer.get_feature_names()).as_matrix(), word_list


def frequence_matrix(dataframe):
    """Returns the frequency matrix of dataframe.

        Keyword arguments:
        dataframe -- The pandas dataframe of the job offers
        """
    dataframe["sect_join"] = dataframe["sect"].apply(lambda w : ' '.join(tokenize2(w)))
    countvec = CountVectorizer()
    return pd.DataFrame(countvec.fit_transform(dataframe.sect_join).toarray(), columns=countvec.get_feature_names())


def frequence_requete(text, word_list):
    """Returns frequency of the words in the text.

        Keyword arguments:
        text -- A string
        word_list -- List of the words of the current IF-IDF matrix
        """
    tokens = np.array(tokenize(text))
    counts = np.array([np.sum(tokens == e) for e in word_list])
    return counts/len(tokens)


def score_offre(requete, word_list, tf_idf_offre):
    """Returns the score of a job offer.

        Keyword arguments:
        requete -- The user request
        word_list -- List of the words of the current IF-IDF matrix
        tf_idf_offre -- The array of the TF-IDF of the job offer
        """
    freq = frequence_requete(requete, word_list)

    return np.sum(np.multiply(freq, tf_idf_offre))


def ville_to_gps(ville, city_gps_base):
    """Returns the gps coordinate of the city ville.

        Keyword arguments:
        ville -- The city name in string format
        city_gps_base -- The pandas dataframe of the city gps coordinates associations
        """

    try:
        lon = city_gps_base.loc[ville,'longitude']
        lat = city_gps_base.loc[ville,'latitude']
        if type(lon) != str:
            lon = list(lon)[0]
            lat = list(lat)[0]
        return (lon,lat)
    except:
        return 1


def extract_number(information):
    """Extracts the first number in a string.

        Keyword arguments:
        information -- A string
        """
    try:
        distance = re.findall("\d+", information)[0]
        return int(distance)
    except:
        return -1


def nettoyage(l, period):
    """Adds  \n every period characters to l.

        Keyword arguments:
        l -- A sting variable
        period -- The period for adding \n
        """
    res = []
    for e in l:
        for k in range(1,len(e)//period +1):
            e = e[:period*k]+ '\n' + e[period*k:]
        res.append(e)

    return res
