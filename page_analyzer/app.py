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
        SELECT DISTINCT ON (urls.id)
            urls.id,
            urls.name,
            checks.status_code AS code,
            MAX(checks.created_at)
        FROM urls
        LEFT JOIN url_checks AS checks ON
            urls.id = checks.url_id
        GROUP BY urls.id, urls.name, code
        ORDER BY urls.id DESC;
    ''')
    urls = cursor.fetchall()

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
        SELECT id FROM urls WHERE name = %s;
    ''', (url,))
    selection = cursor.fetchone()

    if selection:
        flash('Страница уже существует', 'info')
        return redirect(url_for('get_url', id=selection[0])), 302

    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO urls (name, created_at)
        VALUES (%s, NOW())
        RETURNING id;
    ''', (url,))  # datetime.now().isoformat()
    id = cursor.fetchone()[0]

    connection.commit()

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

    if url is None:
        return render_template(
            'not_found.html'
        ), 404

    cursor.execute('''
        SELECT
            checks.id,
            checks.status_code,
            checks.created_at
        FROM url_checks AS checks
            WHERE %s = checks.url_id;
    ''', (id,))
    url_checks = cursor.fetchall()

    url_data = dict(zip(
        ('id', 'name', 'created_at'), url))

    return render_template(
        'checks.html',
        url_data=url_data,
        url_checks=url_checks,
        messages=messages
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO url_checks
            (url_id, created_at, status_code, h1, title, description)
        VALUES
            (%s, NOW(), 200, '', '', '')
    ''', (id,))

    connection.commit()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=id))
