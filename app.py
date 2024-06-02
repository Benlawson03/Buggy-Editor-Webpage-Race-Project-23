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

# Load JSON data
with open('types.json', 'r') as file:
    types_data = json.load(file)

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
            armour TEXT,
            attack TEXT,
            power_type TEXT,
            special TEXT,
            tyres TEXT,
            
            total_cost INTEGER
        )''')
        con.commit()
        
        # Check if 'armour', 'attack', 'power_type', 'special' and 'tyres' column exists, and add it if it doesn't
        cur.execute("PRAGMA table_info(buggies)")
        columns = [column[1] for column in cur.fetchall()]
        if 'armour' not in columns:
            cur.execute("ALTER TABLE buggies ADD COLUMN armour TEXT")
            con.commit()
            
        cur.execute("PRAGMA table_info(buggies)")
        columns = [column[1] for column in cur.fetchall()]
        if 'attack' not in columns:
            cur.execute("ALTER TABLE buggies ADD COLUMN attack TEXT")
            con.commit()
            
        cur.execute("PRAGMA table_info(buggies)")
        columns = [column[1] for column in cur.fetchall()]
        if 'power_type' not in columns:
            cur.execute("ALTER TABLE buggies ADD COLUMN power_type TEXT")
            con.commit()
            
        cur.execute("PRAGMA table_info(buggies)")
        columns = [column[1] for column in cur.fetchall()]
        if 'special' not in columns:
            cur.execute("ALTER TABLE buggies ADD COLUMN special TEXT")
            con.commit()
            
        cur.execute("PRAGMA table_info(buggies)")
        columns = [column[1] for column in cur.fetchall()]
        if 'tyres' not in columns:
            cur.execute("ALTER TABLE buggies ADD COLUMN tyres TEXT")
            con.commit()



def calculate_cost(qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, armour, attack, power_type, special, tyres):
    # Define cost rules
    wheel_cost = 0    # example cost per wheel
    color_cost = 0   # example cost for flag color
    pattern_cost = 0  # example cost for flag pattern
    algo_cost = 0  # example cost for algo

    # Get costs from JSON data
    algo_cost = types_data["algo"][algo]["cost"]
    armour_cost = types_data["armour"][armour]["cost"]
    attack_cost = types_data["attack"][attack]["cost"]
    power_type_cost = types_data["power_type"][power_type]["cost"]
    special_cost = types_data["special"][special]["cost"]
    tyres_cost = types_data["tyres"][tyres]["cost"]

    # Calculate total cost
    total_cost = (int(qty_wheels) * wheel_cost) + color_cost + pattern_cost + algo_cost + armour_cost + attack_cost + power_type_cost + special_cost + tyres_cost
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
@app.route('/new', methods=['POST', 'GET']) 
def create_buggy():
    if request.method == 'GET':
        with sql.connect(DATABASE_FILE) as con:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
            record = cur.fetchone()
            if record:
                return render_template("buggy-form.html", buggy=record)
            else:
                return render_template("buggy-form.html", buggy={})
    elif request.method == 'POST':
        error_messages = {}
        qty_wheels = request.form['qty_wheels'].strip()
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        algo = request.form['algo']
        armour = request.form['armour']
        attack = request.form['attack']
        power_type = request.form['power_type']
        special = request.form['special']
        tyres = request.form['tyres']

        if not qty_wheels.isdigit():
            error_messages['error_qty_wheels'] = "Please enter an integer for the number of wheels"
        
        if flag_color == "--option--":
            error_messages['error_flag_color'] = "Flag colour option has been left unchosen"
        
        if flag_color_secondary == "--option--":
            error_messages['error_secondary_flag_color'] = "Secondary flag colour option has been left unchosen"
        
        if flag_pattern == "--option--":
            error_messages['error_flag_pattern'] = "Flag pattern option has been left unchosen"
        
        if algo == "--option--":
            error_messages['error_algo'] = "Algo option has been left unchosen"
            
        if armour == "--option--":
            error_messages['error_armour'] = "Armour option has been left unchosen"
            
        if attack == "--option--":
            error_messages['error_attack'] = "Attack option has been left unchosen"
            
        if power_type == "--option--":
            error_messages['error_power_type'] = "Power type option has been left unchosen"

        if special == "--option--":
            error_messages['error_special'] = "Sepcial option has been left unchosen"
            
        if tyres == "--option--":
            error_messages['error_tyres'] = "Tyres option has been left unchosen"
        
        if error_messages:
            return render_template("buggy-form.html", **error_messages, buggy=request.form)

        # Calculate the cost of the buggy
        try:
            total_cost = calculate_cost(qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, armour, attack, power_type, special, tyres)
        except Exception as e:
            return render_template("buggy-form.html", error_calculation=f"Error calculating cost: {str(e)}", buggy=request.form)

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    """UPDATE buggies 
                    SET qty_wheels=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, algo=?, armour=?, attack=?, power_type=?, special=?, tyres=?, total_cost=? 
                    WHERE id=?""",
                    (qty_wheels, flag_color, flag_color_secondary, flag_pattern, algo, armour, attack, power_type, special, tyres, total_cost, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"
        except Exception as e:
            con.rollback()
            msg = f"Error in update operation: {str(e)}"
        finally:
            con.close()

        return render_template("updated.html", msg=msg)






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
    with sql.connect(DATABASE_FILE) as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
        record = cur.fetchone()
        if record:
            return render_template("buggy.html", buggy=record)
        else:
            return render_template("buggy.html", buggy={})




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
    with sql.connect(DATABASE_FILE) as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID,))
        record = cur.fetchone()
        if record:
            buggies = dict(record)
            return jsonify({key: val for key, val in buggies.items() if val != "" and val is not None})
        else:
            return jsonify({})

if __name__ == '__main__':
    init_db()
    alloc_port = os.environ.get('CS1999_PORT') or 5001
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
