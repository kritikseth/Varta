import pandas as pd
import numpy as np
# import re
# import nltk
import datetime
from GoogleNews import GoogleNews

def fetch_news(category):
    googlenews = GoogleNews()
    today = datetime.date.today().strftime(format='%m-%d-%Y')
    googlenews.set_lang('en')
    googlenews.set_period('7d')
    googlenews.set_time_range(today, today)
    googlenews.set_encode('utf-8')
    googlenews.get_news(category)
    return googlenews.results()

def get_text(news):
    news = pd.DataFrame(news)
    return news['title'] + ' ' + news['desc']

def get_category_tfidf(df, category):
    categories = ['business', 'technology', 'world', 'india', 'covid19', 'education', 'entertainment']
    ind = categories.index(category)
    inds = list(range(ind*9,ind*9+9))
    return df[inds]

def recommend_news(cs, rating):
    rating = rating.split(',')
    rating = [float(no) for no in rating]
    rating_ing = np.argsort(rating)[::-1]
    rec_news, rec_ind = [], []
    for ind in rating_ing:
        rec_news.append(np.argsort(cs[ind])[-1])
        rec_ind.append([ind]*2)
    rec_news = np.array(rec_news).flatten()
    if len(np.unique(rec_news)) >= 9:
        return rec_news[:9]
    else:
        return list(range(9))

# nltk.download('stopwords', quiet=True)
# nltk.download('punkt', quiet=True)
# nltk.download('wordnet', quiet=True)

# stops = set(nltk.corpus.stopwords.words('english'))
# lemmatizer = nltk.stem.WordNetLemmatizer()
#
# def clean_text(series):
#     series = series.str.lower()
#     ntext = []
#     for text in series:
#         text = re.sub(r'[^a-zA-Z]', ' ', text, 0)
#         text = re.sub(' +', ' ', text)
#         text = nltk.word_tokenize(text.lower())
#         text = [lemmatizer.lemmatize(w) for w in text if w not in stops]
#         text = ' '.join(text)
#         ntext.append(text)
#     return ntext