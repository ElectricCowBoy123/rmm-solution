import subprocess
import sys
from flask import Flask, render_template

def funcCheckAndInstallFlask():
    try:
        import flask
    except ImportError:
        print("Flask is not installed! Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

funcCheckAndInstallFlask()

from flask import Flask, render_template

app = Flask(__name__, template_folder='console')

@app.route('/')
def init():
    return render_template('main.html')

if __name__ == "__main__":
    print("Starting RMM Server...")
    app.run(host='0.0.0.0', port=5000)