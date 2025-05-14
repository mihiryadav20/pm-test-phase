from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/about')
def about():
    return "This is a basic Flask application."

if __name__ == '__main__':
    app.run(debug=True)