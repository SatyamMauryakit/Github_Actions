from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")
