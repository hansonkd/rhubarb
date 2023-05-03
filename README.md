# Rhubarb - The Funky Sweet ORM built on Strawberry GraphQL

Rhubarb is an ORM written from scratch focused on optimizing traversing data generated through postgres.

## Rhubarb at a glance

* Asyncio Native
* Built on GraphQL for optimization layer on nested queries
* Doesn't use any other Python ORM for DB access, only Psycopg3
* Migrations - Automatically generate Schema changes as your data model updates.
* Intuitively Solve N+1 without even realizing it
* Simplify Aggregations / Joins / Subqueries

Rhubarb declares Postgres tables with Strawberry dataclasses.

```python
import decimal
import datetime
import uuid
from typing import Optional
from rhubarb import Schema, ObjectSet, ModelSelector, BaseModel, RhubarbExtension, column, table, type, \
    field, get_conn, query, references, relation, virtual_column
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
    example_bytes_col: bytes = column()
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
    await schema.execute(
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

### Virtual Columns

These Strawberry Types are different from standard Python objects. methods decorated with `virtual_column` and `field` are not executed in Python. These methods are pushed down and transformed into SQL to be executed on the Postgres Server.

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


### Relations

Rhubarb will follow child selections and inline as many queries for relation data as possible. This means that most relations that return 1 or 0 objects can be inlined in the same Query as their parent object.

#### Relationships with Many Objects

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

#### Aggregations

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
import asyncio
from rhubarb import BaseModel, column, table, relation, python_field
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

    @relation
    def address(self, address: Address):
        return self.id == address.person_id

    # Executed in SQL. Cannot use list interpolation with virtual_column
    @virtual_column
    def full_name_sql(self):
        return concat(self.first_name, " ", self.last_name)

    # Executed in Python.
    @python_field(lambda x: [x.first_name, x.last_name])
    def full_name_python(self, first_name: str, last_name: str):
        return f"{first_name} {last_name}"

    # Can use kwargs and async functions...
    @python_field(lambda x: {"fn": x.first_name, "ln": x.last_name})
    async def full_name_async_python(self, fn: str, ln: str):
        await asyncio.sleep(1)
        return f"{fn} {ln}"

    # Can use relations and other virtual columns...
    @python_field(lambda x: {"sql_full_name": x.full_name_sql(), "address": x.address()})
    def full_name_async_python(self, sql_full_name: str, address: Address):
        return f"{sql_full_name} from {address.city} {address.state}"
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

By default there is a DEFAULT_REGISTRY that all models are registered to.

```python
from rhubarb import Registry, BaseModel, table

registry = Registry()

@table(registry)
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