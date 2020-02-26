from flask import Flask
import subprocess

app = Flask(__name__)


@app.route('/')
def welcome():
    return "Welcome to Camunda Python Client"


if __name__ == '__main__':
    subprocess.Popen('SurpriseMenuClient.js', shell=True)
    app.run()
