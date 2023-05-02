# Rhubarb - The Funky Sweet ORM built on Strawberry GraphQL

Rhubarb is an ORM written from scratch focused on optimizing traversing 

## 

The major ORM's have been built separately from the API's they wish to provide data. This results in the need for python computations to extract the data from the query in order to transform it into the format necessary for the API.

Lets take a quick look between Rhubarb and Django to get an idea:

```python
class Book(models.Model):
    name = models.TextField()
    rating = models.IntegerField()
    author = models.ForeignKey(Author)

    
class Author(models.Model):
    name = models.TextField()

authors_by_avg_rating = Author.objects.annotate(
    avg_book_rating=Subquery(
        Book.objects.filter(
            author_id__in=OuterRef("pk")
        ).annotate(
            rating_avg=Avg("rating")
        ).values("rating_avg")
    )
)
```

Rhubarb

```python
import uuid
from rhubarb.model import  BaseModel, column, table, relation
from rhubarb.object_set import ModelSelector, avg_agg

@table
class Author(BaseModel):
    name: str = column()

    @relation
    def books(self: ModelSelector[Self], book: ModelSelector[Book]):
        return self.id == book

    @column(virtual=True)
    def avg_book_rating(self: ModelSelector):
        return avg_agg(self, self.books().rating)
    
@table
class Book(BaseModel):
    name: str = column()
    rating: int = column()
    author_id: uuid.UUID = column(references=Author)
```