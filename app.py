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

        con = sql.connect(DATABASE_FILE)                          #
        con.row_factory = sql.Row                                 #
        cur = con.cursor()                                        #
        cur.execute("SELECT * FROM buggies")                      #
        record = cur.fetchone();                                  #
        return render_template("buggy-form.html", buggy = record) # passes the data from database into
#buggy-form (this sorts out all values in buggy form so dont worry about any of the requirements individually)
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels'].strip()
        if not qty_wheels.isdigit():
            # Error handling: qty_wheels is not a valid integer
            error_msg = "Number of wheels must be a valid integer."
            # Render the form again with an error message
            return render_template("buggy-form.html", error_qty_wheels="Please enter an integer for the number of wheels")
        flag_color = request.form['flag_color'] ##
        if flag_color == "--option--":
            # Error handling: flag colour has not been chosen
            error_flag_color = "Please select a valid flag color."
            # Render the form again with an error message
            return render_template("buggy-form.html", error_flag_color="Flag colour option has been left unchosen")     
        flag_color_secondary = request.form['flag_color_secondary']
        if flag_color_secondary == "--option--":
            # Error handling: secondary flag colour has not been chosen
            error_secondary_flag_color = "Please select a valid flag color."
            # Render the form again with an error message
            return render_template("buggy-form.html", error_secondary_flag_color="Secondary flag colour option has been left unchosen")
        flag_pattern = request.form['flag_pattern']
        if flag_pattern == "--option--":
            # Error handling: flag colour has not been chosen
            error_flag_pattern = "Please select a valid flag pattern."
            # Render the form again with an error message
            return render_template("buggy-form.html", error_flag_pattern="Flag pattern option has been left unchosen")
        algo = request.form['algo']
        if algo == "--option--":
            # Error handling: flag colour has not been chosen
            error_algo = "Please select a valid algo."
            # Render the form again with an error message
            return render_template("buggy-form.html", error_algo="algo option has been left unchosen")
        try:#
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, algo=? WHERE id=? ",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, DEFAULT_BUGGY_ID)
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

@app.route('/info')
def info():
    with open('defaults.json', 'r') as file:
        data1 = json.load(file)
    with open('types.json', 'r') as file:#
        data2 = json.load(file)#
    return render_template('info.html', data1=data1, data2=data2, server_url=BUGGY_RACE_SERVER_URL)    

    

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
