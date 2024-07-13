import os
from dotenv import load_dotenv
from flask import Flask
from flask import render_template

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')


@app.route('/')
def index():
    return render_template(
        'index.html'
    ), 200
