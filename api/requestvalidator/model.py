import asyncio
import bson
from motor.motor_asyncio import AsyncIOMotorClient
from cerberus import Validator
from api.requestvalidator.schema import requestvalidator_schema, request_validator
from password_strength import PasswordPolicy

class RequestValidator:

    @staticmethod
    async def create(document, db):
        """
        Creates a request validation entry.

        @param document: (object) document to be inserted
        @param db: (object) db connection
        """
        if request_validator.validate(document) is True:
            await db.insert_one(document)
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })

    @staticmethod
    async def update(id, document, db):
        """
        Updates a request validation entry.

        @param id: (string) the ID of the request validation entry to update
        @param document: (object) the data to be inserted into this request validation entry
        @param db: (object) db connection
        """

        # first we find the document which already exists and then update
        # currently searches on objectId but easy to change to diff
        if request_validator.validate(document) is True and bson.ObjectId.is_valid(id):
            await db.update_one({'_id': bson.ObjectId(id)}, {'$set': document})
        else:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
        
    @staticmethod
    async def delete(id, db):
        """
        Deletes a request validation entry.

        @param id_: (string) the ID of the request validation entry to delete
        @param db: (object) db connection
        @return: true for success, false for failure (expand on this after discussion)
        """
        if bson.ObjectId.is_valid(id) != True:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
        await db.delete_one({'_id': bson.ObjectId(id)})
        
    @staticmethod
    async def get_all(db):
        """
        Gets all request validation entries
        
        @param db: (object) db connection
        @return: the documents with the provided serviceId
        """
        # not sure if this needs to be broken into 3 seperate methods
        return await db.find({}).to_list(100)

    @staticmethod
    async def get_by_service_id(service_id, db):
        """
        Gets a request validation entry by the service_id provided

        @param service_id: (string) ID for the service which the request is (coming from? targeting?)
        @param db: (object) db connection
        @return: the documents with the provided serviceId
        """
        return await db.find({"serviceId": service_id}).to_list(100)
    
    @staticmethod
    async def get_by_method(method, db):
        """
        Gets a request validation entry by the method provided

        @param method: (string) HTTP method that the request is transmitted by
        @param db: (object) db connection
        @return: the documents using the provided method
        """
        return await db.find({"method": method}).to_list(100)
    
    @staticmethod
    async def get_by_path(path, db):
        """
        Gets a request validation entry by the path provided

        @param path: (string) path of the request
        @param db: (object) db connection
        @return: the documents with the provided path
        """
        return await db.find({"path": path}).to_list(100)

    @staticmethod
    async def validate_schema(request_body, schema):
        """
        Validates that the request body provided matches the schema for the request.

        @param request_body: (object) request body in dictionary format
        @param schema: (object) schema for the expected request body
        @return: true if the request body matches the schema, false otherwise
        """
        # need to think whether schema gets passed or other identifying info
        request_validator = Validator(schema)
        if not request_validator.validate(request_body):
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })

    @staticmethod
    async def validate_password(password, password_policy):
        """
        Validates that the given password matches the provided password policy.

        @param password: (string) password to be validated
        @param password_policy: (object) dict containing the password requirements
        @return: true if the password is valid, false otherwise
        """
        policy = PasswordPolicy.from_names(
            length=password_policy.length, 
            uppercase=password_policy.upperCaseCount,  
            numbers=password_policy.numbersCount,
            special=password_policy.specialCount,
            nonletters=password_policy.nonLetterCount,
        )
        # validate against the constructed policy
        result = policy.test(password)
        if result != []:
            raise Exception({
                'message': 'Invalid data provided',
                'status_code': 400
            })
