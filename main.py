#!/usr/bin/env python3.10
import csv

from flask import Flask, render_template, request, url_for, redirect, session
import sqlite3 as sql
from datetime import datetime
from datetime import timedelta
import queryCollection
import userDAO

app = Flask(__name__)

#conn = sql.connect('/var/www/nutron/user.db')

db_path = 'user.db'
#db_path = '/var/www/nutron/user.db'
#db_path = "E:/nutronGit/user.db"

# managing the database
def databasemanager():
        conn = sql.connect(db_path)
        #database will drop at start of the app
        conn.execute('DROP TABLE IF EXISTS user')
        conn.execute('DROP TABLE IF EXISTS products')
        conn.execute('DROP TABLE IF EXISTS recipes')
        conn.execute('DROP TABLE IF EXISTS ingredients')
        conn.execute('DROP TABLE IF EXISTS symptoms')

        #creating the tables in the database
        conn.execute('Create Table user(name TEXT, age TEXT, g TEXT, activity TEXT, weight TEXT, datum TEXT)')
        conn.execute('Create Table products(class TEXT, label TEXT)')
        conn.execute('Create Table recipes(class TEXT, label TEXT)')
        conn.execute('CREATE Table ingredients(class TEXT, label TEXT)')
        conn.execute('CREATE Table symptoms(class TEXT, label TEXT)')
        conn.close()


databasemanager()

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



# database filled with products and recipes. this happens before the first request.

def fill_database_products():
    with app.app_context():
        con = sql.connect(db_path)
        cur = con.cursor()

        recipes = queryCollection.query_recipes()
        usda = queryCollection.triply_query_products()
        symptom_data = queryCollection.triply_query_symptoms_data()

        for item in usda:
            cur.execute("INSERT INTO ingredients(class, label) VALUES(?,?)", (item["food"]["value"], item["label"]["value"]))
            con.commit()

        for item in recipes:
            cur.execute("INSERT INTO recipes(class, label) VALUES(?,?)", (item["class"]["value"], item["label"]["value"]))
            con.commit()

        for item in symptom_data:
            cur.execute("INSERT INTO symptoms(class, label) VALUES(?,?)", (item["class"]["value"], item["label"]["value"]))
            con.commit()

        con.close()

@app.route('/')
def hello():
   return render_template("new_homepage.html")

@app.route('/home', methods=['POST','GET'])
def backhome():
    if request.method == 'POST':
        return render_template('new_homepage.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    return render_template('contact.html')


@app.route('/disclaimer', methods=['POST', 'GET'])
def disclaimer():
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



#logout function
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


#inserting user data into the database
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

                    cur.execute("INSERT INTO user (name,age,g,activity, weight, datum)VALUES(?, ?, ?,?,?,?)",(name,age,gender,activity, weight, datetime.now()) )

                    con.commit()
                    msg = "User succesfully Added"
                    #con.close()
            except:
                con.rollback()
                msg = "error in insert operation"

            finally:
                return render_template("nutron/homepage.html", msg=msg, username=name,userage=userDAO.getprofileage(),
                                       useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything())





@app.route('/homepage', methods=['POST', 'GET'])
def homepage():
    deleteexpired()
    if request.method == 'POST':
        if redirecttologin() == None:
            return render_template('index.html')
        else:
            return render_template('nutron/homepage.html', userage=userDAO.getprofileage(),
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything())



# Redirect to nutrient.html
@app.route("/name", methods = ['GET', 'POST'])
def name():
    deleteexpired()
    con = sql.connect(db_path)
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select name from 'user'")

    username = cur.fetchone()
    con.close()

    #products and ingredients from the database
    ingredients = userDAO.getIngredients()
    produckte = userDAO.getProducts()
    if redirecttologin() == None:
        return render_template('index.html')
    else:
        if 'username' in session:
            return render_template("nutrient.html", username=username['name'], produckte=produckte, ingredients=ingredients,
                           userage=userDAO.getprofileage(),useractivity=userDAO.getprofileactivity(),
                           everything=userDAO.getEverything())
        else:
            return render_template("index.html")


#redirect to symptoms.html
@app.route("/symptoms", methods = ['GET', 'POST'])
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
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything(),
                                   symptoms = symptoms)



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
        #prefix = "http://purl.org/ProductKG/disease"
        #nutrientlist2 = [x for x in nutrientlist if not x.startswith(prefix)]
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
@app.route("/filterredirect", methods = ['GET', 'POST'])
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
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything())




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
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything(), all=all,
                           allfiltered=allfiltered2)



# redirect to the recipe.html
@app.route("/recipes", methods = ['GET', 'POST'])
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
        return render_template("recipesV2.html", username=username['name'], recipes=recipes,userage=userDAO.getprofileage(),
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything())


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

    return redirect(url_for('recipequery_result', recipe=recipe, portions=portions,userage=userDAO.getprofileage(),
                                   useractivity=userDAO.getprofileactivity() ,everything=userDAO.getEverything(),
                            recipe_shown=recipe_shown))


# the function for the recipe query. returns a list for all catergories which is needed for the table in recipe.html
@app.route('/recipequery/<recipe>,<portions>', methods=['POST','GET'])
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
    return render_template('recipesV2.html', all_prods=all_prods, username=username, recipess=recipess, recipecoveragelist=recipecoveragelist,
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

@app.route('/experiment_chabot', methods=['GET', 'POST'])
def chatbot():
    return render_template('new_experiment.html')

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
    if lang == "ger" :
        render = 'finished_survey.html'
    else:
        render = 'finished_survey_en.html'
    #render = "finished_survey.html" if lang == "ger" else render = "finished_survey_en.html"
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
    with open(w, "a", newline= "") as f:
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
    with open(w, "a", newline= "") as f:
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
            output = list(zip(p,f))
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
    if request.method=="POST":
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
    if request.method=="POST":
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



app.secret_key= 'nutron'


if __name__ == "__main__":
   app.run()
