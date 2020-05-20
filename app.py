import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'myCodeDictionary'
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
@app.route('/get_categories')
def get_categories():
    return render_template("home.html",
                           categories=mongo.db.categories.find())


@app.route('/get_htmldefinitions')
def get_htmldefinitions():
    return render_template("htmldefinitions.html",
                           terms=mongo.db.terms.find())


@app.route('/get_cssdefinitions')
def get_cssdefinitions():
    return render_template("cssdefinitions.html",
                           terms=mongo.db.terms.find())


@app.route('/add_definition')
def add_definition():
    return render_template("adddefinition.html",
                           categories=mongo.db.categories.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
