import flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

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
    notificationDate = db.Column(db.DateTime, default=datetime.now, nullable=False)
    archiveDate = db.Column(db.DateTime, default=(datetime.now() + timedelta(days=30)), nullable=False)
    keepFlag = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return "<Repo %r>" % self.id

@app.route('/')
def index():
    try:
        return flask.render_template('index.html', pat=flask.session['pat'])
    except KeyError:
        return flask.render_template('index.html', pat='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        flask.session['pat'] = flask.request.form['pat']
        return flask.redirect('/')
    return '''
        <form method="post">
            <p><input type=text name=pat>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flask.session.pop('pat', None)
    return flask.redirect('/')

if __name__ == "__main__":
    app.run(debug=True)