# Rhubarb - The Funky Sweet Python ORM built on Strawberry GraphQL That's Totally Awesome

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
from rhubarb.pkg.postgres.connection import connection

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
from rhubarb.pkg.postgres.connection import connection

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
        obj = await by_pk(conn, Person, person_id).one()
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
