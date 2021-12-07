import http
import json
import uuid

import flask
import psycopg2

from todo import app
from todo.payload.todo import Todo
from todo.db.todo import TodoDB

INVALID_UUID_FORMAT_MSG = 'Invalid UUID provided.'
INVALID_STATUS_MSG = "Invalid status provided. Valid values are 'N' or 'D'."
INVALID_STATUS_PARAMETER_MSG = "Invalid status parameter provided. Valid values are 'N' or 'D'."
EMPTY_TODO_TEXT_MSG = 'Empty todo text supplied. This field must be non-empty.'
MISSING_TODO_MSG = 'Todo entry for the supplied UUID does not exist.'
DELETE_TODO_FAILED_MSG = 'Deletion of todo entry failed without database error.'


@app.route('/todo', methods=['POST'])
def create_todo():
    # Parse the request data into a Todo object.
    payload = Todo.from_json(flask.request.data)
    # If id is ommitted a new UUID will be generated, and if status is ommitted a
    # it will be set to default value N (for Not Done).
    payload.assing_default_values()

    # Check that the payload contains a valid UUID
    if not is_valid_uuid(str(payload.get_id())):
        return api_response_bad_request(msg=INVALID_UUID_FORMAT_MSG)

    # Check that a valid todo text was supplied. This is a requirement to be able
    # to create a new Todo.
    if not payload.get_text():
        return api_response_bad_request(msg=EMPTY_TODO_TEXT_MSG)

    # Check that the potentially provided status is one of the valid values
    # Valid are:
    # - N (for Not Done)
    # - D for Done()
    if payload.get_status() != 'N' and payload.get_status() != 'D':
        return api_response_bad_request(msg=INVALID_STATUS_MSG)

    try:
        TodoDB.instance().create(payload)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during creation of new todo.", error)
        return api_response_internal_server_error()
    finally:
        return api_response(payload, http.HTTPStatus.CREATED)


@app.route('/todo/<todoid>', methods=['GET'])
def get_todo(todoid: str):
    # Check that the supplied UUID is valid
    if not is_valid_uuid(todoid):
        return api_response_bad_request(msg=INVALID_UUID_FORMAT_MSG)

    payload = None
    try:
        payload = TodoDB.instance().get(todoid)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during retrieval of todo.", error)
        return api_response_internal_server_error()
    finally:
        if payload is not None:
            return api_response(payload, http.HTTPStatus.OK)
        else:
            return api_response_empty(msg=MISSING_TODO_MSG)


@app.route('/todo', methods=['GET'])
def get_todos():
    textmatch = flask.request.args.get('q')

    # Check that, if supplied, that the status parameter is a valid one.
    status = flask.request.args.get('status')
    if status and status != 'N' and status != 'D':
        return api_response_bad_request(msg=INVALID_STATUS_PARAMETER_MSG)

    try:
        payloads = TodoDB.instance().list(textmatch, status)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during retrieval of todos.", error)
        return api_response_internal_server_error()
    finally:
        return api_response(payloads, http.HTTPStatus.OK)


@app.route('/todo/<todoid>', methods=['PUT'])
def update_todo(todoid: str):
    # Check that the supplied UUID is valid
    if not is_valid_uuid(todoid):
        return api_response_bad_request(msg=INVALID_UUID_FORMAT_MSG)

    # Check that a todo for the specified UUID exists.
    existing_payload = None
    try:
        existing_payload = TodoDB.instance().get(todoid)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during update of todo.", error)
        return api_response_internal_server_error()
    finally:
        if existing_payload is None:
            return api_response_empty(msg=MISSING_TODO_MSG)

    # Parse the request data into a Todo object.
    payload = Todo.from_json(flask.request.data)

    # Check that the payload contains a valid UUID
    if not is_valid_uuid(str(payload.get_id())):
        return api_response_bad_request(msg=INVALID_UUID_FORMAT_MSG)

    # Check that a valid todo text is included.
    if not payload.get_text():
        return api_response_bad_request(msg=EMPTY_TODO_TEXT_MSG)

    # Check that the provided status is one of the valid values
    # Valid are:
    # - N (for Not Done)
    # - D for Done()
    if payload.get_status() != 'N' and payload.get_status() != 'D':
        return api_response_bad_request(msg=INVALID_STATUS_MSG)

    try:
        payload = TodoDB.instance().update(payload)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during update of todo.", error)
        return api_response_internal_server_error()
    finally:
        return api_response(payload, http.HTTPStatus.OK)


@app.route('/todo/<todoid>', methods=['DELETE'])
def delete_todo(todoid: str):
    # Check that the supplied UUID is valid
    if not is_valid_uuid(todoid):
        return api_response_bad_request(msg=INVALID_UUID_FORMAT_MSG)

    # Check that a todo for the specified UUID exists.
    existing_payload = None
    try:
        existing_payload = TodoDB.instance().get(todoid)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during delete of todo.", error)
        return api_response_internal_server_error()
    finally:
        if existing_payload is None:
            return api_response_empty(msg=MISSING_TODO_MSG)

    try:
        is_delete_successful = TodoDB.instance().delete(todoid)
    except (psycopg2.DatabaseError) as error:
        print("Database returned an error during delete of todo.", error)
        return api_response_internal_server_error()
    finally:
        if is_delete_successful:
            return api_response_empty(code=http.HTTPStatus.NO_CONTENT)
        else:
            return api_response_internal_server_error(msg=DELETE_TODO_FAILED_MSG)


##################################################################
############## Utility functions used by endpoints ###############
##################################################################

def is_valid_uuid(id_to_check: str):
    try:
        uuid.UUID(id_to_check)
    except ValueError:
        return False
    return True


# Extend the default JSONEncoder to be able to serialize Todo objects
# as well as UUID objects.
# Used in the api_response function below.
class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Todo):
            return o.to_dict()
        elif isinstance(o, uuid.UUID):
            return str(o)
        else:
            return super(ExtendedJSONEncoder, self).default(o)


def api_response(data, code: int = http.HTTPStatus.OK) -> flask.Response:
    response = flask.Response(json.dumps(data, cls=ExtendedJSONEncoder))
    response.status_code = code
    response.headers.remove("Content-Type")
    response.headers.add_header("Content-Type", "application/json")
    return response

def api_response_empty(code: int = http.HTTPStatus.NOT_FOUND, msg: str = '') -> flask.Response:
    response = flask.Response(msg)
    response.status_code = code
    response.headers.remove("Content-Type")
    return response


def api_response_bad_request(code: int = http.HTTPStatus.BAD_REQUEST, msg: str = '') -> flask.Response:
    response = flask.Response(msg)
    response.status_code = code
    response.headers.remove("Content-Type")
    return response

def api_response_internal_server_error(code: int = http.HTTPStatus.INTERNAL_SERVER_ERROR, msg: str = '') -> flask.Response:
    response = flask.Response(msg)
    response.status_code = code
    response.headers.remove("Content-Type")
    return response
