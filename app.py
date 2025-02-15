from flask import Flask, jsonify, request, render_template
from random_table_manager import RandomTableManager
import traceback

app = Flask(__name__)
manager = RandomTableManager('tables')

@app.route('/load', methods=['POST'])
def load_tables():
    data = request.json
    directory = data.get('directory', 'tables')
    manager.load(directory)
    return jsonify({"message": "Tables loaded successfully"}), 200

@app.route('/addTable', methods=['POST'])
def add_tables():
    try:
        data = request.json
        table = data.get('table')
        manager.add_table_tsv(table)
    except Exception as e:
        print(f"Error while adding table {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Error while adding table: {e}"}), 404
    else:
        return jsonify({"message": "Tables added successfully"}), 200

@app.route('/addTableJson', methods=['POST'])
def add_tables_json():
    try:
        data = request.json
        table = data.get('table')
        manager.add_table_json(table)
    except Exception as e:
        print(f"Error while adding table {e}")
        print(traceback.format_exc())
        return jsonify({"message": f"Error while adding table: {e}"}), 404
    else:
        return jsonify({"message": "Tables added successfully"}), 200

@app.route('/table_entries/<name>', methods=['GET'])
def get_table_entries(name):
    if name not in manager.tables:
        return jsonify({"error": "Table not found"}), 404
    entries = [{'min_roll': entry.min_roll, 'max_roll': entry.max_roll, 'target': entry.target, 'type': entry.type} for entry in manager.tables[name].entries]
    return jsonify({"table_name": name, "entries": entries}), 200

@app.route('/tables', methods=['GET'])
def get_tables():
    tables = manager.get_tables()
    return jsonify({"tables": tables}), 200

@app.route('/draw/<name>', methods=['GET'])
def draw_from_table(name):
    if name not in manager.get_tables():
        return jsonify({"error": "Table not found"}), 404
    result = manager.draw(name)
    return jsonify({"result": result}), 200

@app.route('/formatted_draw/<name>', methods=['GET'])
def formatted_draw_from_table(name):
    if name not in manager.get_tables():
        return jsonify({"error": "Table not found"}), 404
    result = manager.formatted_draw(name)
    return jsonify({"result": result}), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)