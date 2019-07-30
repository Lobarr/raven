import asyncio
import bson
from motor.motor_asyncio import AsyncIOMotorClient
from cerberus import Validator
from .schema import request_validator_schema, request_validator
from password_strength import PasswordPolicy, PasswordStats

class RequestValidator:
	@staticmethod
	async def create(ctx, db):
		"""
		Creates a request validation entry.

		@param document: (object) document to be inserted
		@param db: (object) db connection
		"""
		await db.insert_one(ctx)

	@staticmethod
	async def update(id, ctx, db):
		"""
		Updates a request validation entry.

		@param id: (string) the ID of the request validation entry to update
		@param document: (object) the data to be inserted into this request validation entry
		@param db: (object) db connection
		"""

		await db.update_one({'_id': bson.ObjectId(id)}, {'$set': ctx})
        
	@staticmethod
	async def delete(id, db):
		"""
		Deletes a request validation entry.

		@param id_: (string) the ID of the request validation entry to delete
		@param db: (object) db connection
		@return: true for success, false for failure (expand on this after discussion)
		"""
		await db.delete_one({'_id': bson.ObjectId(id)})
			
	@staticmethod
	async def get_all(db):
		"""
		Gets all request validation entries
		
		@param db: (object) db connection
		@return: the documents with the provided serviceId
		"""
		res = await db.find({})
		return res.to_list(100)

	@staticmethod
	async def get_by_service_id(service_id, db):
		"""
		Gets a request validation entry by the service_id provided

		@param service_id: (string) ID for the service which the request is (coming from? targeting?)
		@param db: (object) db connection
		@return: the documents with the provided serviceId
		"""
		res = await db.find({"service_id": service_id})
		return res.to_list(100)
	
	@staticmethod
	async def get_by_method(method, db):
		"""
		Gets a request validation entry by the method provided

		@param method: (string) HTTP method that the request is transmitted by
		@param db: (object) db connection
		@return: the documents using the provided method
		"""
		res = await db.find({"method": method})
		return res.to_list(100)
	
	@staticmethod
	async def get_by_endpoint(endpoint, db):
		"""
		Gets a request validation entry by the path provided

		@param path: (string) path of the request
		@param db: (object) db connection
		@return: the documents with the provided path
		"""
		res = await db.find({"endpoint": endpoint})
		return res.to_list(100)

	@staticmethod
	async def validate_schema(request_body, schema):
		"""
		Validates that the request body provided matches the schema for the request.

		@param request_body: (object) request body in dictionary format
		@param schema
		"""
		request_validator = Validator(schema)
		if not request_validator.validate(request_body):
			raise Exception({
				'message': 'Body provided does not match provided schema',
				'status_code': 400
			})

	@staticmethod
	async def enforce_policy(password: str, policy: object):
		"""
		Validates that the given password matches the provided password policy.

		@param password: (string) password to be validated
		@param policy: (object) dict containing the password requirements
		"""
		password_policy = PasswordPolicy.from_names(
			length=policy['length'],
			uppercase=policy['upper_case_count'],
			numbers=policy['numbers_count'],
			special=policy['specials_count'],
			nonletters=policy['non_letters_count'],
		)
		
		res = password_policy.test(password)
		if res != []:
			raise Exception({
				'message': 'Password provided does not match policy configured',
				'status_code': 400
			})

	@staticmethod
	async def enforce_strength(password: str, strength_percentage: float):
		stats = PasswordStats(password)
		if stats.strength() < strength_percentage:
			raise Exception({
				'message': 'Password strength not up to standard',
				'status_code': 400
			})
