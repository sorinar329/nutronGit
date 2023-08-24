import sqlite3 as sql
from flask import session
import os.path

# Path of the Database "user.db"

db_path = ("/var/www/nutronGit/user.db")
#db_path = ('user.db')


def getEverything():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select * from 'user' where name = ?", (username, ))
    everything = cur.fetchall()
    return everything


def getprofileage():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select age from 'user' where name = ?", (username, ))
    userage = cur.fetchone()
    profileage = userage['age']
    profileage = profileage.replace("Ewachsene", "")
    profileage = profileage.replace("_", "")
    profileage = profileage.replace("bis unter", "to")
    profileage = profileage.replace("Jahre" , "years")

    return profileage



def getprofileactivity():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select activity from 'user' where name = ?", (username, ))
    useractivity = cur.fetchone()
    profileactivity = useractivity['activity']
    if profileactivity == "mid":
        profileactivity = "average activity"
    elif profileactivity == "high":
        profileactivity = "high activity"
    elif profileactivity == "low":
        profileactivity = "low activity"

    return profileactivity




# Gets the UserName that is currently in the Database
def getUserName():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select name from 'user'")
    username = cur.fetchone()
    return username['name']

# Gets the age of the user that is currently in the database
def getUserWeight():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select weight from 'user' where name = ?", (username,))
    weight = cur.fetchone()
    return weight['weight']

# gets the age of the user that is currently in the database
def getUserAge():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select age from 'user' where name = ?", (username,))
    age = cur.fetchone()
    return age['age']


# gets the gender of the user that is currently in the database
def getUserGender():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select g from 'user' where name = ?", (username,))
    g = cur.fetchone()
    return g['g']


# gets the activity of the current user in the database
def getUserActivity():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    username = session['username']
    cur.execute("select activity from 'user' where name = ?", (username,))
    activity = cur.fetchone()
    return activity['activity']

# get the products from the database
def getProducts():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from 'products'")
    data = cur.fetchall()
    return data

# get the recipes from the database
def getRecipes():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from 'recipes'")
    data = cur.fetchall()
    return data

# get the ingredients from the database
def getIngredients():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from 'ingredients'")
    data = cur.fetchall()
    return data

def getSymptoms():
    conn = sql.connect(db_path)
    conn.row_factory = sql.Row
    cur = conn.cursor()
    cur.execute("select * from 'symptoms'")
    data = cur.fetchall()
    return data

# classifies the user and returns the useragegroup of the user
def getUserAgeGroup():
    userage = getUserAge()
    if 15 <= int(userage) < 19:
        useragegroup = "Jugendliche_15_bis_unter_19_Jahre"
        return useragegroup
    if 19 <= int(userage) < 25:
        useragegroup = "Ewachsene_19_bis_unter_25_Jahre"
        return useragegroup
    if 25 <= int(userage) < 51:
        useragegroup = "Ewachsene_25_bis_unter_51_Jahre"
        return useragegroup
    if 51 <= int(userage) < 65:
        useragegroup = "Ewachsene_51_bis_unter_65_Jahre"
        return useragegroup
    if 7 <= int(userage) < 10:
        useragegroup = "Kinder_7_bis_unter_10_Jahre"
        return useragegroup
    if 10 <= int(userage) < 13:
        useragegroup = "Kinder_10_bis_unter_13_Jahre"
        return useragegroup
    if 13 <= int(userage) < 15:
        useragegroup = "Kinder_13_bis_unter_15_Jahre"
        return useragegroup

# classifies the user and returns the useractivitygroup of the user
def getUserActivityGroup():
    useractivity = getUserActivity()
    if useractivity == "low":
        useractivity_group = "has_low_intake"
        return useractivity_group
    if useractivity == "mid":
        useractivity_group = "has_medium_intake"
        return useractivity_group
    if useractivity == "high":
        useractivity_group = "has_high_intake"
        return useractivity_group

# classifies the user and returns the gender of the user
def getUserGenderGroup():
    usergender = getUserGender()
    if usergender == "m":
        usergender_group = "male"
        return usergender_group
    if usergender == "f":
        usergender_group = "female"
        return usergender_group
    else:
        return usergender
