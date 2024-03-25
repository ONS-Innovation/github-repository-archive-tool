import flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = flask.Flask(__name__)
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
    notificationDate = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return "<Repo %r>" % self.id

if __name__ == "__main__":
    app.run()