from flask import request

from settings import API_KEY


def api_key(method: callable):
    def wrapper(*args, **kwargs):
        key = request.args.get("api_key")

        if key != API_KEY:
            return {"message": "invalid api_key"}, 404

        return method(*args, **kwargs)

    return wrapper
