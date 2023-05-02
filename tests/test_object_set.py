from collections import defaultdict

import pytest

from rhubarb.connection import track_queries


@pytest.mark.asyncio
async def test_books(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { id, title } }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        assert len(tracker.queries) == 1
        assert len(res.data["all_books"]) == 4
        for book in res.data["all_books"]:
            assert book["id"]
            assert book["title"]


@pytest.mark.asyncio
async def test_books_author(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { id, title, author_name, async_title_and_author, title_and_author, author { name } } }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        assert len(tracker.queries) == 1
        assert len(res.data["all_books"]) == 4
        for book in res.data["all_books"]:
            assert book["id"]
            assert book["title"]
            assert book["author"]
            assert book["author"]["name"]
            assert book["author_name"] == book["author"]["name"]
            assert book["title_and_author"] == book["async_title_and_author"]
            assert book["async_title_and_author"] == f"{book['title']} by {book['author_name']}"


@pytest.mark.asyncio
async def test_reviews(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { id, ratings { reviewer { name }, rating} } }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        for query in tracker.queries:
            print(query)
        assert len(tracker.queries) == 2
        assert len(res.data["all_books"]) == 4
        for book in res.data["all_books"]:
            assert book["id"]
            assert book["ratings"]
            for rating in book["ratings"]:
                assert rating["reviewer"]
                assert rating["reviewer"]["name"]
                assert rating["rating"]


@pytest.mark.asyncio
async def test_aggregations_at_top_level(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { agg { book_id, avg_rating} }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        for query in tracker.queries:
            print(query)
        assert len(tracker.queries) == 1
        assert len(res.data["agg"]) == 4
        for book in res.data["agg"]:
            assert book["book_id"]
            assert book["avg_rating"]


@pytest.mark.asyncio
async def test_aggregations_embedded(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { id, avg_rating_embedded} }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        for query in tracker.queries:
            print(query)
        assert len(tracker.queries) == 1
        assert len(res.data["all_books"]) == 4
        for book in res.data["all_books"]:
            assert book["id"]
            assert book["avg_rating_embedded"]


@pytest.mark.asyncio
async def test_aggregations_compared(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { ratings { rating }, id, avg_rating_embedded, ratings_by_book { avg_rating }}, agg { book_id, avg_rating} }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        for query in tracker.queries:
            print(query)
        assert len(tracker.queries) == 3
        assert len(res.data["all_books"]) == 4

        first_values = {}
        book_ratings = defaultdict(list)
        for book in res.data["all_books"]:
            assert book["id"]
            for rating in book["ratings"]:
                book_ratings[book["id"]].append(rating["rating"])
            assert book["avg_rating_embedded"]
            assert book["ratings_by_book"]
            assert book["ratings_by_book"]["avg_rating"] == book["avg_rating_embedded"]
            first_values[book["id"]] = book["avg_rating_embedded"]
        for book in res.data["agg"]:
            assert book["book_id"]
            assert book["avg_rating"] == first_values[book["book_id"]]
            assert book["avg_rating"] == int(sum(book_ratings[book["book_id"]]) / len(book_ratings[book["book_id"]]))


@pytest.mark.asyncio
async def test_book_author_ratings(schema, postgres_connection, basic_data):
    conn = postgres_connection

    with track_queries() as tracker:
        res = await schema.execute(
            "query { all_books { author { ratings { rating } } } }",
            context_value={"conn": conn},
        )
        assert res.errors is None
        assert len(tracker.queries) == 1
        assert len(res.data["all_books"]) == 4
        for book in res.data["all_books"]:
            assert book["author"]
            assert book["author"]["ratings"]
            for rating in book["author"]["ratings"]:
                assert rating["rating"]


@pytest.mark.asyncio
async def test_book_mutation(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation UpdateTitle($book_id: UUID!, $new_title: String!) { update_titles(book_id: $book_id, new_title: $new_title) { title, author { name } } }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
                "new_title": "Awesome title"
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 2
        assert res.data["update_titles"]
        assert res.data["update_titles"]["title"].startswith("Awesome title")


@pytest.mark.asyncio
async def test_book_mutation_save(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation UpdateTitle($book_id: UUID!, $new_title: String!) { update_title(book_id: $book_id, new_title: $new_title) { title, author { name } } }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
                "new_title": "Awesome title"
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 3
        assert res.data["update_title"]
        assert res.data["update_title"]["title"].startswith("Awesome title")


@pytest.mark.asyncio
async def test_insert_mutation(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]
    reviewer = basic_data["reviewers"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation NewReview($book_id: UUID!, $reviewer_id: UUID!, $rating: Int!) { new_review(book_id: $book_id, reviewer_id: $reviewer_id, rating: $rating) { id, rating, reviewer { id } } }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
                "reviewer_id": str(reviewer.id),
                "rating": 11
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 2
        assert res.data["new_review"]
        assert res.data["new_review"]["rating"] == 11
        assert res.data["new_review"]["reviewer"]["id"] == str(reviewer.id)


@pytest.mark.asyncio
async def test_nested_insert_mutation(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]
    reviewer = basic_data["reviewers"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation NewReview($book_id: UUID!, $reviewer_id: UUID!, $rating: Int!) { nested_new_review(book_id: $book_id, reviewer_id: $reviewer_id, rating: $rating) { ok, rating { id, rating, reviewer { id } }} }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
                "reviewer_id": str(reviewer.id),
                "rating": 11
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 2
        assert res.data["nested_new_review"]
        assert res.data["nested_new_review"]["ok"]
        assert res.data["nested_new_review"]["rating"]["rating"] == 11
        assert res.data["nested_new_review"]["rating"]["reviewer"]["id"] == str(reviewer.id)


@pytest.mark.asyncio
async def test_nested_insert_mutation_fail(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]
    reviewer = basic_data["reviewers"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation NewReview($book_id: UUID!, $reviewer_id: UUID!, $rating: Int!) { nested_new_review(book_id: $book_id, reviewer_id: $reviewer_id, rating: $rating) { ok, rating { id, rating, reviewer { id } }} }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
                "reviewer_id": str(reviewer.id),
                "rating": 0
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 0
        assert res.data["nested_new_review"]
        assert not res.data["nested_new_review"]["ok"]
        assert not res.data["nested_new_review"]["rating"]


@pytest.mark.asyncio
async def test_delete(schema, postgres_connection, basic_data):
    conn = postgres_connection

    first_book = basic_data["books"][0]

    with track_queries() as tracker:
        res = await schema.execute(
            "mutation Delete($book_id: UUID!) { delete_book(book_id: $book_id) { id } }",
            context_value={"conn": conn},
            variable_values={
                "book_id": str(first_book.id),
            }
        )
        assert res.errors is None
        assert len(tracker.queries) == 1
        assert res.data["delete_book"]
        assert res.data["delete_book"]["id"] == str(first_book.id)

    res = await schema.execute(
        "query { all_books { id }}",
        context_value={"conn": conn}
    )
    assert res.errors is None
    assert res.data["all_books"]
    assert len(res.data["all_books"]) == 3
    assert str(first_book.id) not in [b["id"] for b in res.data["all_books"]]
