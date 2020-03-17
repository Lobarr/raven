import bson
import time

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pydash import omit, merge, is_empty, has
from api.providers import DBProvider
from api.admin.schema import AdminDTO
from api.util import Hasher, Token, DB, Bson
from api.util.env import RAVEN_ADMIN_PASS, RAVEN_ADMIN_USER


collection_name = 'admin'


class Admin:
    @staticmethod
    async def create(admin: AdminDTO, db_provider: DBProvider):
        """
        creates an admin

        @param ctx: (object) context of admin
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        admin.hash_password()
        await db.insert_one(admin.to_dict(), session=db_provider.get_mongo_session())

    @staticmethod
    async def update(admin: AdminDTO, db_provider: DBProvider):
        """
        updates an admin

        @param id: (str) id of admin to update
        @param ctx: (object)
        """
        db = db_provider.get_mongo_collection(collection_name)

        if admin.password:
            admin.hash_password()

        await db.update_one(
            {'_id': bson.ObjectId(admin.id)}, 
            {'$set': admin.to_dict()}, 
            session=db_provider.get_mongo_session()
        )

    @staticmethod
    async def get_by_id(_id: str, db_provider: DBProvider) -> Optional[AdminDTO]:
        """
        gets an admin by id


        @param id: id of admin
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        admin_context = await db.find_one({'_id': bson.ObjectId(_id)}, session=db_provider.get_mongo_session())

        if is_empty(admin_context):
            return None

        formatted_admin = DB.format_document(Bson.to_json(admin_context))

        return Admin.make_dto(formatted_admin)

    @staticmethod
    async def get_by_email(email: str, db_provider: DBProvider) -> Optional[AdminDTO]:
        """
        gets an admin by email


        @param email: email of admin
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        admin_context = await db.find_one({'email': email}, session=db_provider.get_mongo_session())
        
        if is_empty(admin_context):
            return None

        formatted_admin = DB.format_document(Bson.to_json(admin_context))

        return Admin.make_dto(formatted_admin)

    @staticmethod
    async def get_by_username(username: str, db_provider: DBProvider) -> Optional[AdminDTO]:
        """
        gets an admin by username


        @param username: username of admin
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        admin_context = await db.find_one({'username': username}, session=db_provider.get_mongo_session())

        if is_empty(admin_context):
            return None

        formatted_admin = DB.format_document(Bson.to_json(admin_context))

        return Admin.make_dto(formatted_admin)


    @staticmethod
    async def generate_token(admin: AdminDTO, db_provider: DBProvider):
        sanitized_payload = merge(
            omit(admin.to_dict(), 'password', 'token'),
            {'timestamp': repr(time.time())}
        )

        admin.token = Token.generate(sanitized_payload)

        await Admin.update(admin, db_provider)

    @staticmethod
    async def verify_password(username: str, password: str, db_provider: DBProvider) -> bool:
        """
        verfies admin password

        @param username: (str) username of admin
        @param password: (str) password to check
        @param db: mongo instance
        """
        admin = await Admin.get_by_username(username, db_provider)
        cur_password = ''

        if admin:
            cur_password = admin.password
        else:
            raise Exception({
                'message': 'Admin does not exist',
                'status_code': 404
            })

        match = Hasher.validate(password, cur_password)
        if match:
            await Admin.generate_token(admin, db_provider)

        return match

    @staticmethod
    async def get_all(db_provider: DBProvider) -> List[AdminDTO]:
        """
        gets all admins

        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)
        res = db.find({}, session=db_provider.get_mongo_session())
        admin_contexts = await res.to_list(100)

        return [Admin.make_dto(Bson.to_json(admin_context))
                for admin_context in DB.format_documents(admin_contexts)]

    @staticmethod
    async def count(db_provider: DBProvider) -> int:
        """
        counts admins

        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        return await db.count_documents({}, session=db_provider.get_mongo_session())

    @staticmethod
    async def remove_by_id(_id: str, db_provider: DBProvider):
        """
        removes an id

        @param id: (str) id of admin
        @param db: mongo instance
        """
        db = db_provider.get_mongo_collection(collection_name)

        await db.delete_one({'_id': bson.ObjectId(_id)}, session=db_provider.get_mongo_session())

    @staticmethod
    async def create_default(db_provider: DBProvider):
        """
        create a default admin if none exists

        @param db: mongo instance
        """
        admins_count = await Admin.count(db_provider)

        if admins_count == 0:
            admin = Admin.make_dto({
                'username': RAVEN_ADMIN_USER,
                'password': RAVEN_ADMIN_PASS
            })
            
            await Admin.create(admin, db_provider)

    @staticmethod
    def make_dto(ctx: dict) -> AdminDTO:
        admin = AdminDTO()

        if has(ctx, '_id') or has(ctx, 'id'):
            admin.id = ctx['_id'] if '_id' in ctx else ctx['id']

        if has(ctx, 'email'):
            admin.email = ctx['email']

        if has(ctx, 'username'):
            admin.username = ctx['username']

        if has(ctx, 'password'):
            admin.password = ctx['password']

        if has(ctx, 'token'):
            admin.token = ctx['token']

        return admin
