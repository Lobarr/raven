from aiohttp import web

router = web.RouteTableDef()

@router.get('/ping')
async def ping(request):
  return web.json_response({'ping': 'pong'})
