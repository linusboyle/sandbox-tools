from flask import Flask, jsonify, request, render_template
from random_table_manager import RandomTableManager

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
    data = request.json
    table = data.get('table')
    manager.add_table(table)
    return jsonify({"message": "Tables added successfully"}), 200

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