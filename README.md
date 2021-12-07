# todo-api

Implementation of a backend API using which a client can work with to-do notes.
The API uses JSON as the method of serialization; when working with a todo entry
the payload is a simple JSON object, and when listing todo entries the payload is
a JSON array without wrapping it in a JSON object.

The service currently relies on that a PostgreSQL database is up and running on hostname
postgres, port 5432, and with the necessary database name and schema already delployed.
If using the way of running the application described later on is used such a database is
available on the docker-compose environment used.


## The todo entry

Each todo entry is made up of three fields:
- an `id` field, which contains the UUID of the todo entry.
- a `text` field, which contains a string. This is the main field of the todo entry describing the todo itself.
- a `status` field, which contains a single character string representing the state of the todo note. Supported values are `N` (Not Done) and `D` (Done).

The JSON representation of the todo entry looks like the following:
```
{
    "id": "1c5f7d65-d97e-4e63-996a-ef49ff494184",
    "text": "This something needs to be done",
    "status": "N"
}
```


## API Endpoints
All endpoint URLs use the base path `/todo`.

### `POST /todo`

Creates a new todo entry based on the supplied JSON payload.
The only required field that must be filled in in the supplied payload is the `text` field.
If the other fields aren't present default values will be provided by the endpoint; a newly generated UUID for the `id` field and `N `(Not Done) for the `status` field.
Returns a HTTP status code of 400 (Bad Request) if the `text` field is empty, if the `id` field is provided but doesn't contain a valid UUID or if the `status` field is
provided but doesn't contain one of the supported values. The body of the response will contain a human readable string describing the error.
On success it returns a HTTP status code of 201 (Created) and the complete representation of the created todo entry in the response body.

### `GET /todo/<id>`

Retrieves a single todo entry based on the id supplied in the URL path.
Returns a HTTP status code of 400 (Bad Request) if the id isn't a valid UUID. The body of the response will contain a human readable string describing the error.
Returns a HTTP status code of 404 (Not Found) if an existing todo entry couldn't be found for the supplied id. The body of the response will contain a human readable string describing the error.
On success it returns a HTTP status code of 200 (Ok) and the complete representation of the retrieved todo entry in the response body.

### `GET /todo`

Lists todo entries in the service.
Supports two query parameters which can be used to filter the returned list of todo entries:
- `q`, which can be used to filter todo entries whose text field contains the supplied string.
- `status`, which can be used to filter todo entries of the chosen status. Accepted values are `N` (Not Done) and `D` (Done).
Returns a HTTP status code of 400 (Bad Request) if the `status` parameter is supplied but doesn't contain one of the supported values. The body of the response will contain a human readable string describing the error.
On success it returns a HTTP status code of 200 (Ok) and the body of the response contains a JSON array with the filtered list of todo entries.

### `PUT /todo/<id>`

Updates an existing todo entry based on the supplied JSON payload.
The endpoint doesn't support partial updates at this time, and update of the `id` field is not supported.
Returns a HTTP status code of 400 (Bad Request) if the `text` field is empty, if the `id` field doesn't contain a valid UUID or if the `status` field is doesn't contain one of the supported values. The body of the response will contain a human readable string describing the error.
Returns a HTTP status code of 404 (Not Found) if an existing todo entry couldn't be found for the supplied id. The body of the response will contain a human readable string describing the error.
On success it returns a HTTP status code of 200 (Ok) and the complete representation of the updated todo entry in the response body.

### `DELETE /todo/<id>`

Deletes an existing todo entry based on the id supplied in the URL path.
Returns a HTTP status code of 400 (Bad Request) if the `id` field doesn't contain a valid UUID. The body of the response will contain a human readable string describing the error.
Returns a HTTP status code of 404 (Not Found) if an existing todo entry couldn't be found for the supplied id. The body of the response will contain a human readable string describing the error.
On success it returns a HTTP status code of 204 (No Content) and an empty response body.


## Running the application

To run the application it is required that the machine has both Docker and docker-compose installed. A Dockerfile for the application as well as a docker-compose file to launch an environment
with the application and a PostgreSQL database is available inside the repository.

A helper script to easily start the docker-compose environment is available in `bin/run_app.sh`.

When the environment is up and running the service can be accessed at `http://localhost:5000` using the endpoints described in the previous section.
