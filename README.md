# Rhubarb - The Funky Sweet Python ORM built on Strawberry GraphQL

Rhubarb is an ORM baked from scratch focused on automatic optimizations with Postgres data using GQL.

<img width="653" alt="Screenshot 2023-05-03 at 2 32 48 AM" src="https://user-images.githubusercontent.com/496914/235881083-f47d21ff-2462-46f9-acc2-e900316fe05f.png">

*Strawberry-Rhubarb Pie... Tasty!*

# Rhubarb at a glance

* Asyncio Native
* Built on GraphQL for optimization layer on nested queries
* Doesn't use any other Python ORM for DB access, only Psycopg3
* Migrations - Automatically generate Schema changes as your data model updates.
* Intuitively Solve N+1 without even realizing it
* Simplify Aggregations / Joins / Subqueries
* Heavily inspired by Django and built with the philosophy of take the best parts.
* Native Public / Private Schema dichotomy
* Pass User and Extra info to use in queries through Strawberry Info's context.

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
        return query(Person, get_conn(info), info)

    
schema = Schema(
    query=Query,
    extensions=[
        RhubarbExtension
    ]
)
```

## Using GQL as an ORM client

Now we can use our schema to make queries and Rhubarb will try to optimize them for you.

Currently, Rhubarb only does a few optimizations but they cover most use cases:

* Selecting only the columns being asked for in the current GQL query
* Inlining joins the don't produce more rows.
* Managing exploding cartesian products from m:n joins
* Pushing Aggregates to Subquery
* Combining aggregates if they use same `GROUP BY`

```python
from rhubarb.connection import connection


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

### Public Schemas

While you can expose your Schema on FastAPI directly, and maybe that is beneficial for internal use, but for the public users, you do not want all your DB Columns exposed.

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
        return query(Person, get_conn(info), info).where(lambda x: x.example_int_col > 10)


private_schema = Schema(
    query=PublicQuery,
    extensions=[
        RhubarbExtension
    ]
)
```

### Without GQL

You can also make queries outside of GQL like a normal ORM. However the optimizations won't benefit you once you convert it into a list or concrete instance.

```python
from rhubarb import query, Desc
from rhubarb.connection import connection


async with connection() as conn:
    person_list: list[Person] = await query(Person, conn).as_list()
    limited_person_list: list[Person] = await query(Person, conn).where(lambda x: x.a_bool_column == True).limit(5).as_list()
    other_table_list: list[TableWithoutSuperClass] = await query(Person, conn).select(lambda x: x.other_table()).as_list()
    bool_list: list[bool] = await query(Person, conn).select(lambda x: x.int_is_big()).as_list()
    one_person = await query(Person, conn).one()
    recent_person = await query(Person, conn).order_by(lambda x: Desc(x.example_date_col)).one()
```

## Virtual Columns

Rhubarb tables are different from standard Python objects. methods decorated with `virtual_column` and `field` are not executed in Python. These methods are pushed down and transformed into SQL to be executed on the Postgres Server.

```python
from rhubarb import  BaseModel, ModelSelector, column, table, virtual_column
from rhubarb.functions import concat, case, Value


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
            (self.score == 0, Value("Bad")),
            (self.score < 5, Value("Poor")),
            (self.score < 7, Value("Good")),
            default=Value("Excellent")
        )
```

## Relations

Rhubarb will follow child selections and inline as many queries for relation data as possible. This means that most relations that return 1 or 0 objects can be inlined in the same Query as their parent object.

### Relationships with Many Objects

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
from rhubarb import  BaseModel, column, table, relation, virtual_column
from rhubarb.functions import sum_agg, avg_agg


@table
class Pet(BaseModel):
    name: str = column()
    owner_id: str = column()
    weight_lbs: float = column()


@table(skip_registry=True)
class PetByOwner(Pet):
    @virtual_column
    def avg_weight(self) -> float:
        return avg_agg(self.weight_lbs)
    
    @virtual_column
    def weight_of_all_lets(self) -> float:
        return sum_agg(self.weight_lbs)
    
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

#### Computations executed in Python 

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
    def full_name_sql(self):
        return concat(self.first_name, " ", self.last_name)

    # Executed in Python.
    @python_field(lambda x: [x.first_name, x.last_name])
    def full_name_python(self, first_name: str, last_name: str):
        return f"{first_name} {last_name}"

    # Can use kwargs and async functions...
    @staticmethod
    @python_field(lambda x: {"fn": x.first_name, "pokemon_id": x.favorite_pokemon})
    async def api_backed_python_field(fn: str, pokemon_id: int):
        # In the real world, probably would cache this HTTP Call or something.
        async with aiohttp.ClientSession() as session:
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'
            async with session.get(pokemon_url) as resp:
                pokemon = await resp.json()
                pokemon_name = pokemon["name"]
                return f"{fn}'s Favorite Pokemon is pokemon {pokemon_name}"

    # Can use relations and other virtual columns...
    @python_field(lambda x: {"sql_full_name": x.full_name_sql(), "address": x.address()})
    def full_name_with_relation_python(self, sql_full_name: str, address: Address):
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
        return update(Person, get_conn(info), do, where, info=info, one=True)

    @mutation
    async def update_name(
        self, info: Info, person_id: uuid.UUID, new_name: str
    ) -> Person:
        # Or avoid the optimization extension and just use await statements. 
        obj = (
            await query(Person, get_conn(info))
            .where(lambda book: book.id == person_id)
            .one()
        )
        obj.title = new_name
        return await save(obj, get_conn(info), info=info)

    
schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        RhubarbExtension
    ]
)
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


#### Indexes and Constraints

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


### Running Python in Migrations

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
    objs = await query(RatingModel, info.conn).as_list()
    for obj in objs:
        obj.rating += 10
        await save(obj, info.conn)


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
* BaseUpdateAtModel - UUID Primary Key, created_at, updated_at fields.
* BaseIntModel - SERIAL Primary Key
* BaseIntUpdateAtModel - SERIAL Primary Key, created_at, updated_at fields.

# Built-in Types


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
* `None` -> `NULL` (cannot use as column, use Optional instead.)
