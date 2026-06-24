# Taipan

A fast ASGI web framework for building REST APIs in Python, with a routing core written in Rust.

Taipan is built on a single idea: top-tier performance should not cost you transparency. The Python core is small enough to read in one evening, while the hot paths — routing, validation, and serialization — are handled by Rust and msgspec.

> **Project status: early development (0.x).** The public API may change between minor releases. Taipan is not yet recommended for critical production systems. Follow the repository to track progress toward 1.0.

---

## Why Taipan

- **Rust-powered routing.** Routes are matched by a compressed prefix tree (radix tree). Match time depends on the length of the request path, not on the number of registered routes, so an application with a thousand endpoints routes as fast as one with ten.
- **msgspec-speed validation.** Request bodies are decoded and validated, and responses encoded, by msgspec — the fastest structured-data library in the Python ecosystem.
- **Plans compiled at startup.** Handler signatures are introspected once when the application starts. Parameter binding and dependency injection run from precompiled plans, not from per-request reflection. Configuration errors surface at startup, not under live traffic.
- **No magic.** No global state, no import-time side effects, no hidden wrappers. The function signature is the single source of truth for an endpoint.
- **Standard ASGI.** Taipan is an ordinary ASGI application. It runs under uvicorn, granian, or hypercorn, and works with the existing ASGI middleware ecosystem.
- **Installs without a compiler.** Prebuilt wheels are shipped for Linux, macOS, and Windows. When the native module is unavailable, Taipan falls back to a pure-Python router with identical behavior.

---

## Installation

```bash
pip install taipan-framework
```

The import name is `taipan`:

```python
import taipan
```

Requires Python 3.10 or newer.

---

## Quick start

```python
from taipan import App
import msgspec

app = App()


class UserIn(msgspec.Struct):
    name: str
    email: str
    age: int | None = None


class UserOut(msgspec.Struct):
    id: int
    name: str


@app.get("/")
async def index() -> dict:
    return {"status": "ok"}


@app.get("/users/{user_id:int}")
async def get_user(user_id: int) -> UserOut:
    return UserOut(id=user_id, name="Ada")


@app.post("/users", status_code=201)
async def create_user(data: UserIn) -> UserOut:
    return UserOut(id=1, name=data.name)
```

Run it with any ASGI server:

```bash
uvicorn main:app
```

---

## How parameter binding works

Taipan derives everything from the handler signature. The rules are explicit and have no special markers:

| Condition | Source of the value |
|---|---|
| Parameter name matches a path parameter | Request path |
| Parameter type is a `msgspec.Struct` | Request body (at most one per handler) |
| Parameter type is `Request` or `WebSocket` | The raw object |
| Parameter type is registered with a provider | Dependency injection |
| Any other scalar-typed parameter | Query string |

The return annotation determines the response schema and encoding. Conflicting signatures (a path parameter that collides with a provider, two body parameters) are rejected at startup with a clear error.

---

## Dependency injection

Providers are registered by type. There are no wrapper objects to call in the signature.

```python
@app.provide(Database, scope="app")
async def database():
    db = Database(dsn="...")
    await db.connect()
    yield db
    await db.close()


@app.get("/users/{user_id:int}")
async def get_user(user_id: int, db: Database) -> UserOut:
    record = await db.fetch_user(user_id)
    return UserOut(id=record.id, name=record.name)
```

Generator providers receive guaranteed teardown in reverse order, including when the handler raises. Scopes are `app` (one instance for the application lifetime) and `request` (one instance per request).

---

## Modular routing

```python
from taipan import Router

orders = Router(prefix="/orders", tags=["orders"])


@orders.get("/{order_id:int}")
async def get_order(order_id: int) -> OrderOut:
    ...


app.include(orders)
```

---

## When Taipan is the right choice

- Your profiler shows the framework itself — routing, validation, serialization — taking a meaningful share of CPU, not just waiting on the database.
- You serve a large route table: an API gateway, a backend-for-frontend, or a large product API.
- Throughput per instance translates directly into infrastructure cost.
- Request validation is a hot path: webhooks, telemetry, ingestion endpoints.
- You already use msgspec, or you are starting fresh with no Pydantic legacy.
- You want to be able to read your framework's source in full.

## When Taipan is not the right choice

- Your bottleneck is the database. Fix queries and pooling first; a framework change will move your latency by percentage points, not multiples.
- You need the ecosystem more than the speed. FastAPI has the examples, integrations, and community that Taipan does not yet have.
- You are building a website, not an API. Server-side rendering, templates, sessions, and an admin interface are Django's domain.
- You depend on Pydantic. Taipan does not accept Pydantic models in handlers, by design.
- You cannot accept the risk of a 0.x framework. We are the first to tell you so.

---

## Design boundaries

Taipan builds one layer — the API layer — and builds it fast. The following are deliberately out of scope and will not be added in the 1.x line:

- A built-in HTTP server (delegated to ASGI servers).
- An ORM, migrations, or an admin interface (application concerns; integration recipes live in the docs).
- A template engine or server-side HTML rendering.
- WSGI and synchronous execution. ASGI only.

---

## Performance

Performance is a primary goal of the project, and every published number is backed by a reproducible benchmark protocol: a fixed bench, separate machines for the application and the load generator, identical participant applications, and a full run reproducible with a single command.

Benchmark results will be published here once the native routing core lands (target: version 0.4). Until then, this section intentionally contains no numbers. Claims without a protocol are not claims we make.

---

## Contributing

Contributions are welcome. The Python core requires no Rust knowledge; only changes under `rust/core/` do. Thanks to the pure-Python fallback, you can develop and run the full test suite without a Rust toolchain by setting `TAIPAN_PURE_PYTHON=1`.

See `CONTRIBUTING.md` for the development setup, testing requirements, and pull request process. Routing defects should be reported with a reproducing case in the conformance corpus format.

---

## License

MIT
