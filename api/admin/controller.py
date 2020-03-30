import json
import multidict
import copy

from typing import List, Optional
from pydash import has, is_empty
from bson import json_util
from aiohttp import web
from api.admin import Admin, AdminDTO
from api.util import Error, Bson, DB, Validate, Token

router = web.RouteTableDef()

@router.post('/admin/login')
async def login_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        ctx = json.loads(await request.text())

        if not has(ctx, 'username') or not has(ctx, 'password'):
            raise Exception({
                'message': 'Bad Request',
                'status_code': 400
            })

        verified = await Admin.verify_password(
            ctx['username'], ctx['password'],
            db_provider
        )

        if not verified:
            raise Exception({
                'message': 'Unauthorized',
                'status_code': 401
            })
        
        await db_provider.start_mongo_transaction()

        admin = await Admin.get_by_username(ctx['username'], db_provider)

        await db_provider.end_mongo_transaction()

        return web.json_response({
            'data': admin.to_dict() if admin else admin
        })

    except Exception as err:
        return Error.handle(err)


@router.post('/admin')
async def post_handler(request: web.Request):
    try:
        # TODO: make sure no duplicate email, username

        db_provider = copy.deepcopy(DB.get_provider(request))
        admin_context = json.loads(await request.text())
        admin = Admin.make_dto(admin_context)

        if not admin.is_valid():
            raise Exception({
                'message': admin.get_validation_errors(),
                'status_code': 400
            })

        await db_provider.start_mongo_transaction()
        await Admin.create(admin, db_provider)
        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Admin created',
        })
    except Exception as err:
        return Error.handle(err)


@router.get('/admin')
async def get_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        has_prop = len(request.rel_url.query.keys()) > 0

        await db_provider.start_mongo_transaction()
        
        if not has_prop:
            admins = await Admin.get_all(db_provider)

            await db_provider.end_mongo_transaction()

            return web.json_response({
                'data': [admin.to_dict() for admin in admins],
                'status_code': 200
            })
        else:
            admin: Optional[AdminDTO] = None

            if 'id' in request.rel_url.query:
                admin_id = request.rel_url.query.get('id')
                Validate.validate_object_id(admin_id)

                admin = await Admin.get_by_id(admin_id, db_provider)

            elif 'email' in request.rel_url.query:
                admin_email = request.rel_url.query.get('email')
                admin = await Admin.get_by_email(admin_email, db_provider)

            elif 'username' in request.rel_url.query:
                admin_username = request.rel_url.query.get('username')
                admin = await Admin.get_by_username(admin_username, db_provider)

            await db_provider.end_mongo_transaction()

            return web.json_response({
                'data': admin.to_dict() if admin else admin,
                'status_code': 200
            })

    except Exception as err:
        return Error.handle(err)


@router.patch('/admin')
async def patch_handler(request: web.Request):
    try:
        db_provider = copy.deepcopy(DB.get_provider(request))
        admin_context = json.loads(await request.text())
        admin = Admin.make_dto(admin_context)

        Validate.validate_object_id(admin.id)

        if not admin.is_valid():
            raise Exception({
                'message': admin.get_validation_errors(),
                'status_code': 400
            })

        await db_provider.start_mongo_transaction()

        await Admin.update(admin, db_provider)

        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Admin updated',
        })
    except Exception as err:
        return Error.handle(err)


@router.delete('/admin')
async def delete_handler(request: web.Request):
    try:
        if not has(request.rel_url.query, 'id'):
            raise Exception({
                'message': 'Bad Request',
                'status_code': 400
            })

        Validate.validate_object_id(request.rel_url.query.get('id'))

        db_provider = copy.deepcopy(DB.get_provider(request))

        await db_provider.start_mongo_transaction()

        await Admin.remove_by_id(request.rel_url.query.get('id'), db_provider)

        await db_provider.end_mongo_transaction()

        return web.json_response({
            'message': 'Admin deleted'
        })
    except Exception as err:
        return Error.handle(err)
