'''
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
'''
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home():
    return("hello")

if __name__ == '__main__':
    app.run(debug=True)
