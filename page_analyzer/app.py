from flask import Flask
from flask import render_template, redirect
from flask import request, flash, get_flashed_messages
from flask import url_for

from page_analyzer import utils
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

import psycopg2
import requests
import validators
import datetime
import os


load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

connection = psycopg2.connect(os.getenv('DATABASE_URL'))


@app.route('/')
def index():
    return render_template(
        'index.html'
    ), 200


@app.route('/urls', methods=['GET'])
def get_urls():
    """Displays a list of URLs the user has added"""

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
    """Posts a new URL to the database"""

    url = request.form.get('url')

    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=url,
            messages=get_flashed_messages(with_categories=True)
        ), 422

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

    date = datetime.date.today().isoformat()

    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO urls (name, created_at)
        VALUES (%s, %s)
        RETURNING id;
    ''', (url, date))
    id = cursor.fetchone()[0]

    connection.commit()

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('get_url', id=id)), 302


@app.route('/urls/<int:id>', methods=['GET'])
def get_url(id: int):
    """Displays information about the URL with the given ID, if found"""

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
            checks.created_at,
            checks.h1,
            checks.title,
            checks.description
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
    ), 200


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id: int):
    """Runs an HTTP check for a
    specified URL, enters the check result into database"""

    cursor = connection.cursor()
    cursor.execute('''
        SELECT name FROM urls
        WHERE id = %s;
    ''', (id,))
    url = cursor.fetchone()[0]

    try:
        response = requests.get(url)
        response.raise_for_status()

        status_code = response.status_code
        html = response.text

        h1, title, description = utils.parse_html(html)
        date = datetime.date.today().isoformat()

        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO url_checks
                (url_id, created_at, status_code, h1, title, description)
            VALUES
                (%s, %s, %s, %s, %s, %s)
        ''', (id, date, status_code,
              h1, title, description))

        connection.commit()

        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('get_url', id=id)), 302

    except (requests.HTTPError, requests.ConnectionError):
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('get_url', id=id)), 302
