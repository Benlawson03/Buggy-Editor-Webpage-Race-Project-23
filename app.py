from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql
import json

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"
JSON_FILE = "cs1999-defaults.json" # Path to JSON file

# Load JSON file content
with open(JSON_FILE, 'r') as f:
    json_data = json.load(f)

# Connect to SQLite database
DATABASE_FILE = "database.db"
con = sql.connect(DATABASE_FILE)
cur = con.cursor()

# Create a table to store JSON data
cur.execute('''CREATE TABLE IF NOT EXISTS json_data (
                id INTEGER PRIMARY KEY,
                data TEXT
            )''')

# Insert JSON data into the table
cur.execute("INSERT INTO json_data (data) VALUES (?)", (json.dumps(json_data),))
con.commit()

# Close connection
con.close()

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels']
        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=? WHERE id=?",
                    (qty_wheels, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the info of the buggy
#------------------------------------------------------------

@app.route('/info', methods = ['POST', 'GET'])
def info_buggy():
    # Fetch data from SQLite database
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone() 
    return render_template("info.html", buggy=record)

    

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })


# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ.get('CS1999_PORT') or 5001
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
