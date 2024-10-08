#!/usr/bin/env python3.10
import csv
import numpy
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import sqlite3 as sql
from pyzbar import pyzbar
from src.owlvisualizer.graph import graph
from src.owlvisualizer.graph import coloring
#from src.owlvisualizer import query_builder
import cv2
from datetime import datetime
from datetime import timedelta
from src.nutron import queryCollection, textManipulation, userDAO
import os
from rdflib import Graph, OWL, RDFS, RDF
import random

app = Flask(__name__)

# conn = sql.connect('/var/www/nutron/user.db')
db_path = '/var/www/nutronGit/user.db'
# db_path = "E:/nutronGit/user.db"
# db_path = 'C:/Users/meike/Downloads/nutronGit/user.db'
#db_path = "user.db"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './pictures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# --------------------------- PRODUCT SCAN BACKEND ---------------------------
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


# --------------------------- DATABASE STUFF ---------------------------
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


def redirecttologin():
    username = session['username']
    conn = sql.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * from 'user' where name = ?", (username,))
    data = cursor.fetchone()
    return data


# --------------------------- NutrOn ---------------------------
@app.route('/')
def hello():
    return render_template("new_homepage.html")


@app.route('/home', methods=['POST', 'GET'])
def backhome():
    if request.method == 'POST':
        return render_template('new_homepage.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    return render_template('new_contact.html')


@app.route('/disclaimer', methods=['POST', 'GET'])
def disclaimer():
    return render_template('new_disclaimer.html')


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
        return render_template("new_homepage.html")


@app.route('/logouttohome', methods=['POST', 'GET'])
def logouttohome():
    if request.method == 'POST':
        username = session['username']
        # database connection
        conn = sql.connect(db_path)
        conn.execute("DELETE from 'user' where name = ?", (username,))
        conn.commit()
        conn.close()
        return render_template("new_homepage.html")


@app.route('/nutron_landingpage', methods=['POST', 'GET'])
def nutron_landingpage():
    return render_template("nutron/new_nutronlandingpage.html")


@app.route("/nutron_continue_without_registration", methods=["POST", "GET"])
def nutron_continue_without_registration():
    return render_template("nutron/new_nutron_continue_without_account.html")


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
        return render_template("nutron/new_nutron_continue_without_account_failed.html")
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
                return render_template("nutron/homepage.html", msg=msg, username=name, userage=userDAO.getprofileage(),
                                       useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    deleteexpired()
    if request.method == 'POST':
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template('nutron/homepage.html', userage=userDAO.getprofileage(),
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



#the function for getting the right nutrients for a given symptom
@app.route('/treatmentnutrient/', methods = ['GET', 'POSt'])
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


# redirect to the recipe.html
@app.route("/recipes", methods=['GET', 'POST'])
def recipes():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")

    username = cur.fetchone()
    con.close()

    recipes = userDAO.getRecipes()
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        return render_template("recipesV2.html", username=username['name'], recipes=recipes,
                               userage=userDAO.getprofileage(),
                               useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything())


# function for getting the needed parameters for the query. calls another function 'recipequery_result' and gives the
# needed parameters
@app.route('/recipe_querry/', methods=['POST', 'GET'])
def actualquery_recipe():
    recipe = request.form['rr']
    recipe_shown = request.form['rr']
    portions = int(request.form['portions'])
    if "http://purl.org/heals/ingredient/" in recipe:
        recipe = recipe.replace("http://purl.org/heals/ingredient/", "ingredient:")

    if "http://purl.org/heals/ingredient/" in recipe_shown:
        recipe_shown = recipe.replace("http://purl.org/heals/ingredient/", "")

    return redirect(url_for('recipequery_result', recipe=recipe, portions=portions, userage=userDAO.getprofileage(),
                            useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(),
                            recipe_shown=recipe_shown))


# the function for the recipe query. returns a list for all catergories which is needed for the table in recipe.html
@app.route('/recipequery/<recipe>,<portions>', methods=['POST', 'GET'])
def recipequery_result(recipe, portions):
    results = queryCollection.query_products_in_recipe(recipe, portions)
    gender = userDAO.getUserGenderGroup()
    age = userDAO.getUserAge()
    activity = userDAO.getUserActivityGroup()
    weight = userDAO.getUserWeight()
    recipecoverage = queryCollection.coverage_recipe(gender, age, activity, recipe, portions)
    category1 = "Vitamin"
    category2 = "Lipid"
    category3 = "Carbohydrates"
    category4 = "Minerals"
    proteins = queryCollection.query_recipe_protein(gender, age, recipe, portions)
    vitamins = queryCollection.query_nutrient_recipe_percategory(gender, age, activity, category1, recipe, portions)
    carbos = queryCollection.query_nutrient_recipe_percategory(gender, age, activity, category3, recipe, portions)
    fats = queryCollection.query_nutrient_recipe_percategory(gender, age, activity, category2, recipe, portions)
    minerals = queryCollection.query_nutrient_recipe_percategory(gender, age, activity, category4, recipe, portions)
    others = queryCollection.recipe_coverage_others(gender, age, activity, recipe, portions)
    label = recipe
    if "ingredient" in label:
        label = label.replace("ingredient:", "")
    vitaminlist = list()
    minerallist = list()
    carboslist = list()
    fatslist = list()

    all_prods = list()
    recipecoveragelist = list()
    for item in recipecoverage:
        recipecoveragelist.append(item)
    for item in results:
        all_prods.append(item)
    for item in vitamins:
        vitaminlist.append(item)
    for item in carbos:
        carboslist.append(item)
    for item in fats:
        fatslist.append(item)
    for item in minerals:
        minerallist.append(item)
    for item in proteins:
        carboslist.append(item)
    username = userDAO.getUserName()
    recipess = userDAO.getRecipes()
    return render_template('recipesV2.html', all_prods=all_prods, username=username, recipess=recipess,
                           recipecoveragelist=recipecoveragelist,
                           vitaminlist=vitaminlist, fatslist=fatslist, carboslist=carboslist, minerallist=minerallist,
                           userage=userDAO.getprofileage(),
                           useractivity=userDAO.getprofileactivity(), everything=userDAO.getEverything(),
                           recipe=recipe, others=others, label=label, portions=portions)


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


# --------------------------- Surveys STUFF ---------------------------
@app.route('/set_language', methods=['POST', 'GET'])
def set_language():
    req = request.form['langButton']
    print(req)
    if request.method == 'POST':
        req = request.form['langButton']
        print(req)
        if req == 'English':
            print("I selected English")
            return render_template('survey_en.html')
        elif req == 'German':
            print('I selected German')
            return render_template('survey.html')

    return render_template('survey.html')


@app.route('/surveys_and_experiments', methods=['GET', 'POST'])
def surveys_and_experiments():
    return render_template('new_surveys_experiments.html')

html1_count = 0
html2_count = 0
total_visits = 0

@app.route('/randomize_chatroom')
def redirect_random():
    global html1_count, html2_count, total_visits
    total_visits += 1


    html1_percentage = (html1_count / total_visits) * 100 if total_visits > 0 else 0
    html2_percentage = (html2_count / total_visits) * 100 if total_visits > 0 else 0


    if html1_percentage >= 60:
        chosen = 'html2'
    elif html2_percentage >= 40:
        chosen = 'html1'
    else:
        chosen = random.choices(['html1', 'html2'], weights=[0.6, 0.4])[0]

    if chosen == 'html1':
        html1_count += 1
        return redirect(url_for('chatbot_robot'))
    else:
        html2_count += 1
        return redirect(url_for('chatbot_human'))

@app.route('/chatbot_robot', methods=['GET', 'POST'])
def chatbot_robot():
    return render_template('chatroom_robot.html')


@app.route('/chatbot_human', methods=['GET', 'POST'])
def chatbot_human():
    return render_template('chatroom_human.html')


@app.route('/survey', methods=['POST', 'GET'])
def survey():
    return render_template('surveys/survey.html')


@app.route('/finish_survey', methods=['POST', 'GET'])
def finish_survey():
    lang = request.form["language"]
    getUsageOfRobotos(lang)
    getDailyOfRobots(lang)
    getfirstOpinion(input.opinionLabel1, input.opinionCheckboxes1, lang)
    getfirstOpinion(input.opinionLabel2, input.opinionCheckboxes2, lang)
    getMissingRobots(lang)
    render = ""
    if lang == "ger":
        render = 'finished_survey.html'
    else:
        render = 'finished_survey_en.html'
    # render = "finished_survey.html" if lang == "ger" else render = "finished_survey_en.html"
    return render_template(render)


def writeTOCSV_en(l, which):
    w = ""
    if which == "use":
        w = "survey/survey_usage_en.csv"
    elif which == "daily":
        w = "survey/survey_daily_en.csv"
    elif which == "missing":
        w = "survey/survey_missing_en.csv"
    else:
        w = "survey/survey_opinion_en.csv"
    with open(w, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(l)


def writeTOCSV_ger(l, which):
    w = ""
    if which == "use":
        w = "survey/survey_usage_de.csv"
    elif which == "daily":
        w = "survey/survey_daily_de.csv"
    elif which == "missing":
        w = "survey/survey_missing_de.csv"
    else:
        w = "survey/survey_opinion_de.csv"
    with open(w, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(l)


def getMissingRobots(lang):
    if request.method == "POST":
        try:
            output = list()
            p = list()
            f = list()
            place = request.form['placeOfMissing']
            func = request.form['functionOfMissing']
            p.append(place)
            f.append(func)
            output = list(zip(p, f))
            writeTOCSV_ger(output, "missing") if lang == "ger" else writeTOCSV_en(output, "missing")
        except Exception as e:
            print("Missing: " + str(e))


def getfirstOpinion(label, checkbox, lang):
    if request.method == "POST":
        try:
            opinion = list()
            for i in checkbox:
                if request.form.get(i[0]) == "on":
                    opinion.append("Yes")
                elif request.form.get(i[1]) == "on":
                    opinion.append("No")
                elif request.form.get(i[2]) == "on":
                    opinion.append("Unsure")
            zippedList = list(zip(label, opinion))
            writeTOCSV_ger(zippedList, "") if lang == "ger" else writeTOCSV_en(zippedList, "")
        except Exception as e:
            print(str(e))


def getDailyOfRobots(lang):
    if request.method == "POST":
        try:
            quantity = list()
            function = list()
            miscNum = request.form['quantitiyMisc']
            miscName = request.form['nameOfMisc']
            miscFunc = request.form['functionMisc']

            for i in input.dailyQuanitity:
                num = request.form[i]
                quantity.append(num)
            for n in input.dailyFunction:
                func = request.form[n]
                function.append(func)
            zippedList = list(zip(input.dailyLabel, quantity, function))
            zippedList.append(('Misc', miscNum, miscFunc, miscName))
            writeTOCSV_ger(zippedList, "daily") if lang == "ger" else writeTOCSV_en(zippedList, "daily")
        except Exception as e:
            print(str(e))


def getUsageOfRobotos(lang):
    if request.method == "POST":
        try:
            quantitiy = list()
            function = list()
            miscNum = request.form['usageMisc']
            miscFunc = request.form['usageMiscFunction']
            miscName = request.form['nameOfMisc2']
            for i in input.usageQuantitiy:
                num = request.form[i]
                print(num)
                quantitiy.append(num)
            for n in input.usageFunction:
                func = request.form[n]
                print(func)
                function.append(func)
            zippedList = list(zip(quantitiy, function))
            zippedList.append(('Misc', miscNum, miscFunc, miscName))

            writeTOCSV_ger(zippedList, "daily") if lang == "ger" else writeTOCSV_en(zippedList, "daily")

        except Exception as e:
            print(str(e))


@app.route('/contact_survey', methods=['POST', 'GET'])
def contact_survey():
    return render_template('contact_survey.html')


@app.route('/contact_survey_en', methods=['POST', 'GET'])
def contact_survey_en():
    return render_template('contact_survey_em.html')


@app.route('/about_survey', methods=['POST', 'GET'])
def about_survey():
    return render_template('about_survey.html')


@app.route('/about_survey_en', methods=['POST', 'GET'])
def about_survey_en():
    return render_template('about_survey_en.html')



# --------------------------- GraphViz STUFF ---------------------------

@app.route('/graphviz')
def graph_viz():
    return render_template("owlvisualizer/graphviz.html")


def get_intersection(dict1, dict2):
    dict1_ids = {node['id'] for node in dict1['nodes']}
    dict2_ids = {node['id'] for node in dict2['nodes']}
    intersection_ids = dict1_ids.intersection(dict2_ids)

    intersection_nodes = [node for node in dict1['nodes'] if node['id'] in intersection_ids]

    intersection_edges = [edge for edge in dict1['edges'] if
                          edge['from'] in intersection_ids and edge['to'] in intersection_ids]

    return {'nodes': intersection_nodes, 'edges': intersection_edges}

cached_data = None
cached_status = False


@app.route('/get_graph_data_rdf')
def get_graph_data_rdf():
    global cached_data
    global cached_status
    file_path = [os.path.join("/home/sorin/code/nutronGit/nutronGit/data", file) for file in
                 os.listdir("/home/sorin/code/nutronGit/nutronGit/data")]

    knowledge_graph = Graph()
    knowledge_graph.parse(file_path[0])
    if not cached_status:
        if cached_data is None:

            graph_visualize = graph.get_graph_to_visualize(knowledge_graph)
            coloring.color_classes(graph_visualize)
            coloring.color_parameters(graph_visualize)
            cached_data = {'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")}
            cached_status = True
            return jsonify(cached_data)
    if cached_status:
        graph_visualize = graph.get_graph_to_visualize(knowledge_graph)
        coloring.color_classes(graph_visualize)
        coloring.color_parameters(graph_visualize)
        cached_data_new = {'nodes': graph_visualize.get("nodes"), 'edges': graph_visualize.get("edges")}


        filtered_data = get_intersection(cached_data, cached_data_new)


        return jsonify(cached_data_new)


@app.route('/suggest_classes', methods=["GET"])
def suggest_classes():
    graph_visualize = graph.get_graph_to_visualize()
    classes = [i.get('id') for i in graph_visualize.get("nodes")]
    print(classes)
    return jsonify(classes)


@app.route('/query_builder', methods=["GET"])
def suggest_triples():
    qb = query_builder.get_query_builder()
    suggestions = qb.mock_suggestion2()
    selected_option = request.args.get('selectedOption')
    return jsonify(suggestions)


@app.route('/upload', methods=['POST'])
def upload_file_graph():
    # Delete existing files in the folder
    folder_path = '/home/sorin/code/nutronGit/nutronGit/data/'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to delete {file_path}: {e}'})

    # Save the new uploaded file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    file.save(os.path.join(folder_path, file.filename))

    return jsonify({'filename': file.filename})



app.secret_key = 'nutron'

if __name__ == "__main__":
    app.run()
