import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET')


@app.route('/')
def index():
    return '''
    <script>
        alert(\'hello hexlet!\')
    </script>
    '''
