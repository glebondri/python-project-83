from flask import Flask
from flask import render_template, redirect
from flask import request, flash, get_flashed_messages
from flask import url_for

from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

import psycopg2
import validators
import os


load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')

connection = psycopg2.connect(os.getenv('DB_SECRET'))


@app.route('/')
def index():
    return render_template(
        'index.html'
    ), 200


@app.route('/urls', methods=['GET'])
def get_urls():
    messages = get_flashed_messages(with_categories=True)

    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, name FROM urls ORDER BY id DESC;
    ''')
    urls = cursor.fetchall()
    cursor.close()

    return render_template(
        'urls.html',
        urls=urls,
        messages=messages
    ), 200


@app.route('/urls', methods=['POST'])
def post_url():
    url = request.form.get('url')

    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=url,
            messages=get_flashed_messages(with_categories=True)
        )

    parsed = urlparse(url)._replace(query='', path='', params='')
    url = urlunparse(parsed)

    cursor = connection.cursor()
    cursor.execute('''
        SELECT id FROM urls
        WHERE name = %s;
    ''', (url,))
    selection = cursor.fetchone()

    if selection is not None:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=selection[0])), 302

    cursor.execute('''
        INSERT INTO urls (name, created_at)
        VALUES (%s, NOW())
        RETURNING id;
    ''', (url,))  # datetime.now().isoformat()
    id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=id)), 302


@app.route('/urls/<int:id>', methods=['GET'])
def get_url(id):
    messages = get_flashed_messages(with_categories=True)

    cursor = connection.cursor()
    cursor.execute('''
            SELECT id, name, created_at FROM urls
            WHERE id = %s;
        ''', (id,))
    url = cursor.fetchone()
    cursor.close()

    if url is None:
        # return 'url does\'nt exists!'
        return render_template(
            'not_found.html'
        ), 404

    data = dict(zip(
        ('id', 'name', 'created_at'), url))
    return render_template(
        'checks.html',
        data=data,
        messages=messages
    )
