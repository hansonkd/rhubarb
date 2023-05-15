import inspect

from graphql import GraphQLResolveInfo
from psycopg import Rollback
from strawberry.extensions import SchemaExtension
from strawberry.field import StrawberryField
from strawberry.types import Info
from strawberry.types.graphql import OperationType

from rhubarb.pkg.postgres.connection import connection, override_conn
from rhubarb.object_set import (
    pk_concrete,
    ObjectSet,
    Selector,
    optimize_selection,
    WrappedSelector,
    UpdateSet,
    InsertSet,
    MutationSet,
)


class RhubarbExtension(SchemaExtension):
    async def on_execute(self):
        self.execution_context.context["object_sets"] = {}
        if "conn" not in self.execution_context.context:
            async with connection() as conn:
                self.execution_context.context["conn"] = conn
                yield
        else:
            yield

    async def resolve(self, _next, root, info: GraphQLResolveInfo, *args, **kwargs):
        prev_key = (
            "|".join(v for v in info.path.prev.as_list() if isinstance(v, str))
            if info.path.prev
            else "|"
        )
        cur_key = "|".join(v for v in info.path.as_list() if isinstance(v, str))
        object_sets = self.execution_context.context["object_sets"]

        if prefetched := object_sets.get(cur_key, None):
            return await prefetched.for_pk(pk_concrete(root))

        field: StrawberryField = root and hasattr(root, "_type_definition") and root._type_definition.get_field(
            info.field_name
        )
        real_info = Info(_raw_info=info, _field=field)
        selected_mapped = {f.name: f for f in real_info.selected_fields}
        if parent_object_set := object_sets.get(prev_key, None):
            accum: Selector = parent_object_set.selection
            model_ref = accum.__model_reference__()
            to_use_accum = accum.__inner_selector__()
            result = _next(to_use_accum, info, *args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, ObjectSet):
                result = optimize_selection(
                    selected_mapped[real_info.field_name].selections, result
                )

            if isinstance(result, ObjectSet):
                result = result.select(
                    lambda x: WrappedSelector(
                        optimize_selection(
                            selected_mapped[real_info.field_name].selections, x
                        ),
                        model_ref,
                        field,
                    )
                )
                await parent_object_set.sync_cache(result)
                object_sets[cur_key] = result
                return await result.for_pk(pk_concrete(root))
            elif isinstance(result, Selector):
                new_selector = WrappedSelector(result, model_ref, field)
                os: ObjectSet = parent_object_set.select(lambda _: new_selector)
                await parent_object_set.sync_cache(os)
                object_sets[cur_key] = os
                return await object_sets[cur_key].for_pk(pk_concrete(root))
            return result
        else:
            result = _next(root, info, *args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            if isinstance(result, MutationSet):
                result = await result.as_object_set(real_info)
            if isinstance(result, ObjectSet):
                result = result.select(
                    lambda x: optimize_selection(
                        selected_mapped[real_info.field_name].selections, x
                    )
                )
                object_sets[cur_key] = result
                return await result.resolve()

            return result


class TransactionalMutationExtension(SchemaExtension):
    async def on_execute(self):
        if self.execution_context.operation_type == OperationType.MUTATION:
            if "conn" not in self.execution_context.context:
                async with connection() as conn:
                    self.execution_context.context["conn"] = conn
                    async with conn.transaction() as txn:
                        yield
                        result = self.execution_context.result
                        if result and result.errors:
                            raise Rollback(txn)
            else:
                conn = self.execution_context.context["conn"]
                async with conn.transaction() as txn:
                    yield
                    result = self.execution_context.result
                    if result and result.errors:
                        raise Rollback(txn)
        else:
            yield


class RhubarbTestingExtension(SchemaExtension):
    def __init__(self, *, execution_context, conn=None):
        self.conn = conn
        super().__init__(execution_context=execution_context)

    async def on_execute(self):
        with override_conn(self.conn):
            yield
