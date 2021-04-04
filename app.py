import os
import pathlib

import sklearn
import requests, datetime, random
import pandas, numpy
from sklearn.metrics.pairwise import cosine_similarity
from joblib import dump, load
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import varta_tools as v

app = Flask('Varta Media')

from database_tables import *

db.init_app(app)

app.secret_key = 'VartaMedia'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

GOOGLE_CLIENT_ID = '101956761353-rs0ihfgbigb4gb7gn4dq52sq20mpkfif.apps.googleusercontent.com'
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email',
            'openid'],
    redirect_uri='http://127.0.0.1:5000/callback'
)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/varta_media'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vdrnigwaqybubl:8d117f3be50b4129c4b4d4a71f54be7ec71a4001c12d25f265228709722776b2@ec2-52-21-252-142.compute-1.amazonaws.com:5432/d89h8rrdrlbg2s'

recommend_news = pandas.read_csv('data/news_learn.csv')
# svc_c = load(open('data/linearsvc_classification.joblib', 'rb'))
# svc_s = load(open('data/svc_sentiment.joblib', 'rb'))
# tfidf_c = load(open('data/tfidf_classification.joblib', 'rb'))
tfidf_r = load(open('data/tfidf_recommend.joblib', 'rb'))
save_tfidf = numpy.load('data/text.npy')

@app.errorhandler(404)
def error404(error):
    return render_template('404.html'), 404


@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    session['authentication'] = 'loggedin'
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session['google_id'] = id_info.get('sub')
    session['name'] = id_info.get('name')
    session['email'] = id_info.get('email')
    session['username'] = session['email'].split('@')[0]

    if db.session.query(Users).filter(Users.id == session['google_id']).count() == 0:
        user = Users(session['google_id'], session['name'], session['username'], session['email'])
        news = News(session['google_id'])
        scores = Scores(session['google_id'])
        db.session.add(user)
        db.session.add(news)
        db.session.add(scores)
        db.session.commit()
    login_time = LoginLogs(session['google_id'], session['name'], datetime.datetime.now())
    db.session.add(login_time)
    db.session.commit()
    return redirect(session['redirect_url'])


@app.route('/logout')
def logout():
    logout_time = LogoutLogs(session['google_id'], session['name'], datetime.datetime.now())
    db.session.add(logout_time)
    db.session.commit()
    session.clear()
    session['authentication'] = 'loggedout'
    return redirect('/')


@app.route('/')
def index():
    session['redirect_url'] = '/'
    if 'authentication' not in session or 'name' not in session:
        session['authentication'] = 'loggedout'
        user = ' Google Login'
    elif 'name' in session:
        user = session['name']

    return render_template('index.html', state=session['authentication'], user=user)


@app.route('/user')
def user():
    session['redirect_url'] = '/user'
    if 'google_id' not in session:
        return redirect('/signin')
    else:
        return render_template('user.html', session=session)


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/recommend/<string:category>')
def recommend(category):
    return render_template('learn.html', state=session['authentication'], user=session['name'],
                           news_category=category.title(), news=recommend_news[recommend_news['category'] == category].reset_index())


@app.route('/process/<string:category>', methods=['GET', 'POST'])
def process(category):
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=True)
        form_data = {k: str(int(v)/10) for k, v in form_data.items()}
        rating = ','.join(form_data.values())
        news = News.query.get_or_404(session['google_id'])
        score = Scores.query.get_or_404(session['google_id'])
        if category == 'india':
            news.india = 1
            score.india = rating
        if category == 'world':
            news.world = 1
            score.world = rating
        if category == 'business':
            news.business = 1
            score.business = rating
        if category == 'technology':
            news.technology = 1
            score.technology = rating
        if category == 'education':
            news.education = 1
            score.education = rating
        if category == 'entertainment':
            news.entertainment = 1
            score.entertainment = rating
        if category == 'covid19':
            news.covid19 = 1
            score.covid19 = rating
        db.session.add(news)
        db.session.add(score)
        db.session.commit()
    return redirect(session['redirect_url'])


@app.route('/news/city/<string:city>')
def news_city(city):
    session['redirect_url'] = f'/news/city/{city}'
    if 'google_id' not in session:
        return redirect('/signin')
    else:
        news = v.fetch_news(city)
        return render_template('news.html', news_category=city.title(), news=news, state=session['authentication'], user=session['name'])


@app.route('/news/<string:category>')
def news_category(category):
    session['redirect_url'] = f'/news/{category}'
    if 'google_id' not in session:
        return redirect('/signin')
    else:
        news = News.query.get_or_404(session['google_id'])
        user_news = {'id': news.id, 'india': news.india, 'world': news.world, 'business': news.business,
                                  'technology': news.technology, 'education': news.education, 'entertainment': news.entertainment,
                                  'covid19': news.covid19}
        if user_news[category] == 0:
            return redirect(f'/recommend/{category}')
        else:
            news = v.fetch_news(category)
            text = v.get_text(news)
            news_tfidf = tfidf_r.transform(text[:36]).toarray()
            saved_tfidf = v.get_category_tfidf(save_tfidf, category)
            score = Scores.query.get_or_404(session['google_id'])
            user_scores = {'id': score.id, 'india': score.india, 'world': score.world, 'business': score.business,
                           'technology': score.technology, 'education': score.education,
                           'entertainment': score.entertainment,
                           'covid19': score.covid19}
            rec_ids = v.recommend_news(cosine_similarity(saved_tfidf, news_tfidf), user_scores[category])
            recommended_news = [news[i] for i in rec_ids]
            return render_template('news.html', news_category=category.title(), news=recommended_news, state=session['authentication'], user=session['name'])


@app.route('/classify')
def classify():
    session['redirect_url'] = '/classify'
    if 'google_id' not in session:
        return redirect('/signin')
    else:
        return render_template('classify.html', state=session['authentication'], user=session['name'])

@app.route('/classify/tags', methods=['GET', 'POST'])
def classified():
    session['redirect_url'] = '/classify'
    if 'google_id' not in session:
        return redirect('/signin')
    else:
        if request.method == 'POST':
            form_data = request.form.to_dict(flat=True)

        return render_template('classify.html', state=session['authentication'], user=session['name'])


if __name__ == '__main__':
    app.run()
