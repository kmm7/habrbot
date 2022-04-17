#!/usr/bin/env python3
import argparse
from aiohttp import web
import json

def generate_forecast(latitude, longitude):
    pass

async def forecast(request):
    latitude = 0
    longitude = 0
    forecast_data = generate_forecast(latitude, longitude)
    return web.Response(text=json.dumps(forecast_data))


def bad_status(param, hour=None):
    if hour is None:
        msg = 'Wrong {} has been passed'.format(param)
    else:
        msg = 'Wrong {} for hour {} has been passed'.format(param, hour)

    return web.Response(status=400, text=msg)



async def health(request):
    return web.Response(text="OK")


def arg_parser():
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('--port',
                        type=int,
                        default=8080,
                        help='Port to serve on')
    parser.add_argument('--host',
                        default='0.0.0.0',
                        help='Host to serve on')
    return parser


def setup_routes(app):
    app.router.add_get('/', health)
    app.router.add_get('/forecast', forecast)


def run_server(host, port):
    app = web.Application()
    setup_routes(app)
    web.run_app(app, host=host, port=port)


def main():
    parser = arg_parser()
    args = parser.parse_args()

    try:
        run_server(args.host, args.port)
    except KeyboardInterrupt:
        ...


if __name__ == '__main__':
    main()
