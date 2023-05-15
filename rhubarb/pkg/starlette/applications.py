from starlette.applications import Starlette
from strawberry.asgi import GraphQL as OrigGraphQL


class GraphQL(OrigGraphQL):
    pass
