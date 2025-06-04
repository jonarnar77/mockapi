# mockapi

A simple Flask-based mock API service using SQLite for storage.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python -m mockapi.app
```

This will start the server on `http://127.0.0.1:5000`. If you use
`localhost` and your system prefers IPv6, you might hit another service
listening on port 5000. Using the IPv4 address avoids that issue.

## Registering an endpoint

Send a POST request to `/register` with a JSON body:

```json
{
  "path": "customer/123",
  "methods": ["GET"],
  "response_type": "json",
  "response_body": "{\"id\":123,\"name\":\"John Doe\",\"email\":\"john@doe.com\"}",
  "status_code": 200
}
```

## Deregistering

Send a POST request to `/deregister` with a JSON body containing the path:

```json
{ "path": "customer/123" }
```

## Listing registered endpoints

Call `GET /endpoints` to retrieve a JSON array of all registered endpoints.
Each entry contains the path, allowed methods and status code. For example:

```json
[
  {
    "path": "customer/123",
    "methods": ["GET"],
    "status_code": 200
  }
]
```

## Using the API

Once registered, you can query the mocked endpoint via the `/api/` prefix.
For example, if you registered `customer/123` you would call
`GET http://127.0.0.1:5000/api/customer/123` to retrieve the document.

### HTML responses and status codes

You can also register endpoints that return HTML with custom status codes. For
example, to register an endpoint that returns a welcome page and another that
returns a 500 error:

```bash
curl -X POST http://127.0.0.1:5000/register -H 'Content-Type: application/json' \
  -d '{"path":"welcome","methods":["GET"],"response_type":"html","response_body":"<h1>Welcome</h1>","status_code":200}'

curl -X POST http://127.0.0.1:5000/register -H 'Content-Type: application/json' \
  -d '{"path":"error","methods":["GET"],"response_type":"html","response_body":"<h1>Internal Server Error</h1>","status_code":500}'
```

After registering, `GET http://127.0.0.1:5000/api/welcome` returns the HTML
welcome page with status 200, while
`GET http://127.0.0.1:5000/api/error` returns the error page with status 500.

## Importing and exporting

You can export all registered endpoints with:

```bash
curl http://127.0.0.1:5000/export
```

This returns a JSON array with the full definitions including response bodies.

To import multiple endpoints in one call, POST the JSON back to `/import`:

```bash
curl -X POST http://127.0.0.1:5000/import -H 'Content-Type: application/json' \
  -d '[{"path":"foo","methods":["GET"],"response_type":"json","response_body":"{}","status_code":200}]'
```

Each entry is added just like calling `/register` and the response includes the
number of endpoints created.

---

## License

This project is licensed under the MIT License — see LICENSE.

---

## Author

Created with ❤️  by Jon Arnar Jonsson.
