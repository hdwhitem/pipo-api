from typing import Any
from bson import ObjectId
from pydantic_core import core_schema

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(cls.validate),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, value: Any) -> str:
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, str) and ObjectId.is_valid(value):
            return value
        raise ValueError("Invalid ObjectId")