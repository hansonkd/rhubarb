# Rhubarb - The Funky Sweet Python ORM built on Strawberry GraphQL

Rhubarb is an ORM baked from scratch focused on automatic optimizations with Postgres data using GQL.

<img width="653" alt="Screenshot 2023-05-03 at 2 32 48 AM" src="https://user-images.githubusercontent.com/496914/235881083-f47d21ff-2462-46f9-acc2-e900316fe05f.png">

*Strawberry-Rhubarb Pie... Tasty!*

# Rhubarb at a glance

* Asyncio Native
* Build SQL functions with Python
* Built on GraphQL for optimization layer on nested queries
* Migrations - Automatically generate Schema changes as your data model updates.
* Intuitively Solve N+1 without even realizing it
* Simplify Aggregations / Joins / Subqueries
* Heavily inspired by Django and built with the philosophy of take the best parts.
* Native Public / Private Schema dichotomy
* Pass User and Extra info to use in queries through Strawberry Info's context.
* Doesn't use any other Python ORM for DB access, only Psycopg3

# Extra Rhubarb Features

Rhubarb comes with some extra integrations to make using the ORM easy...

* HTTP - FastAPI / Starlette
* Redis - Rate Limiting / Caching
* Auth - Impersonate / Sessions / Users / WebAuthN / Password
* Security - CORS / CSRF / TrustedHostNames / Auth Rate Limits
* Auditing - Record all Mutations / Queries / Subscriptions / Custom Events


# Basics

Rhubarb declares Postgres tables with Strawberry dataclasses.

```python
import decimal
import datetime
import uuid
from typing import Optional
from rhubarb import Schema, ObjectSet, ModelSelector, BaseModel, RhubarbExtension, column, table, type, \
    field, get_conn, query, references, relation, virtual_column, Binary
from strawberry.scalars import JSON
from strawberry.types import Info


@table
class TableWithoutSuperClass:
    __schema__ = "public"
    __table__ = "my_awesome_table"
    __pks__ = "id"
    id: int = column()
    info: str = column()



@table
class Person(BaseModel):
    name: str = column()
    some_uuid: Optional[uuid.UUID] = column(sql_default="generate_uuid_v4()")
    a_bool_column: bool = column(column_name="awesome_custom_column_name")
    example_dt_col: datetime.datetime = column(sql_default="now()")
    example_date_col: datetime.date = column()
    example_float_col: float = column()
    example_int_col: int = column()
    example_decimal_col: decimal.Decimal = column()
    example_bytes_col: Binary = column()
    example_jsonb_col: JSON = column()
    
    other_table_reference_id: int = references(TableWithoutSuperClass.__table__)

    @relation
    def other_table(self, other: TableWithoutSuperClass):
        return self.other_table_reference_id == other.id
    
    @virtual_column
    def int_is_big(self) -> bool:
        return self.example_int_col > 100

@type
class Query:
    @field(graphql_type=list[Person])
    def all_people(self, info: Info) -> ObjectSet[Person, ModelSelector[Person]]:
        return query(get_conn(info), Person, info)

    
schema = Schema(
    query=Query
)
```

## Using GQL as an ORM client

Now we can use our schema to make queries and Rhubarb will optimize them for you.

Currently, Rhubarb only does a few optimizations but they cover most use cases:

* Selecting only the columns being asked for in the current GQL query
* Inlining joins that don't produce more rows.
* Managing exploding cartesian products from m:n joins
* Pushing Aggregates to Subquery
* Combining aggregates if they use same `GROUP BY`

```python
from rhubarb.contrib.postgres.connection import connection

async with connection() as conn:
    res = await schema.execute(
        """
        query {
            all_people {
                name
                int_is_big
                a_bool_column
                other_table {
                    id
                    info
                }
            }
        }
        """,
        context_value={"conn": conn}
    )
```

You can either use Rhubarb stand alone or integrate it with FastAPI and Strawberry for a web service.

## Public Schemas

While you can expose your Schema on FastAPI directly, and that may be beneficial for internal use, but for the public users, you do not want all your DB Columns exposed.

Simply create a new schema using standard `type` and `field` exposing only the fields you want from the underlying object exposed.

```python
import rhubarb
from rhubarb import Schema, ObjectSet, RhubarbExtension, get_conn, query
from strawberry.types import Info
from strawberry.scalars import Base64


@rhubarb.type
class TableWithoutSuperClass:
    info: str



@rhubarb.type
class PublicPerson:
    name: str
    # If you are exposing public APIs, better to serialize the Binary fields as Base64
    example_bytes_col: Base64

    @rhubarb.field
    def other_table(self) -> TableWithoutSuperClass:
        return self.other_table()
    
    @rhubarb.field
    def int_is_big(self) -> bool:
        return self.int_is_big()

    
@rhubarb.type
class PublicQuery:
    # Do the query on the Private type and return an ObjectSet, but make the GQL type a Public type instead.
    @rhubarb.field(graphql_type=list[PublicPerson])
    def public_people(self, info: Info) -> ObjectSet[Person, Person]:
        return query(get_conn(info), Person, info).where(lambda x: x.example_int_col > 10)


public_schema = Schema(
    query=PublicQuery,
    extensions=[
        RhubarbExtension
    ]
)
```

## Without GQL

You can also make queries outside of GQL like a normal ORM for use in general Python apps and tasks.

```python
from rhubarb import query, Desc
from rhubarb.contrib.postgres.connection import connection

async with connection() as conn:
    bool_list: list[bool] = await query(conn, Person).select(lambda x: x.int_is_big()).as_list()
```

## Virtual Columns

Rhubarb tables are different from standard Python objects. methods decorated with `virtual_column` and `field` are not executed in Python. These methods are pushed down and transformed into SQL to be executed on the Postgres Server.

```python
from rhubarb import  BaseModel, ModelSelector, column, table, virtual_column
from rhubarb.functions import concat, case, val


@table
class Person(BaseModel):
    first_name: str = column()
    last_name: str = column()
    favorite_number: int = column()
    score: int = column()
    
    @virtual_column
    def full_name(self: ModelSelector) -> str:
        return concat(self.first_name, self.last_name)

    @virtual_column
    def favorite_number_is_42(self: ModelSelector) -> bool:
        return self.favorite_number == 42

    @virtual_column
    def case_computation(self: ModelSelector) -> str:
        return case(
            (self.score == 0, val("Bad")),
            (self.score < 5, val("Poor")),
            (self.score < 7, val("Good")),
            default=val("Excellent")
        )
```

## Relations

Rhubarb will follow child selections and inline as many queries for relation data as possible. This means that most relations that return 1 or 0 objects can be inlined in the same Query as their parent object.

## Relationships with Many Objects

If you have a parent with many children, you can return a list of children by specifying that you want to return a list using `graphql_type` like so `@relation(graphql_type=list[Pet])`.

Because Rhubarb Aggressively inlines all possible fields into a SQL Query, if you return a `list` from a Relation, there is an optimization fence in which Rhubarb will no longer try to inline the relation. Rhubarb will instead start a new tree and start inlining as many children as possible. This is to avoid exploding cartesian products.

```python
from rhubarb import  BaseModel, column, table, relation


@table
class Pet(BaseModel):
    name: str = column()
    owner_id: str = column()
    
    # Default relation returns a single object
    @relation
    def owner(self, owner: "Person"):
        return self.owner_id == owner.id
    
    
@table
class Person(BaseModel):
    name: str = column()

    # Specify relation list of objects. Optimization fence.
    @relation(graphql_type=list[Pet])
    def pets(self, pet: Pet):
        return self.id == pet.owner_id
```

## Aggregations

Aggregations are done by making a virtual table by setting registry to None and then specifying a `__group_by__`.

Once a `__group_by__` is set on a table, all methods and virtual columns have to be aggregate functions or included in the group by.

Rhubarb will make a subquery and join to do the groupby in order to avoid mixing groupby in your parent query.

```python
from rhubarb import  ModelSelector, BaseModel, column, table, relation, virtual_column
from rhubarb.functions import sum_agg, avg_agg


@table
class Pet(BaseModel):
    name: str = column()
    owner_id: str = column()
    weight_lbs: float = column()


@table(skip_registry=True)
class PetByOwner(Pet):
    @virtual_column
    def avg_weight(self: ModelSelector) -> float:
        return avg_agg(self, self.weight_lbs)
    
    @virtual_column
    def weight_of_all_lets(self: ModelSelector) -> float:
        return sum_agg(self, self.weight_lbs)
    
    def __group_by__(self):
        return self.owner_id

    
@table
class Person(BaseModel):
    name: str = column()

    # Specify relation list of objects. Optimization fence.
    @relation(graphql_type=list[Pet])
    def pets(self, pet: Pet):
        return self.id == pet.owner_id

    @relation
    def pet_stats(self, stats: PetByOwner):
        return self.id == stats.owner_id

    @virtual_column
    def avg_pet_weight(self) -> float:
        return self.pet_stats().avg_weight
```

## Computations executed in Python 

Sometimes you may not want to have all your computations be in SQL. If you want a table method to execute in Python, use the `python_field`.

`python_field` takes a function which you use to list your dependencies for the computation. This allows you to specify any other SQL computation or column to feed into your function.

```python
import uuid
from rhubarb import BaseModel, column, table, relation, python_field, virtual_column
from rhubarb.functions import concat


@table
class Address(BaseModel):
    city: str = column()
    state: str = column()
    person_id: uuid.UUID = column()


@table
class Person(BaseModel):
    first_name: str = column()
    last_name: str = column()
    favorite_pokemon: int = column()

    @relation
    def address(self, address: Address):
        return self.id == address.person_id

    # Executed in SQL so need to use special SQL function.
    @virtual_column
    def full_name_sql(self) -> str:
        return concat(self.first_name, " ", self.last_name)

    # Executed in Python, you have to list the SQL dependencies.
    @python_field(lambda x: [x.first_name, x.last_name])
    def full_name_python(self, first_name: str, last_name: str) -> str:
        return f"{first_name} {last_name}"

    # Can use kwargs and async functions...
    @python_field(lambda x: {"fn": x.first_name, "pokemon_id": x.favorite_pokemon})
    async def api_backed_python_field(self, fn: str, pokemon_id: int) -> str:
        # In the real world, probably would cache this HTTP Call or something.
        async with aiohttp.ClientSession() as session:
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'
            async with session.get(pokemon_url) as resp:
                pokemon = await resp.json()
                pokemon_name = pokemon["name"]
                return f"{fn}'s Favorite Pokemon is pokemon {pokemon_name}"

    # Can use relations and other virtual columns...
    @python_field(lambda x: {"sql_full_name": x.full_name_sql(), "address": x.address()})
    def full_name_with_relation_python(self, sql_full_name: str, address: Address) -> str:
        return f"{sql_full_name} from {address.city} {address.state}"
```

# Mutations

Insert, Update, Delete are also optimized for GQL and can be used in Mutations.

```python
import uuid
from rhubarb import Schema, ModelSelector, ModelUpdater, RhubarbExtension, type, \
    get_conn, mutation, update, query, save
from rhubarb.functions import concat
from strawberry.types import Info


@type
class Mutation:
    @mutation
    def update_person(self, info: Info, person_id: uuid.UUID, new_name: str) -> Person:
        def do(person: ModelUpdater[Person]):
            # With Update expressions, we can use computations and reference sql fields and joins.
            person.title = concat(
                new_name, "(Old Name: ", person.title, ")"
            )

        def where(person: ModelSelector[Person]):
            return person.id == person_id

        # Even though this mutation is not async, we are returning an UpdateSet which will
        # be executed by Rhubarb async middleware.
        return update(get_conn(info), Person, do, where, info=info, one=True)

    @mutation
    async def update_name(
        self, info: Info, person_id: uuid.UUID, new_name: str
    ) -> Person:
        conn = get_conn(info)
        # Or avoid the optimization extension and just use await statements. 
        obj = (
            await query(conn, Person)
            .where(lambda book: book.id == person_id)
            .one()
        )
        obj.title = new_name
        return await save(conn, obj, info=info)

    
schema = Schema(
    query=Query,
    mutation=Mutation
)
```

# Cheat Sheet

Here are some other ways to query and update data

```python
import datetime
from rhubarb.crud import query, by_kw, by_pk, save, find_or_create, insert_objs, reload

# Use keywords
query(conn, Person).kw_where(username="my_username")
by_kw(conn, Person, username="my_username")
by_kw(conn, Person, created__lt=datetime.datetime.now() - datetime.timedelta(1))
by_kw(conn, Person, created__lte=datetime.datetime.now() - datetime.timedelta(1))
by_kw(conn, Person, created__gt=datetime.datetime.now() - datetime.timedelta(1))
by_kw(conn, Person, created__gte=datetime.datetime.now() - datetime.timedelta(1))


# Get an object by Primary Key
by_pk(conn, Person, "4fdd6a2d-ff49-41b6-b92a-dc05beb67298")
by_pk(conn, Person, "4fdd6a2d-ff49-41b6-b92a-dc05beb67298")

# Updating
by_kw(conn, Person, username="my_username").kw_update(email="new_email@example.com")
query(conn, Person).kw_update(email="some@example.com", active=True)
save(conn, exising_person)
# Update with a function, lets you use fields.
def set_fn(person):
    person.email = person.verification().email
    person.active = True

def where_fn(person):
    return is_not_null(person.verification().completed)

query(conn, Person).where(where_fn).update(set_fn)
update(conn, Person, set_fn, where_fn)


# Deleting
query(conn, Person).kw_where(username="my_username").delete()
query(conn, Person).where(lambda x: x.username == "my_username").delete()
delete(conn, Person, lambda x: x.username == "my_username")

# find_or_create, attempt to find the record by kw, if not, insert the object.
find_or_create(conn, Person(email="user@example.com"), email="user@example.com")

# Insert an object
save(conn, Person(email="user@example.com"))
# Insert many objects
insert_objs(conn, Person, [Person(email="user@example.com"), Person(email="user2@example.com")])

# Reload an object from the db
reload(conn, existing_person)

# limit results
query(conn, Person).limit(1)
# Order
query(conn, Person).order_by(lambda x: x.updated)
query(conn, Person).order_by(lambda x: Desc(x.updated)) # Descend
query(conn, Person).order_by(lambda x: (Asc(x.birthday), Desc(x.updated))) # Mix and match
query(conn, Person).order_by(lambda x: x.updated).limit(1) 

# Prepare a result set to indicate that only one row will be returned.
update(conn, Person, do, where) # will return a list when `execute` is called
update(conn, Person, do, where, one=True)  # will return one or None rows when `execute` is called
query(conn, Person) # will return a list when `resolve` is called
query(conn, Person, one=True) # will return one or None rows when `resolve` is called


# Executing Object sets
await query(conn, Person).one() # return the result (one or none)
await query(conn, Person).as_list() # return the result (list)
await query(conn, Person, one=one_or_many).resolve() # return the result (dependent on `one` kwarg passed to query)
await query(conn, Person).count() # Executes a COUNT(*) and returns an int
await query(conn, Person).exists() # Executes a SELECT TRUE LIMIT 1 and returns an bool

# Executing Mutations
await insert_objs(conn, Person, ...).execute() # Execute and return list
await insert_objs(conn, Person, ...).execute(one=True) # Execute and return first object
await save(conn, Person(...)).execute() # Execute and return one object
await query(conn, Person).update(...).execute() # Execute and return list
await query(conn, Person, one=True).update(...).execute() # Execute and return one or none objects
await query(conn, Person, one=True).delete().execute() # Execute and return one or none objects
await query(conn, Person).update(...).execute(one=True) # Execute and return one or none objects
```

## Default Filter by User

For each model you can specify a custom `__where__` clause that can take an optional Info. If you give an Info, you can then use the user from the request.

```python
import rhubarb
from rhubarb import table, column, references
from rhubarb.errors import PermissionDenied


# Filter model by user by default...
@table
class SomeModel:
    name: str = column()
    user_id = references(MyUserModel.__table__)

    def __where__(self, info: Info):
        user = info.context["request"].user
        if not user.is_authenticated:
            raise PermissionDenied
        elif user.is_staff or user.is_superuser:
            return True
        return self.user_id == user.id


@rhubarb.type
class Query:
    @rhubarb.field(graphql_type=list[SomeModel])
    def my_field(self, info: Info):
        # To query SomeModel you must pass an info object now.
        return query(conn, SomeModel, info=info)
```

## Efficiently manually querying without GQL

Using the Models through a GQL schema will automatically inline and combine relations. To get the same functionality, when manually using `query` outside of GQL, you will need to return a dataclass from `select` with all the data you want to return.

```python
import dataclasses


@dataclasses.dataclass
class R:
    author: Author
    book: Book


# Query author and book at the same time.
result: list[R] = await query(conn, Book).select(lambda book: R(book=book, author=book.author())).as_list()
```

# Migrations

Rhubarb has basic support for migrations. It will watch for new, changed columns and tables.

## Migration Commands
Make migrations with:

```bash
python -m rhubarb.migrations.cmd.make
```

Apply migrations with

```bash
python -m rhubarb.migrations.cmd.apply
```

Drop all Tables

```bash
python -m rhubarb.migrations.cmd.reset
```

## Migration Basics

You can manage migrations with Registries. A registry is a group of models that can include other registries. This allows you include apps with collections of models in your app.

By default there is a DEFAULT_REGISTRY that all models will be associated with unless otherwise specified.

```python
from rhubarb import DEFAULT_REGISTRY, Registry, BaseModel, table

registry = Registry()

# You can link other registries to your registry, this is useful for other plugins or libs.
# from some_third_party_plugin import third_party_registry
# registry.link(third_party_registry)

# For your main app, its a good idea to link DEFAULT_REGISTRY for the migration table.
registry.link(DEFAULT_REGISTRY)



# Go to default registry
@table
class SomeTable(BaseModel):
    pass

# Go to your specific registry
@table(registry=registry)
class MyTable(BaseModel):
    pass


# Don't include in migrations...
@table(skip_registry=True)
class OtherTable(BaseModel):
    pass
```


## Indexes and Constraints

Indexes and constraints are returned with the `__indexes__` and `__constraints__` function. Rhubarb will monitor if these change by their key and generate migrations if needed.

```python
from rhubarb import BaseModel, column, table, Index, Constraint
from rhubarb.functions import concat


@table
class Person(BaseModel):
    first_name: str = column()
    last_name: str = column()
    favorite_number: int = column()
    last_favorite_number: int = column()
    
    def __indexes__(self):
        return {
            "by_last_name_comma_first": Index(
                on=concat(self.last_name, ",", self.first_name)
            ),
            "by_favorite_number": Index(
                on=self.favorite_number
            )
        }

    def __constraints__(self):
        return {
            "favorite_ne_least_favorite": Constraint(
                check=self.favorite_number != self.last_favorite_number
            )
        }
```

You can add a `DEFAULT` to a column with `sql_default`. Only some SQL functions are supported in order to preserve serialization functionality with Migrations for now.

```python
import uuid
import datetime
from rhubarb import BaseModel, column, table


@table
class AwesomeTable(BaseModel):
    some_uuid: uuid.UUID = column(sql_default="generate_uuid_v4()")
    some_datetime: datetime.datetime = column(sql_default="now()")
```


## Running Python in Migrations

If you want to run a data migration and you need to run python, then generate migrations with `--empty`, and add  `RunPython` to the operations list.

```bash
python -m rhubarb.migrations.cmd.make --empty
```
With RunPython, you get a snapshot of table instances with only concrete fields (no virtual columns or relationships). If you need a computation, redefine it inside the migration so that when you code changes, your migration will always stay the same.

```python
from rhubarb import migrations
from rhubarb import query, save


async def mig_fn(info: migrations.MigrationInfo):
    RatingModel = info.get_model("ratingmodel")
    objs = await query(info.conn, RatingModel).as_list()
    for obj in objs:
        obj.rating += 10
        await save(info.conn, obj)


def migrate():
    return migrations.Migration(
        id="migration_20230426-034718",
        depends_on=[...],
        operations=[
            migrations.RunPython(mig_fn)
        ]
    )
```

# Base Models

There are some convenience superclasses that will add primary keys and utility fields to your Model automatically.

* BaseModel - UUID Primary Key
* BaseUpdateAtModel - UUID Primary Key, created, updated fields.
* BaseIntModel - SERIAL Primary Key
* BaseIntUpdateAtModel - SERIAL Primary Key, created, updated fields.

# Built-in Column / Sql Types

* `dict` -> `JSONB`
* `list` -> `JSONB`
* `strawberry.scalars.JSON` -> `JSONB`
* `strawberry.scalars.Base64` -> `BYTEA`
* `strawberry.scalars.Base32` -> `BYTEA`
* `strawberry.scalars.Base16` -> `BYTEA`
* `rhubarb.core.Binary` -> `BYTEA` (returns raw `bytes` objects)
* `rhubarb.core.Serial` -> `SERIAL`
* `typing.Optional` -> make columns accept NULL
* `bool` -> `BOOLEAN`
* `int` -> `BIGINT`
* `float` -> `FLOAT`
* `str` -> `TEXT`
* `bytes` -> `BYTEA`
* `datetime.datetime` -> `TIMESTAMPTZ`
* `datetime.date` -> `DATE`
* `uuid.UUID` -> `UUID`
* `phonenumbers.PhoneNumber` -> `TEXT`
* `rhubarb.PhoneNumber` -> `TEXT`
* `rhubarb.Email` -> `TEXT`
* `None` -> `NULL` (cannot use as column, use Optional instead.)



# Auth

```python
import uuid

import rhubarb
from rhubarb import Schema, Registry, table, get_conn
from rhubarb.config import Config
from rhubarb.contrib.users.models import User, user_registry, get_user
from rhubarb.contrib.users.backends import login
from rhubarb.contrib.users.config import UserConfig
from rhubarb.contrib.users.middleware import SessionAuthenticationMiddleware
from rhubarb.contrib.sessions.middleware import SessionMiddleware
from rhubarb.contrib.starlette.asgi import GraphQL

from strawberry.types import Info
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware


migrations_registry = Registry()
# Link the user registry for supporting models.
migrations_registry.link(user_registry)


# Add your own user.
@table(registry=migrations_registry)
class MyUser(User):
    pass


@table(registry=migrations_registry)
class CustomModel:
    pass



config = Config(
    registry=migrations_registry,
    users=UserConfig(
        user_model=MyUser
    )
)


@rhubarb.type
class Query:
    @rhubarb.field
    def current_user(self, info: Info) -> MyUser | None:
        if info.context["request"].user.is_authenticated:
            return info.context["request"].user
        return None


@rhubarb.type
class Mutation:
    @rhubarb.mutation
    async def login(self, user_id: uuid.UUID, info: Info) -> MyUser:
        conn = get_conn(info)
        user = await get_user(conn, user_id)
        return await login(conn, user, info.context["request"])


schema = Schema(
    query=Query,
    mutation=Mutation,
)

app = Starlette(
    middleware=[
        Middleware(SessionMiddleware),
        Middleware(SessionAuthenticationMiddleware),
    ],
    routes=[Route("/graphql/", GraphQL(schema, debug=True))],
)
```

# Auditing

Rhubarb comes with built-in Auditing extension that can record all queries, subscriptions, and mutations.

By default, the auditing extension will use a new connection to the database different from the current executing connection of the schema. This is to prevent Transaction rollbacks from deleting written audit events. It also allows you to specify an alternative auditing database (like TimeseriesDB) to silo your events.

The default configuration only logs mutations. This is configurable with `AuditConfig`.

You an save custom Audit events with `rhubarb.contrib.audit.models.log_event`

```python
from rhubarb import Schema
from rhubarb.contrib.audit.extensions import AuditingExtension


schema = Schema(
    query=...,
    mutation=...,
    extensions=[
        AuditingExtension,
    ]
)
```


# Redis and Caching

Rhubarb has built in integrations with redis for caching and ratelimiting and pubsub.

```python
from rhubarb.contrib.redis.connection import connection
from rhubarb.contrib.redis.cache import cache, local_cache, local_only_cache, clear_cache

import aiohttp


async def use_redis():
    async with connection() as r:
        await r.set("some_key", "some_value")
        return await r.get("some_key")

    
# Cache a function in Redis for a minute
@cache(ttl_seconds=60)
async def cached_fn():
        resp = await aiohttp.get("http://example.com")
        return resp.json()
        
# Cache a function locally and in Redis. On Read, prioritize local memory.
# Be careful, clearing cache with local
@local_cache(ttl_seconds=60)
async def cached_fn():
        resp = await aiohttp.get("http://example.com")
        return resp.json()


# Cache a function locally only. 
@local_only_cache(ttl_seconds=60)
async def local_only_cache():
    resp = await aiohttp.get("http://example.com")
    return resp.json()
        
        
# Clear the cache by passing the function.
await clear_cache(cached_fn)
```

# Rate limiting

Rhubarb has built-in a rate limit context manager and decorator. It is synchronized by Redis so can be used in distributed apps to secure parts of the code from bad actors.

```python
from starlette.requests import Request
from rhubarb.contrib.redis.rate_limit import rate_limit


# Rate limit by IP. Once a minute.
async def once_a_minute(request: Request):
    with rate_limit(key=f"my_action-{request.client.host}", max_times=1, ttl_seconds=60):
        return await some_other_function()


# Rate limit as a decorator (this ratelimit would use the same key for all users).
@rate_limit(key=f"my_action", max_times=1, ttl_seconds=60)
async def once_a_minute():
    return await some_other_function()
```
