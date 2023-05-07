import copy

import strawberry
from strawberry.scalars import JSON

from rhubarb import RhubarbExtension, Binary


class Schema(strawberry.Schema):
    def __init__(self, *args, **kwargs):
        extensions = copy.copy(kwargs.pop("extensions", []))
        if RhubarbExtension not in extensions:
            extensions.append(RhubarbExtension)
        kwargs["extensions"] = extensions

        scalar_overrides = copy.copy(kwargs.pop("scalar_overrides", {}))
        if bytes not in scalar_overrides:
            scalar_overrides[bytes] = Binary
            scalar_overrides[dict] = JSON
        kwargs["scalar_overrides"] = scalar_overrides
        super().__init__(*args, **kwargs)


class ErrorRaisingSchema(Schema):
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
