from flask import Flask, request, jsonify
import sqlite3
import os
from contextlib import closing
from threading import Thread

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'database', 'data', 'Records.db')

def _ensure_db():
    # Ensure DB path exists; the app's Database.create_tables should handle schema.
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@app.route('/request_connect', methods=['POST'])
def request_connect():
    payload = request.json or {}
    name = payload.get('name')
    requested_access = payload.get('access', 'read')
    host_info = payload.get('host_info', '')

    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS connection_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, access TEXT, host_info TEXT, status TEXT DEFAULT "pending")')
        cur.execute('INSERT INTO connection_requests (name, access, host_info, status) VALUES (?, ?, ?, ?)', (name, requested_access, host_info, 'pending'))
        conn.commit()
        req_id = cur.lastrowid

    return jsonify({'request_id': req_id, 'status': 'pending'})


@app.route('/admin/pending_requests', methods=['GET'])
def pending_requests():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS connection_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, access TEXT, host_info TEXT, status TEXT DEFAULT "pending")')
        cur.execute("SELECT id, name, access, host_info, status FROM connection_requests WHERE status = 'pending'")
        rows = cur.fetchall()
        reqs = [{'id': r[0], 'name': r[1], 'access': r[2], 'host_info': r[3], 'status': r[4]} for r in rows]
    return jsonify(reqs)


@app.route('/admin/approve_request', methods=['POST'])
def approve_request():
    data = request.json or {}
    req_id = data.get('request_id')
    approve = data.get('approve', True)
    token = None
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, name, access FROM connection_requests WHERE id = ?', (req_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        if approve:
            # create a simple token (insecure but workable for local usage)
            token = f"T{req_id:06d}"
            cur.execute('UPDATE connection_requests SET status = ? WHERE id = ?', ('approved', req_id))
            cur.execute('CREATE TABLE IF NOT EXISTS approved_tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id INTEGER, token TEXT, access TEXT)')
            cur.execute('INSERT INTO approved_tokens (request_id, token, access) VALUES (?, ?, ?)', (req_id, token, row[2]))
        else:
            cur.execute('UPDATE connection_requests SET status = ? WHERE id = ?', ('denied', req_id))
        conn.commit()

    return jsonify({'approved': bool(approve), 'token': token})


@app.route('/sync/members', methods=['GET'])
def sync_members_get():
    # return all members (read)
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM members")
        cols = [c[0] for c in cur.description] if cur.description else []
        rows = cur.fetchall()
        members = [dict(zip(cols, r)) for r in rows]
    return jsonify(members)


@app.route('/sync/members', methods=['POST'])
def sync_members_post():
    # accept posted member changes (simple upsert by member_id)
    data = request.json or {}
    if not isinstance(data, dict) and not isinstance(data, list):
        return jsonify({'error': 'invalid payload'}), 400

    items = data if isinstance(data, list) else [data]
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        for it in items:
            member_id = it.get('member_id')
            name = it.get('name')
            # naive upsert
            cur.execute('SELECT id FROM members WHERE member_id = ?', (member_id,))
            row = cur.fetchone()
            if row:
                cur.execute('UPDATE members SET name = ?, contact = ?, email = ?, dob = ?, occupation = ?, marital_status = ?, duty = ?, class = ?, activity = ?, photo_path = ? WHERE member_id = ?', (
                    it.get('name'), it.get('contact'), it.get('email'), it.get('dob'), it.get('occupation'), it.get('marital_status'), it.get('duty'), it.get('member_class'), it.get('activity_status'), it.get('photo_path'), member_id
                ))
            else:
                cur.execute('INSERT INTO members (member_id, name, contact, email, dob, occupation, marital_status, duty, class, activity, photo_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
                    member_id, it.get('name'), it.get('contact'), it.get('email'), it.get('dob'), it.get('occupation'), it.get('marital_status'), it.get('duty'), it.get('member_class'), it.get('activity_status'), it.get('photo_path')
                ))
        conn.commit()
    return jsonify({'status': 'ok'})


def run_server(host='0.0.0.0', port=5000):
    _ensure_db()
    app.run(host=host, port=port)


if __name__ == '__main__':
    run_server()
