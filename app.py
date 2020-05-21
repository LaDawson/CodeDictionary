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

""" THIS IS THE ROUTE FOR RENDERING THE HOME PAGE
    WITH THE LIST OF CATEGORIES AND SIGN IN FORM """


@app.route('/')
@app.route('/all_categories')
def all_categories():
    return render_template("home.html",
                           categories=mongo.db.categories.find())


@app.route('/get_category/<category_id>')
def get_category(category_id):
    the_cat = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    all_categories = mongo.db.categories.find()
    the_terms = mongo.db.terms.find()
    return render_template('category.html',
                           categories=all_categories,
                           cat=the_cat,
                           term=the_terms)


@app.route('/add_definition')
def add_definition():
    return render_template("adddefinition.html",
                           categories=mongo.db.categories.find())


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
