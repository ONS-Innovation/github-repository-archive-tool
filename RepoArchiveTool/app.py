import flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import apiScript

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///repoArchiveTool.db"
db = SQLAlchemy(app)

# Create the Database if it doesn't already exist
with app.app_context():
    db.create_all()

# Declare the Database Table
class Repositories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repoName = db.Column(db.String(100), nullable=False)
    repoURL = db.Column(db.String(255), nullable=False)
    repoAPIURL = db.Column(db.String(255), nullable=False)
    lastCommitDate = db.Column(db.DateTime, nullable=True)
    comparisonDate = db.Column(db.DateTime, nullable=True)
    notificationDate = db.Column(db.DateTime, default=datetime.now, nullable=False)
    dateToArchive = db.Column(db.DateTime, default=(datetime.now() + timedelta(days=30)), nullable=False)
    keepFlag = db.Column(db.Boolean, default=False)

    # Table Structure Notes:

    # id: record primary key
    # repoName: the name of the repo
    # repoURL: a link to the repo
    # repoAPIURL: the api endpoint for the repo so further api calls can be made
    # lastCommitDate: when the repo was last updated (pushed_at on github)
    # comparisonDate: the archive date given by the user
    # notificationDate: when the notification email was sent -> also shows when the record was added
    # dateToArchive: when the repo can be archived from (30 days after email)
    # keepFlag: whether the repo should remain unarchived

    # When the repo gets archived, it should be removed from the table
    

    def __repr__(self) -> str:
        return "<Repo %r>" % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if flask.request.method == "POST":
        flask.session['pat'] = flask.request.form['pat']

    try:
        return flask.render_template('index.html', pat=flask.session['pat'], date=datetime.now().strftime("%Y-%m-%d"))
    except KeyError:
        return flask.render_template('index.html', pat='', date=datetime.now().strftime("%Y-%m-%d"))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if flask.request.method == 'POST':
        flask.session['pat'] = flask.request.form['pat']

        # No need to test token here as tested when getting repos

        return flask.redirect('/')
    return flask.redirect('/')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flask.session.pop('pat', None)
    return flask.redirect('/')

@app.route('/FindRepositories', methods=['POST', 'GET'])
def findRepos():
    if flask.request.method == 'POST':
        # Create APIHandler instance
        gh = apiScript.APIHandler(flask.session['pat'])

        # Get form values
        org = flask.request.form['org']
        date = flask.request.form['date']
        repoType = flask.request.form['repoType']

        repos = apiScript.GetOrgRepos(org, date, repoType, gh)

        if type(repos) == str:
            # Error Message Returned
            # Need to make an error page
            return repos

        return repos

if __name__ == "__main__":
    app.run(debug=True)