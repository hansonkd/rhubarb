import inspect

from graphql import GraphQLResolveInfo
from strawberry.extensions import SchemaExtension
from strawberry.field import StrawberryField
from strawberry.types import Info

from rhubarb.object_set import pk_concrete, ObjectSet, Selector, optimize_selection, WrappedSelector, UpdateSet, \
    InsertSet


class RhubarbExtension(SchemaExtension):
    def on_execute(self):
        self.execution_context.context["object_sets"] = {}
        yield

    async def resolve(self, _next, root, info: GraphQLResolveInfo, *args, **kwargs):
        prev_key = (
            "|".join(v for v in info.path.prev.as_list() if isinstance(v, str))
            if info.path.prev
            else "|"
        )
        cur_key = "|".join(v for v in info.path.as_list() if isinstance(v, str))
        object_sets = self.execution_context.context["object_sets"]

        print("cur_key", cur_key, prev_key, object_sets.keys())
        if prefetched := object_sets.get(cur_key, None):
            print(f"found using {prefetched}, {prefetched.row_cache}")
            return await prefetched.for_pk(pk_concrete(root))

        field: StrawberryField = root and root._type_definition.get_field(info.field_name)
        real_info = Info(_raw_info=info, _field=field)
        selected_mapped = {
            f.name: f for f in real_info.selected_fields
        }
        if parent_object_set := object_sets.get(prev_key, None):
            accum: Selector = parent_object_set.selection
            model_ref = accum.__model_reference__()
            to_use_accum = accum.__inner_selector__()
            result = _next(to_use_accum, info, *args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            if not isinstance(result, ObjectSet):
                result = optimize_selection(selected_mapped[real_info.field_name].selections, result)

            if isinstance(result, ObjectSet):
                result = result.select(
                    lambda x: WrappedSelector(optimize_selection(selected_mapped[real_info.field_name].selections, x), model_ref, field)
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
            if isinstance(result, (InsertSet, UpdateSet)):
                result = await result.as_object_set(real_info)
            if isinstance(result, ObjectSet):
                result = result.select(
                    lambda x: optimize_selection(selected_mapped[real_info.field_name].selections, x)
                )
                print("selection", result.selection)
                object_sets[cur_key] = result
                return await result.resolve()

            return result



