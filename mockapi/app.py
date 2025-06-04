import sqlite3
import json
from flask import Flask, request, jsonify, make_response
from .database import get_connection, init_db

app = Flask(__name__)

init_db()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    path = data.get('path')
    methods = ','.join(data.get('methods', ['GET']))
    response_type = data.get('response_type', 'json')
    response_body = data.get('response_body', '')
    status_code = int(data.get('status_code', 200))

    if not path:
        return jsonify({'error': 'path required'}), 400

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            'INSERT INTO endpoints (path, methods, response_type, response_body, status_code) VALUES (?,?,?,?,?)',
            (path, methods, response_type, response_body, status_code)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'endpoint already exists'}), 400
    conn.close()
    return jsonify({'message': 'registered'}), 201


@app.route('/deregister', methods=['POST'])
def deregister():
    data = request.get_json(force=True)
    path = data.get('path')
    if not path:
        return jsonify({'error': 'path required'}), 400
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM endpoints WHERE path = ?', (path,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'deregistered'}), 200


@app.route('/endpoints', methods=['GET'])
def list_endpoints():
    """Return all registered endpoints with their allowed methods and status codes."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT path, methods, status_code FROM endpoints ORDER BY path')
    rows = c.fetchall()
    conn.close()
    endpoints = [
        {
            'path': row['path'],
            'methods': row['methods'].split(','),
            'status_code': row['status_code'],
        }
        for row in rows
    ]
    return jsonify(endpoints)


@app.route('/api/<path:endpoint_path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def api(endpoint_path):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM endpoints WHERE path = ?', (endpoint_path,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'not found'}), 404

    if request.method not in row['methods'].split(','):
        return jsonify({'error': 'method not allowed'}), 405

    if row['response_type'] == 'json':
        response = jsonify(json.loads(row['response_body']))
    else:
        response = make_response(row['response_body'])
    response.status_code = row['status_code']
    return response


if __name__ == '__main__':
    # Listen on all interfaces so both IPv4 and IPv6 clients can connect
    app.run(debug=True, host='0.0.0.0')
