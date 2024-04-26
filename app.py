from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to read JSON data from file
def read_json():
    try:
        with open('data.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data

# Function to write JSON data to file
def write_json(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Initialize the database schema if it doesn't exist
def init_db():
    if not os.path.exists('inventory.db'):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE inventory (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            thumbnail TEXT NOT NULL)''')
        conn.commit()
        conn.close()

# Initialize the database when the application starts
init_db()

# Route to display inventory list
@app.route('/')
def inventory_list():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM inventory')
    inventory = cursor.fetchall()
    conn.close()
    return render_template('inventory_list.html', inventory=inventory)

# Route to display item details
@app.route('/item/<int:item_id>')
def item_details(item_id):
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM inventory WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return render_template('item_details.html', item=item)
    else:
        return "Item not found", 404

# Route to add a new item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        thumbnail = request.form['thumbnail']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO inventory (name, description, thumbnail) VALUES (?, ?, ?)', (name, description, thumbnail))
        conn.commit()
        conn.close()
        
        return redirect(url_for('inventory_list'))
    return render_template('add_item.html')

# Route to add a code number
@app.route('/add_code', methods=['POST'])
def add_code():
    req_data = request.get_json()
    if 'code' not in req_data:
        return jsonify({'error': 'Code number is missing'}), 400
    
    data = read_json()
    code = req_data['code']
    data.append({'code': code})
    write_json(data)
    
    return jsonify({'message': 'Code number added successfully'}), 201

if __name__ == '__main__':
    app.run(host='192.168.1.14',port=8080, debug=True)
