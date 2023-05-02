# Rhubarb - The Funky Sweet ORM built on Strawberry GraphQL

Rhubarb is an ORM written from scratch focused on optimizing traversing data generated through postgres.

## Rhubarb at a glance

With rhubarb you declare Postgres tables with Strawberry dataclasses.

```python
from rhubarb.model import  BaseModel, column, table


@table
class Person(BaseModel):
    name: str = column()
```

### Virtual Columns

These Strawberry Types are different from standard Python objects. methods decorated with `virtual_column` and `field` are not executed in Python. These methods are pushed down and transformed into SQL to be executed on the Postgres Server.

```python
from rhubarb.model import  BaseModel, column, table
from rhubarb.object_set import virtual_column, concat


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
from rhubarb.model import  BaseModel, column, table
from rhubarb.object_set import relation


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
from rhubarb.model import  BaseModel, column, table
from rhubarb.object_set import relation, virtual_column


@table
class Pet(BaseModel):
    name: str = column()
    owner_id: str = column()
    weight_lbs: float = column()


@table(registry=None)
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
from rhubarb.model import BaseModel, column, table
from rhubarb.object_set import python_field, virtual_column, concat, relation


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

#### Indexes and Constraints

Indexes and constraints are returned with the `__indexes__` and `__constraints__` function. Rhubarb will monitor if these change by their key and update them if needed.

```python
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

You can add a `DEFAULT` to a column with `default_sql`. Only some SQL functions are supported.

```python
@table
class AwesomeTable(BaseModel):
    some_uuid: uuid.UUID = column(default_sql="generate_uuid_v4()")
    some_datetime: datetime.datetime = column(default_sql="now()")
```