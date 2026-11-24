from flask import current_app, jsonify, request

from app.errors import BadRequest


def json_body():
    """Parse the request body; it must be a JSON object."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("Request body must be a JSON object")
    return data


def service(name):
    return current_app.extensions[name]


def created(body, location):
    resp = jsonify(body)
    resp.status_code = 201
    resp.headers["Location"] = location
    return resp
