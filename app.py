from flask import Flask
import threading
from surprise_menu_client import SurpriseMenuClient

app = Flask(__name__)
threading.Thread(target=SurpriseMenuClient).start()


@app.route('/')
def welcome():
    return "Welcome to Camunda Python Client"


if __name__ == '__main__':
    app.run()
