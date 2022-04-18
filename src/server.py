#!/usr/bin/env python3
import argparse
import os
from aiohttp import web


def html_response(dir, document):
    file_path = os.path.join(dir, document)
    s = open(file_path, "r")
    return web.Response(text=s.read(), content_type='text/html')


async def data_handler(request):
    return html_response('data', 'history.csv')


async def client_handler(request):
    return html_response('', 'client.html')


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
    app.router.add_get('/', client_handler)
    app.router.add_get('/health', health)
    app.router.add_get('/data', data_handler)


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
