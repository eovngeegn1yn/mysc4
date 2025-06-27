from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_very_strong_secret_key'

# Настройка БД
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'leagues.db')


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


# Маршруты
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/football')
def football():
    db = get_db()
    leagues = db.execute('SELECT * FROM leagues ORDER BY position').fetchall()
    title = db.execute('SELECT title FROM settings WHERE id = 1').fetchone()['title']
    db.close()
    return render_template('football.html', leagues=leagues, title=title)


@app.route('/check_admin', methods=['POST'])
def check_admin():
    if request.form.get('admin_code') == 'mysc':  # Замените на ваш код
        session['admin_mode'] = True
    return redirect(request.referrer or url_for('home'))


@app.route('/exit_admin')
def exit_admin():
    session.pop('admin_mode', None)
    return redirect(request.referrer or url_for('home'))


@app.route('/update_league', methods=['POST'])
def update_league():
    if not session.get('admin_mode'):
        return jsonify({'error': 'Доступ запрещён'}), 403

    data = request.json
    db = get_db()
    db.execute('UPDATE leagues SET name = ?, position = ? WHERE id = ?',
               [data['name'], data['position'], data['id']])
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/add_league', methods=['POST'])
def add_league():
    if not session.get('admin_mode'):
        return jsonify({'error': 'Доступ запрещён'}), 403

    db = get_db()
    db.execute('INSERT INTO leagues (name, position) VALUES (?, ?)',
               [request.json['name'], request.json['position']])
    db.commit()
    db.close()
    return jsonify({'success': True})


@app.route('/delete_league/<int:league_id>', methods=['DELETE'])
def delete_league(league_id):
    if not session.get('admin_mode'):
        return jsonify({'error': 'Доступ запрещён'}), 403

    db = get_db()
    db.execute('DELETE FROM leagues WHERE id = ?', [league_id])
    db.commit()
    db.close()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)