import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
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


""" ROUTE THAT RENDERS THE HOME PAGE """


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


""" ROUTE FOR RENDERING ADD DEFINITION PAGE"""


@app.route('/add_definition')
def add_definition():
    return render_template("adddefinition.html",
                           categories=mongo.db.categories.find())


""" ROUTE TAKING VALUES FROM FORM TO INSERT TERM TO DB """


@app.route('/insert_definition', methods=['POST'])
def insert_definition():
    term = mongo.db.terms
    term.insert_one(request.form.to_dict())
    return redirect(url_for('all_categories'))


""" REGISTE ROUTE FOR REGISTER NAV BUTTON AND REGISTER LINK FROM LOGIN FORMS """


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_users = users.find_one({'user_name':
                                         request.form['username']})
        if existing_users is None:
            if request.form['password'] == request.form['repeat_password']:
                hashed_password = bcrypt.hashpw(
                    request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'user_name': request.form['username'],
                              'user_password': hashed_password,
                              'user_email': request.form['email'],
                              'admin': 'no'})
                session['username'] = request.form['username']
                return redirect(url_for('all_categories'))
            flash('Passwords do not match')
        else:
            flash('That username already exists!')
    return render_template('register.html')


""" LOGIN ROUTE FOR THE LOGIN NAV BUTTON """


@app.route('/login_main')
def login_main():
    if 'username' in session:
        return redirect(url_for('all_categories'))
    return render_template('mainloginroute.html')


@app.route('/login_mainlogin', methods=['POST'])
def login_mainlogin():
    users = mongo.db.users
    login_user = users.find_one({'user_name': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['user_password']) == login_user['user_password']:
            session['username'] = request.form['username']
            session['admin_user'] = login_user['admin']
        return redirect(url_for('all_categories'))
    else:
        flash('Invalid password/username combination')


""" LOGIN ROUTE FOR THE ADD TERM NAV BUTTON """


@app.route('/login_page_addterm')
def login_page_addterm():
    if 'username' in session:
        return redirect(url_for('add_definition'))
    return render_template('login_addterm.html')


@app.route('/login_addterm', methods=['POST'])
def login_addterm():
    users = mongo.db.users
    login_user = users.find_one({'user_name': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['user_password']) == login_user['user_password']:
            session['username'] = request.form['username']
        return redirect(url_for('add_definition'))
    else:
        flash('Invalid password/username combination')


""" ADMIN PAGE """


@app.route('/admin_page')
def admin_page():
    the_terms = mongo.db.terms.find()
    users = mongo.db.users
    if 'username' in session:
        the_user = users.find_one({'user_name': session['username']})
        if the_user['admin'] == "yes":
            return render_template('adminpage.html',
                                   terms=the_terms,
                                   user=the_user)
    else:
        return render_template('mainloginroute.html')
    return redirect(url_for('all_categories'))


""" ADMIN APPROVE TERM ROUTE """


@app.route('/approve_term/<term_id>', methods=['POST'])
def approve_term(term_id):
    terms = mongo.db.terms
    terms.update_one({'_id': ObjectId(term_id)},
                  {'$set': {'approved': "yes"}})
    return redirect(url_for('admin_page'))


    """ ADMIN DELETE TERM ROUTE """


@app.route('/delete_term/<term_id>')
def delete_term(term_id):
    terms = mongo.db.terms
    terms.remove({'_id': ObjectId(term_id)})
    return redirect(url_for('admin_page'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
