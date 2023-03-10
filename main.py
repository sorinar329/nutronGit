#!/usr/bin/env python3.10
import os

import numpy
from flask import Flask, render_template, request, url_for, redirect, session, flash
import sqlite3 as sql
from pyzbar import pyzbar

from werkzeug.utils import secure_filename
import cv2
from datetime import datetime
from datetime import timedelta
import queryCollection
import textManipulation
import userDAO

app = Flask(__name__)

# conn = sql.connect('/var/www/nutron/user.db')
db_path = '/var/www/nutron/user.db'
# db_path = "E:/nutronGit/user.db"
# db_path = 'C:/Users/meike/Downloads/nutronGit/user.db'
#db_path = "user.db"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routing Function for the Product Scanner
@app.route("/productScan", methods=['GET', 'POST'])
def productScan():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")
    username = cur.fetchone()
    con.close
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        return render_template("productScan.html", userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# Function for the access to the webcam
@app.route("/upload_webcam/", methods=['GET', 'POST'])
def upload_webcam():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")
    username = cur.fetchone()
    con.close

    message = ""
    ingredients = list()
    harmful_ingredients = list()

    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        key = cv2.waitKey(20)
        success = False
        for code in pyzbar.decode(frame):
            product_ean = code.data.decode('utf-8')
            name = queryCollection.get_product_name(code.data.decode('utf-8'))
            if len(name) > 0:
                message = textManipulation.get_product_name(name)
                ing = textManipulation.get_readableList(queryCollection.get_Ingredients_of_Prod(product_ean))
                harmful_ingredients = textManipulation.get_readableList_harmful(
                    queryCollection.get_harmful_ingredients_of_product(product_ean))
                ingredients = textManipulation.remove_duplicate_ingredients(ing, textManipulation.get_readableList(
                    queryCollection.get_harmful_ingredients_of_product(product_ean)))
                flash(message)
                success = True
            else:
                message = "No product with this EAN was found in the database"
                flash(message)
                success = True

        if success:
            break
    cv2.destroyWindow("preview")
    vc.release()
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        return render_template("productScan.html", userage=userDAO.getprofileage(), ingredients=ingredients,
                               harmful_ingredients=harmful_ingredients,
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


@app.route("/query_treatment", methods=['GET', 'POST'])
# Function for the manual upload of files
@app.route("/upload_file/", methods=['GET', 'POST'])
def upload_file():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select name from 'user'")
    username = cur.fetchone()
    con.close()

    ingredients = list()
    harmful_ingredients = list()
    name = list()
    message = ""
    if request.method == 'POST':
        test = request.files['filename']

        f = request.files['filename'].read()
        if allowed_file(test.filename):
            file_byte = numpy.fromstring(f, numpy.uint8)
            img = cv2.imdecode(file_byte, cv2.IMREAD_UNCHANGED)

            decode_objects = pyzbar.decode(img)
            for obj in decode_objects:
                product_ean = obj.data.decode('utf-8')
                name = queryCollection.get_product_name(product_ean)
                if len(name) > 0:
                    message = textManipulation.get_product_name(name)
                    # print(message)
                    ing = textManipulation.get_readableList(queryCollection.get_Ingredients_of_Prod(product_ean))
                    harmful_ingredients = textManipulation.get_readableList_harmful(
                        queryCollection.get_harmful_ingredients_of_product(product_ean))
                    ingredients = textManipulation.remove_duplicate_ingredients(ing, textManipulation.get_readableList(
                        queryCollection.get_harmful_ingredients_of_product(product_ean)))
                    flash(message)
                else:
                    message = "No product with this EAN was found in the database."
                    flash(message)

        elif not allowed_file(f.filename):
            flash('Allowed image types are png, jpeg, jpg,')
            return render_template("productScan.html", name=name, ingredients=ingredients,
                                   harmful_ingredients=harmful_ingredients, userage=userDAO.getprofileage(),
                                   message=message,
                                   useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())
        # print("I want to die " + str(ingredients))
        # print("I want to die too" + str(harmful_ingredients))
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template("productScan.html", userage=userDAO.getprofileage(), ingredients=ingredients,
                                   harmful_ingredients=harmful_ingredients, message=message,
                                   useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# managing the database
def databasemanager():
    conn = sql.connect(db_path)
    # database will drop at start of the app
    conn.execute('DROP TABLE IF EXISTS user')
    conn.execute('DROP TABLE IF EXISTS products')
    conn.execute('DROP TABLE IF EXISTS recipes')
    conn.execute('DROP TABLE IF EXISTS ingredients')
    conn.execute('DROP TABLE IF EXISTS symptoms')

    # creating the tables in the database
    conn.execute('Create Table user(name TEXT, age TEXT, g TEXT, activity TEXT, weight TEXT, datum TEXT)')
    conn.execute('Create Table products(class TEXT, label TEXT)')
    conn.execute('Create Table recipes(class TEXT, label TEXT)')
    conn.execute('CREATE Table ingredients(class TEXT, label TEXT)')
    conn.execute('CREATE Table symptoms(class TEXT, label TEXT)')
    conn.close()


databasemanager()


# Deletes a user entry from the database after 3 Hours.
def deleteexpired():
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT datum from 'user'")
    data = cursor.fetchall()
    for i in data:
        timez = datetime.fromisoformat(i[0])
        expiration = (datetime.now() - timez)
        if expiration > timedelta(hours=3):
            expired = str(timez)
            cursor.execute("DELETE from 'user' where datum = ?", (expired,))
            conn.commit()


# User of the session, will be redirected to log in.
def redirecttologin():
    username = session['username']
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * from 'user' where name = ?", (username,))
    data = cursor.fetchone()
    return data


# database filled with products and symptoms. this happens before the first request.
@app.before_first_request
def fill_database_products():
    con = sql.connect(db_path)
    cur = con.cursor()

    usda = queryCollection.triply_query_products()
    symptom_data = queryCollection.triply_query_symptoms_data()

    for item in usda:
        cur.execute("INSERT INTO ingredients(class, label) VALUES(?,?)",
                    (item["food"]["value"], item["label"]["value"]))
        con.commit()

    for item in symptom_data:
        cur.execute("INSERT INTO symptoms(class, label) VALUES(?,?)", (item["class"]["value"], item["label"]["value"]))
        con.commit()

    con.close()


# Homepage is brought up, at the start of the application
@app.route('/')
def hello():
    return render_template("TestHome.html")


# Returns the user to the Homepage
@app.route('/home', methods=['POST', 'GET'])
def backhome():
    if request.method == 'POST':
        return render_template('TestHome.html')


# Redirects the user to the ContactPage
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        return render_template('contact.html')


# Redirects the user to the Disclaimerpage
@app.route('/disclaimer', methods=['POST', 'GET'])
def disclaimer():
    if request.method == 'POST':
        return render_template('disclaimer.html')


@app.route('/contactnutron', methods=['POST', 'GET'])
def contactnutron():
    deleteexpired()
    if request.method == 'POST':
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template('contactnutron.html')


@app.route('/disclaimernutron', methods=['POST', 'GET'])
def disclaimernutron():
    deleteexpired()
    redirecttologin()
    if request.method == 'POST':
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template('disclaimernutron.html')


@app.route('/sparklis', methods=['POST', 'GET'])
def sparklis():
    if request.method == 'POST':
        return render_template('osparklis.html')


# logout function
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        username = session['username']
        # database connection
        conn = sql.connect(db_path)
        conn.execute("DELETE from 'user' where name = ?", (username,))
        conn.commit()
        conn.close()
        return render_template("index.html")


# When returning to the Homepage of productkg, the user is logged out.
@app.route('/logouttohome', methods=['POST', 'GET'])
def logouttohome():
    if request.method == 'POST':
        username = session['username']
        # database connection
        conn = sql.connect(db_path)
        conn.execute("DELETE from 'user' where name = ?", (username,))
        conn.commit()
        conn.close()
        return render_template("TestHome.html")


# Redirect to the login-page
@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return render_template('index.html')


# inserting user data into the database
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    deleteexpired()
    username = request.form['nm']
    session['username'] = username
    con = sql.connect(db_path)
    cur = con.cursor()
    cur.execute("Select name from 'user'")
    names = []
    for row in cur:
        for field in row:
            names.append(field)

    if str(username) in names:
        return render_template("index_login_failed.html")
    else:
        if request.method == 'POST':
            try:
                name = request.form['nm']
                age = request.form['age']
                gender = request.form['gender']
                activity = request.form['activity']
                weight = request.form['weight']
                with sql.connect(db_path) as con:
                    cur = con.cursor()

                    cur.execute("INSERT INTO user (name,age,g,activity, weight, datum)VALUES(?, ?, ?,?,?,?)",
                                (name, age, gender, activity, weight, datetime.now()))

                    con.commit()
                    msg = "User succesfully Added"
                    # con.close()
            except:
                con.rollback()
                msg = "error in insert operation"

            finally:
                return render_template("homepage.html", msg=msg, username=name, userage=userDAO.getprofileage(),
                                       useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# Redirect to the homepage of Nutron.
@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    deleteexpired()
    if request.method == 'POST':
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template('homepage.html', userage=userDAO.getprofileage(),
                                   useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# Redirect to nutrient.html
@app.route("/name", methods=['GET', 'POST'])
def name():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")

    username = cur.fetchone()
    con.close()

    # products and ingredients from the database
    ingredients = userDAO.getIngredients()
    produckte = userDAO.getProducts()
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        if 'username' in session:
            return render_template("nutrient.html", username=username['name'], produckte=produckte,
                                   ingredients=ingredients,
                                   userage=userDAO.getprofileage(), useractivity=userDAO.getprofileactivity(),
                                   everything=userDAO.getEverything())
        else:
            return render_template("index.html")


# redirect to symptoms.html
@app.route("/symptoms", methods=['GET', 'POST'])
def symptoms():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")

    username = cur.fetchone()
    con.close()
    symptoms = userDAO.getSymptoms()
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        return render_template("symptomsV2.html", userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(),
                               symptoms=symptoms)


# the function for getting the right nutrients for a given symptom
@app.route('/treatmentnutrient/', methods=['GET', 'POSt'])
def treatmentnutrient():
    deleteexpired()
    symptom = request.form['symptom']
    symptom = symptom.replace("http://purl.org/ProductKG/symptom#", "")
    symptoms = userDAO.getSymptoms()
    nutrients = queryCollection.triply_query_symptoms(symptom)
    nutrientlist = list()
    if len(nutrients) > 0:
        for item in nutrients:
            nutrientlist.append(item["nutrient"]["value"])
        nutrientlist = [n.replace('http://purl.org/ProductKG/nutrition#', '') for n in nutrientlist]
        # prefix = "http://purl.org/ProductKG/disease"
        # nutrientlist2 = [x for x in nutrientlist if not x.startswith(prefix)]
        products = queryCollection.triply_query_filter(nutrientlist)

        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template("symptomsV2.html", nutrients=nutrients, userage=userDAO.getprofileage(),
                                   useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(),
                                   products_conjuction=products, symptom=symptom, symptoms=symptoms)
    else:
        return render_template("symptomsV2_error.html", userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(),
                               symptom=symptom, symptoms=symptoms)


# redirect to nutrient_filter.html
@app.route("/filterredirect", methods=['GET', 'POST'])
def filterredirect():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")

    username = cur.fetchone()
    con.close()

    if redirecttologin() == None:
        return render_template('index.html')
    else:
        return render_template("nutrient_filter.html", username=username['name'], userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# function for the nutrient_filter.html. Gets a list of search parameters (nutrients) and returns a table with the
# belonging products
@app.route('/filternut/', methods=['GET', 'POST'])
def filternut():
    misc = list()
    vitamin = list()
    minerals = list()
    fats = list()
    carbos = list()
    vitaminb = list()
    all = list()
    if request.method == 'POST':
        misc = request.form.getlist('misc')
        vitamin = request.form.getlist('vitamin')
        vitaminb = request.form.getlist('vitaminb')
        minerals = request.form.getlist('minerals')
        fats = request.form.getlist('fats')
        carbos = request.form.getlist('carbos')

    all = carbos + misc + minerals + fats + vitamin + vitaminb

    allfiltered = str(all)
    allfiltered1 = allfiltered.replace("[", "")
    allfiltered2 = allfiltered1.replace("]", "")

    products = queryCollection.triply_query_filter(all)

    return render_template("nutrient_filter.html", products=products, userage=userDAO.getprofileage(),
                           useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(), all=all,
                           allfiltered=allfiltered2)


# function that contains the parameters needed for the query for the nutritional information of a given product
@app.route('/query/<product>, <unit>', methods=['POST', 'GET'])
def sparql_query(product, unit):
    deleteexpired()
    age = userDAO.getUserAge()
    gender = userDAO.getUserGenderGroup()
    activity = userDAO.getUserActivityGroup()
    weight = userDAO.getUserWeight()

    category1 = "vitamin"
    category2 = "lipid"
    category3 = "carbohydrates"
    category4 = "minerals"
    label = str(product)
    if "ntr:" in label:
        label = label.replace("ntr:", "")

    vitamins = queryCollection.triply_query_nutrient_products_percategory(age, gender, activity, category1, product,
                                                                          unit)
    fats = queryCollection.triply_query_nutrient_products_percategory(age, gender, activity, category2, product, unit)
    carbohydrates = queryCollection.triply_query_nutrient_products_percategory(age, gender, activity, category3,
                                                                               product, unit)
    minerals = queryCollection.triply_query_nutrient_products_percategory(age, gender, activity, category4, product,
                                                                          unit)
    proteins = queryCollection.triply_query_nutrient_products_protein(age, gender, weight, product, unit)

    minerallist = list()
    vitaminslist = list()
    fatslist = list()
    carbolist = list()
    nutrients = list()
    products = list()
    otherslist = list()
    articles_url = list()
    articles_label = list()
    articles = list()

    for item in vitamins:
        vitaminslist.append(item)

    for item in fats:
        fatslist.append(item)

    for item in carbohydrates:
        carbolist.append(item)

    for item in minerals:
        minerallist.append(item)

    for item in proteins:
        carbolist.append(item)

    username = userDAO.getUserName()
    produkte = userDAO.getProducts()
    ingredients2 = userDAO.getIngredients()

    if redirecttologin() == None:
        return render_template('index.html')

    else:
        return render_template('nutrient.html', results=nutrients, products=products, userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything()
                               , articles_url=articles_url, articles_label=articles_label, articles=articles,
                               username=username, produkte=produkte, ingredients2=ingredients2, product=product,
                               vitamins=vitaminslist, minerals=minerallist, fats=fatslist, carbohydrates=carbolist,
                               otherslist=otherslist, label=label)


# this function represents the button click, which redirects to the 'sparql_query' with the needed parameters
@app.route('/query_param/', methods=['POST', 'GET'])
def query_param():
    product = request.form['nm']
    label = request.form['nm']
    unit = request.form['unit']
    actualunit = float(unit) / 100

    if "http://knowrob.org/kb/product-taxonomy.owl" in product:
        product = product.replace("http://knowrob.org/kb/product-taxonomy.owl#", "ptx:")

    if "http://purl.org/heals/ingredient/" in product:
        product = product.replace("http://purl.org/heals/ingredient/", "ingredient:")

    if "http://localhost/usda_food_nutritions#" in product:
        product = product.replace("http://localhost/usda_food_nutritions#", "ntr:")

    if "http://knowrob.org/kb/product-taxonomy.owl" in label:
        label = label.replace("http://knowrob.org/kb/product-taxonomy.owl#", "")
        label = label.replace((""), ", ")

    if "http://purl.org/heals/ingredient/" in label:
        label = label.replace("http://purl.org/heals/ingredient/", "")
        label = label.replace((""), ", ")

    if "http://purl.org/ProductKG/food-nutrition#" in label:
        label = label.replace("http://purl.org/ProductKG/food-nutrition#", "")
        label = label.replace(("_"), ", ")

    if "http://purl.org/ProductKG/food-nutrition#" in product:
        product = product.replace("http://purl.org/ProductKG/food-nutrition#", "")
        # product = product.capitalize()

    if "http://localhost/usda_food_nutritions#" in label:
        label = label.replace("http://localhost/usda_food_nutritions#", "")
        label = label.replace(("_"), ", ")

    return redirect(url_for('sparql_query', product=product, unit=actualunit))


app.secret_key = 'nutron'

if __name__ == "__main__":
    app.run()
