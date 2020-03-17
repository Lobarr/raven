from cerberus import Validator
from typing import Optional
from api.admin.validate import admin_schema
from api.util import Hasher
from pydash import omit, omit_by, has, merge, is_empty


class AdminDTO:
    def __init__(self):
        self.id: Optional[str] = None
        self.email: Optional[str]
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.token: Optional[str] = None

        self.__schema = admin_schema
        self.__validator = Validator(self.__schema)

    def to_dict(self) -> dict:
        transformed_data = merge(
            omit(self.__dict__, '_AdminDTO__schema', '_AdminDTO__validator', 'id'),
            {'_id': self.id}
        )

        return omit_by(transformed_data, lambda v: is_empty(v))

    def is_valid(self) -> bool:
        return self.__validator.validate(self.to_dict())

    def get_validation_errors(self) -> list:
        return self.__validator.errors

    def hash_password(self):
        self.password = Hasher.hash(self.password)



