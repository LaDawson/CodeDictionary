import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt
if os.path.exists("env.py"):
    import env

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
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


@app.route('/insert_definition', methods=['POST'])
def insert_definition():
    term = mongo.db.terms
    term.insert_one(request.form.to_dict())
    return redirect(url_for('all_categories'))


""" REGISTER AND LOGIN ROUTES """


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_users = users.find_one({'user_name':
                                         request.form['username']})

        if existing_users is None:
            if request.form['password'] == request.form['repeat_password']:
                hashed_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'user_name': request.form['username'],
                              'user_password': hashed_password,
                              'user_email': request.form['email']})
                session['username'] = request.form['username']
                return redirect(url_for('all_categories'))
            return 'Passwords do not match'
        return 'That username already exists!'
    return render_template('register.html')


@app.route('/login_page')
def login_page():
    if 'username' in session:
        return render_template('adddefinition.html')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'user_name': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['user_password']) == login_user['user_password']:
            session['username'] = request.form['username']
        return redirect(url_for('add_definition'))

    return 'Invalid username/password combination'


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
