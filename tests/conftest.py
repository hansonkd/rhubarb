import datetime
import random

import pytest_asyncio

from strawberry.scalars import JSON

import uuid
from typing import Optional

import pytest
import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry.types import Info

from rhubarb.core import get_conn
from rhubarb.crud import delete, save, insert_objs, update, query
from rhubarb.extension import RhubarbExtension
from rhubarb.fixtures import *  # noqa
from rhubarb.migrations.utils import reset_db_and_fast_forward
from rhubarb.model import BaseUpdatedAtModel
from rhubarb.functions import (
    avg_agg,
    concat,
    case,
)
from rhubarb.object_set import (
    ModelSelector,
    ModelUpdater,
    ObjectSet,
    column,
    relation,
    table,
    virtual_column,
    python_field,
    Registry,
    field,
    Value,
    Constraint,
    Index,
    References,
    references,
)


@pytest.fixture
def schema():
    return Schema(
        query=Query,
        mutation=Mutation,
        extensions=[RhubarbExtension],
        config=StrawberryConfig(auto_camel_case=False),
    )


@pytest_asyncio.fixture
async def run_migrations(postgres_connection):
    await reset_db_and_fast_forward(postgres_connection, testing_registry)


@pytest_asyncio.fixture
async def basic_data(postgres_connection, run_migrations):
    conn = postgres_connection

    reviewers = await insert_objs(
        Reviewer,
        conn,
        [Reviewer(name="Jane Jones"), Reviewer(name="Jo Bob")],
        returning=True,
    ).execute()

    authors = await insert_objs(
        Author,
        conn,
        [
            Author(name="Smarty McPy"),
            Author(name="Sandy Doe"),
            Author(name="Justin Nealy"),
        ],
        returning=True,
    ).execute()

    books = await insert_objs(
        Book,
        conn,
        [
            Book(
                title="Python for Dummies",
                author_id=authors[0].id,
                published_on=datetime.date(2023, 9, 3),
            ),
            Book(
                title="How to GQL",
                author_id=authors[1].id,
                published_on=datetime.date(2023, 1, 4),
            ),
            Book(
                title="What is GQL",
                author_id=authors[1].id,
                published_on=datetime.date(2021, 8, 22),
            ),
            Book(
                title="How to find Happiness in Python",
                author_id=authors[2].id,
                published_on=datetime.date(2022, 3, 14),
            ),
        ],
        returning=True,
    ).execute()

    ratings_to_insert = []
    for reviewer in reviewers:
        for book in books:
            ratings_to_insert.append(
                RatingModel(
                    book_id=book.id,
                    reviewer_id=reviewer.id,
                    rating=random.randint(1, 10),
                )
            )

    ratings = await insert_objs(
        RatingModel,
        conn,
        ratings_to_insert,
        returning=True,
    ).execute()

    return {
        "books": books,
        "ratings": ratings,
        "authors": authors,
        "reviewers": reviewers,
    }


testing_registry = Registry(prefix="testing_")


@table(registry=testing_registry)
class Reviewer(BaseUpdatedAtModel):
    name: str = column()


@table(registry=testing_registry)
class Author(BaseUpdatedAtModel):
    __table__ = "custom_author_name"
    name: str = column()

    @relation(graphql_type=list["Book"])
    def books(self, book: "Book"):
        return self.id == book.author_id

    @field(graphql_type=list["RatingModel"])
    def ratings(self):
        return self.books().select(lambda book: book.ratings())


@table(registry=testing_registry)
class Book(BaseUpdatedAtModel):
    title: str = column()
    comments: Optional[str] = column(sql_default=None)
    author_id: uuid.UUID = references(Author.__table__, on_delete="RESTRICT")
    published_on: datetime.date = column()
    meta_info: Optional[JSON] = column(sql_default=None)
    public: bool = column(sql_default=False)

    @relation
    def author(self, author: Author):
        return self.author_id == author.id

    @relation(graphql_type=list["RatingModel"])
    def ratings(self, rating: "RatingModel"):
        return self.id == rating.book_id

    @relation(graphql_type="RatingsByBook")
    def ratings_by_book(self, rating: "RatingsByBook"):
        return self.id == rating.book_id

    @virtual_column
    def avg_rating_embedded(self) -> int:
        return self.ratings_by_book().avg_rating()

    @virtual_column
    def parent_rating(self: ModelSelector) -> "SomeResult":
        return SomeResult(ok=True, author_model=self.author)

    @virtual_column
    def author_name(self) -> str:
        return self.author().name

    @python_field(
        depends_on=lambda root: {"title": root.title, "author_name": root.author().name}
    )
    def title_and_author(self, title: str, author_name: str) -> str:
        return f"{title} by {author_name}"

    @python_field(
        depends_on=lambda root: {"title": root.title, "author_name": root.author().name}
    )
    async def async_title_and_author(self, title: str, author_name: str) -> str:
        return f"{title} by {author_name}"


@table(registry=testing_registry)
class RatingModel(BaseUpdatedAtModel):
    rating: int = column()
    book_id: uuid.UUID = column(
        references=References(Book.__table__, on_delete="CASCADE")
    )
    reviewer_id: uuid.UUID = column(
        references=References(Reviewer.__table__, on_delete="SET NULL")
    )
    published_on: datetime.datetime = column(insert_default="now()")

    @relation
    def book(self, om: Book):
        return self.book_id == om.id

    @relation
    def reviewer(self, om: Reviewer):
        return self.reviewer_id == om.id

    @column(virtual=True)
    def inflated(self) -> int:
        return self.rating + 1

    @column(virtual=True)
    def case_computation(self: ModelSelector) -> str:
        return case(
            (self.rating == 0, Value("Bad")),
            (self.rating < 5, Value("Poor")),
            (self.rating < 7, Value("Good")),
            default=Value("Excellent"),
        )

    def __constraints__(self: ModelSelector):
        return {"rating_positive": Constraint(check=self.rating >= 0)}

    def __indexes__(self: ModelSelector):
        return {"rating_idx": Index(on=self.rating)}


@table(skip_registry=True)
class RatingsByBook(RatingModel):
    @virtual_column
    def avg_rating(self: ModelSelector) -> int:
        return avg_agg(self, self.rating)

    def __group_by__(self):
        return self.book_id

    def __order_by__(self):
        return self.book_id


@strawberry.type
class SomeResult:
    ok: bool
    author_model: Author


@strawberry.type
class Query:
    @strawberry.field(graphql_type=list[Book])
    def all_books(self, info: Info) -> ObjectSet[Book, ModelSelector[Book]]:
        return query(Book, get_conn(info), info)

    @strawberry.field(graphql_type=list[RatingModel])
    def all_ratings(
        self, info: Info
    ) -> ObjectSet[RatingModel, ModelSelector[RatingModel]]:
        return query(RatingModel, get_conn(info), info)

    @strawberry.field(graphql_type=list[RatingsByBook])
    def agg(self, info: Info) -> ObjectSet[RatingsByBook, ModelSelector[RatingsByBook]]:
        return query(RatingsByBook, get_conn(info), info)


@strawberry.type
class SomeRatingResult:
    ok: bool
    rating: Optional[RatingModel] = None


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Updates all author's books with a new title")
    def update_titles(self, info: Info, book_id: uuid.UUID, new_title: str) -> Book:
        def do(book: ModelUpdater[Book]):
            # With Update expressions, we can use computations and reference sql fields and joins.
            book.title = concat(
                new_title, "(Old Title: ", book.title, ", by: ", book.author().name, ")"
            )

        def where(book: ModelSelector[Book]):
            return book.id == book_id

        return update(Book, get_conn(info), do, where, info=info, one=True)

    @strawberry.mutation
    async def new_review(
        self, info: Info, book_id: uuid.UUID, reviewer_id: uuid.UUID, rating: int
    ) -> RatingModel:
        return insert_objs(
            RatingModel,
            get_conn(info),
            [RatingModel(book_id=book_id, reviewer_id=reviewer_id, rating=rating)],
            info=info,
            one=True,
        )

    @strawberry.mutation
    async def nested_new_review(
        self, info: Info, book_id: uuid.UUID, reviewer_id: uuid.UUID, rating: int
    ) -> SomeRatingResult:
        if rating < 1:
            return SomeRatingResult(ok=False)
        else:
            return SomeRatingResult(
                ok=True,
                rating=insert_objs(
                    RatingModel,
                    get_conn(info),
                    [
                        RatingModel(
                            book_id=book_id, reviewer_id=reviewer_id, rating=rating
                        )
                    ],
                    info=info,
                    one=True,
                ),
            )

    @strawberry.mutation
    async def update_title(
        self, info: Info, book_id: uuid.UUID, new_title: str
    ) -> Book:
        obj = (
            await query(Book, get_conn(info))
            .where(lambda book: book.id == book_id)
            .one()
        )
        obj.title = new_title
        return await save(obj, get_conn(info), info=info)

    @strawberry.mutation
    async def delete_book(self, info: Info, book_id: uuid.UUID) -> Book:
        def where(root):
            return root.id == book_id

        return await delete(
            Book, get_conn(info), info=info, where=where, returning=True
        ).execute(one=True)


class Schema(strawberry.Schema):
    def process_errors(
        self,
        errors,
        execution_context=None,
    ) -> None:
        super().process_errors(errors, execution_context)

        for error in errors:
            err = getattr(error, "original_error")
            if err:
                raise err
