from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(200), primary_key=True)
    name = db.Column(db.String(200))
    username = db.Column(db.String(200))
    email = db.Column(db.String(300))

    def __init__(self, id, name, username, email):
        self.id = id
        self.name = name
        self.username = username
        self.email = email


class LoginLogs(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(200))
    name = db.Column(db.String(200))
    login_time = db.Column(db.String(200))

    def __init__(self, google_id, name, login_time):
        self.google_id = google_id
        self.name = name
        self.login_time = login_time


class LogoutLogs(db.Model):
    __tablename__ = 'logout_logs'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(200))
    name = db.Column(db.String(200))
    logout_time = db.Column(db.String(200))

    def __init__(self, google_id, name, logout_time):
        self.google_id = google_id
        self.name = name
        self.logout_time = logout_time


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.String(200), primary_key=True)
    india = db.Column(db.Integer)
    world = db.Column(db.Integer)
    business = db.Column(db.Integer)
    technology = db.Column(db.Integer)
    education = db.Column(db.Integer)
    entertainment = db.Column(db.Integer)
    covid19 = db.Column(db.Integer)

    def __init__(self, id, india=0, world=0, business=0, technology=0, education=0, entertainment=0, covid19=0):
        self.id = id
        self.india = india
        self.world = world
        self.business = business
        self.technology = technology
        self.education = education
        self.entertainment = entertainment
        self.covid19 = covid19


class Scores(db.Model):
    __tablename__ = 'news_scores'
    id = db.Column(db.String(50), primary_key=True)
    india = db.Column(db.String(50))
    world = db.Column(db.String(50))
    business = db.Column(db.String(50))
    technology = db.Column(db.String(50))
    education = db.Column(db.String(50))
    entertainment = db.Column(db.String(50))
    covid19 = db.Column(db.String(50))

    def __init__(self, id, india=0, world=0, business=0, technology=0, education=0, entertainment=0, covid19=0):
        self.id = id
        self.india = india
        self.world = world
        self.business = business
        self.technology = technology
        self.education = education
        self.entertainment = entertainment
        self.covid19 = covid19