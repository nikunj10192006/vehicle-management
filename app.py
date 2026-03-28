from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"vehicles": [], "drivers": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "vehicles": [
                {"id": 1, "make": "BMW", "model": "M3 Competition", "year": 2024, "vin": "WBS8M9C50R5A12345", "color": "Alpine White", "price": 85000, "mileage": 1200, "status": "available", "driver_id": None, "fuel": "Gasoline", "transmission": "Automatic", "added": "2024-01-15"},
                {"id": 2, "make": "Mercedes-Benz", "model": "C300", "year": 2023, "vin": "W1KWF8DB4PR123456", "color": "Obsidian Black", "price": 58000, "mileage": 8500, "status": "sold", "driver_id": 1, "fuel": "Gasoline", "transmission": "Automatic", "added": "2024-02-10"},
                {"id": 3, "make": "Audi", "model": "Q8 e-tron", "year": 2024, "vin": "WA1AVBF18RD012345", "color": "Glacier White", "price": 92000, "mileage": 350, "status": "available", "driver_id": None, "fuel": "Electric", "transmission": "Automatic", "added": "2024-03-01"},
                {"id": 4, "make": "Porsche", "model": "Cayenne GTS", "year": 2023, "vin": "WP1AG2A5XRL123456", "color": "Night Blue", "price": 125000, "mileage": 4200, "status": "reserved", "driver_id": 2, "fuel": "Gasoline", "transmission": "Automatic", "added": "2024-01-28"},
                {"id": 5, "make": "Tesla", "model": "Model S Plaid", "year": 2024, "vin": "5YJSA1E69RF123456", "color": "Midnight Silver", "price": 109000, "mileage": 120, "status": "available", "driver_id": None, "fuel": "Electric", "transmission": "Automatic", "added": "2024-03-10"},
            ],
            "drivers": [
                {"id": 1, "name": "James Hartwell", "license": "DL-4821930", "phone": "+1 (555) 201-4892", "email": "j.hartwell@dealer.com", "status": "active"},
                {"id": 2, "name": "Sofia Reyes", "license": "DL-7736421", "phone": "+1 (555) 348-2210", "email": "s.reyes@dealer.com", "status": "active"},
                {"id": 3, "name": "Marcus Chen", "license": "DL-5592018", "phone": "+1 (555) 477-8831", "email": "m.chen@dealer.com", "status": "active"},
            ]
        }
        save_data(data)
    return load_data()

@app.route('/')
def index():
    data = init_data()
    return render_template('index.html', vehicles=data['vehicles'], drivers=data['drivers'])

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    data = load_data()
    search = request.args.get('search', '').lower()
    status = request.args.get('status', '')
    fuel = request.args.get('fuel', '')
    
    vehicles = data['vehicles']
    if search:
        vehicles = [v for v in vehicles if 
                    search in v['make'].lower() or 
                    search in v['model'].lower() or 
                    search in v['vin'].lower() or
                    search in str(v['year'])]
    if status:
        vehicles = [v for v in vehicles if v['status'] == status]
    if fuel:
        vehicles = [v for v in vehicles if v['fuel'] == fuel]
    
    # Enrich with driver name
    drivers_map = {d['id']: d for d in data['drivers']}
    for v in vehicles:
        v['driver_name'] = drivers_map[v['driver_id']]['name'] if v['driver_id'] else None
    
    return jsonify(vehicles)

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = load_data()
    vehicle = request.json
    vehicle['id'] = max([v['id'] for v in data['vehicles']], default=0) + 1
    vehicle['added'] = datetime.now().strftime('%Y-%m-%d')
    vehicle['driver_id'] = int(vehicle['driver_id']) if vehicle.get('driver_id') else None
    data['vehicles'].append(vehicle)
    save_data(data)
    return jsonify(vehicle), 201

@app.route('/api/vehicles/<int:vid>', methods=['PUT'])
def update_vehicle(vid):
    data = load_data()
    vehicle = request.json
    for i, v in enumerate(data['vehicles']):
        if v['id'] == vid:
            vehicle['id'] = vid
            vehicle['added'] = v['added']
            vehicle['driver_id'] = int(vehicle['driver_id']) if vehicle.get('driver_id') else None
            data['vehicles'][i] = vehicle
            save_data(data)
            return jsonify(vehicle)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/vehicles/<int:vid>', methods=['DELETE'])
def delete_vehicle(vid):
    data = load_data()
    data['vehicles'] = [v for v in data['vehicles'] if v['id'] != vid]
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    data = load_data()
    return jsonify(data['drivers'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
