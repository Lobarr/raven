from cerberus import Validator
from typing import Optional, List, Any
from api.endpoint_cacher.validate import endpoint_cacher_schema
from api.util import Hasher
from pydash import omit, omit_by, has, merge, is_none


class EndpointCacherDTO:
    def __init__(self):
        self.id: Optional[str] = None
        self.service_id: Optional[str] = None
        self.timeout: Optional[int] = None
        self.response_codes: Optional[List[int]] = None

        self.__schema = endpoint_cacher_schema
        self.__validator = Validator(self.__schema)

    def to_dict(self) -> dict:
        transformed_data = merge(
            omit(self.__dict__, '_EndpointCacherDTO__schema', '_EndpointCacherDTO__validator', 'id'),
            {'_id': self.id}
        )

        return omit_by(transformed_data, lambda v: is_none(v))

    def is_valid(self) -> bool:
        return self.__validator.validate(self.to_dict())

    def get_validation_errors(self) -> list:
        return self.__validator.errors

    def is_field_none(self, field: str) -> bool:
        if has(self.__dict__, field):
            return is_none(self.__dict__[field])
        return True

    def get_field(self, field: str) -> Any:
        if has(self.__dict__, field):
            return self.__dict__[field]
        return None
