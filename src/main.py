import json
import logging

from flask import Flask
from flask_cors import CORS

import bot
from settings import IP, PORT

app = Flask(__name__)
CORS(app)


@app.route("/run")
def run_bot():
    result = bot.run()
    return json.dumps(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app.run(host=IP, port=PORT)
