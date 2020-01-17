from aiohttp import web
from api.util import Error, Token, DB
from api.admin import Admin

TOKEN_HEADER_KEY = 'x-raven-token'

@web.middleware
async def auth_middleware(request: web.Request, handler: web.RequestHandler):
  try:
    if '/admin/login' not in request.path_qs:
      err = {
      'message': 'Unauthorized!',
        'status_code': 401
      }
      token = request.headers.get(TOKEN_HEADER_KEY)

      if not token:
        raise Exception(err)

      token_context = Token.decode(token)
      admin = await Admin.get_by_id(token_context['_id'], DB.get(request))

      if not admin or 'token' not in admin or admin['token'] != token:
        raise Exception(err)

    return await handler(request)
  except Exception as err:
    return Error.handle(err)
