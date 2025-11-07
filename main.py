from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/candidacy")
def candidacy():
    return render_template("candidacy.html")

@app.route("/apply/<empresa>/<post>")
def apply(empresa, post):
    return "pendente"

@app.route("/vacancies")
def vacancies():
    return render_template("vacancies.html")

@app.route("/create")
def create():
    return render_template("create.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
