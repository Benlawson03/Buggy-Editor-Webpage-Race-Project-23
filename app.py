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

def init_db():
    with sql.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS buggies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qty_wheels INTEGER,
            flag_color TEXT,
            flag_color_secondary TEXT,
            flag_pattern TEXT,
            algo TEXT,
            total_cost INTEGER
        )''')
        con.commit()

if __name__ == "__main__":
    init_db()


def calculate_cost(qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo):
    # Define cost rules
    wheel_cost = 0    # example cost per wheel
    color_cost = 0   # example cost for flag color
    pattern_cost = 0  # example cost for flag pattern
    algo_cost = 0  # example cost for algo
    qty_tyres = 0
    power_units = 0
    aux_power_units = 0
    
    # Get costs from JSON data
    algo_cost = types_data["algo"][algo]["cost"]
    armour_cost = types_data["armour"][armour]["cost"]
    attack_cost = types_data["attack"][attack]["cost"]
    power_type_cost = types_data["power_type"][power_type]["cost"]
    aux_power_type_cost = types_data["power_type"][aux_power_type]["cost"] ## Aux is only the same as power type as its the same cost
    special_cost = types_data["special"][special]["cost"]
    tyres_cost = types_data["tyres"][tyres]["cost"]

# Calculate total cost
    total_cost = (
        (int(qty_wheels) * wheel_cost) +
        (int(qty_attacks) * attack_cost) +
        (int(tyres_cost) * int(qty_tyres)) +
        (int(power_type_cost) * int(power_units)) +
        (int(aux_power_type_cost) * int(aux_power_units)) +
        color_cost + pattern_cost + algo_cost + armour_cost + special_cost
    )
    return total_cost


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
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        algo = request.form['algo']
        armour = request.form['armour']
        attack = request.form['attack']
        power_type = request.form['power_type']
        aux_power_type = request.form['aux_power_type']
        special = request.form['special']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        qty_attacks = request.form['qty_attacks']
        power_units = request.form['power_units']
        aux_power_units = request.form['aux_power_units']
        
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
            error_messages['error_algo'] = "Algo option has been left unchosen"
            
        if armour == "--option--":
            error_messages['error_armour'] = "Armour option has been left unchosen"
            
        if attack == "--option--":
            error_messages['error_attack'] = "Attack option has been left unchosen"
            
        if power_type == "--option--":
            error_messages['error_power_type'] = "Power type option has been left unchosen"
            
        if aux_power_type == "--option--":
             error_messages['error_aux_power_type'] = "Aux power type option has been left unchosen"

        if special == "--option--":
            error_messages['error_special'] = "Sepcial option has been left unchosen"
            
        if tyres == "--option--":
            error_messages['error_tyres'] = "Tyres option has been left unchosen"
            
        if qty_tyres == "--option--":
            error_messages['error_qty_tyres'] = "Numbers of tyres option has been left unchosen"

        if qty_attacks == "--option--":
            error_messages['error_qty_attacks'] = "Number of attacks option has been left unchosen"
        
        if power_units == "--option--":
            error_messages['error_power_units'] = "Power units option has been left unchosen"

        if aux_power_units == "--option--":
            error_messages['error_aux_power_untis'] = "Aux power units option has been left unchosen"
        
        if error_messages:
            return render_template("buggy-form.html", **error_messages, buggy=request.form)

        # Calculate the cost of the buggy
        try:
            total_cost = calculate_cost(qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, armour, attack, power_type, aux_power_type, special, tyres, qty_tyres, qty_attacks, power_units, aux_power_units)
        except Exception as e:
            return render_template("buggy-form.html", error_calculation=f"Error calculating cost: {str(e)}", buggy=request.form)

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies set qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, algo=? WHERE id=? ",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, DEFAULT_BUGGY_ID)
                )
                con.commit()    
                msg = "Record successfully saved"
        except Exception as e:
            con.rollback()
            msg = f"Error in update operation: {str(e)}"
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
