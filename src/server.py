#!/usr/bin/env python3
import argparse
import asyncio
import base64
import datetime
import io
import string

import aiohttp
from aiohttp import web
from aiohttp import hdrs
import json

try:
    import uvloop
except ImportError:
    uvloop = None


DEFAULT_SERVER_HEADER = 'Cors/{}'.format('1.0')
STORAGE = []  # [{probability: number, amount: number}]
DATE_FORMAT = '%FT%T+02:00'


def generate_forecast(latitude, longitude):
    result = [{
        "location": {
            "timeZoneName": "Europe/Berlin",
            "latitude": latitude,
            "stationId": "3010277",
            "longitude": longitude
        },
        "forecasts": {
            "hourly": []
        }
    }]

    hourly = result[0]['forecasts']['hourly']

    time = datetime.datetime.now()
    current_hour = time.hour

    for hour in range(168):
        validAt = datetime.datetime(
                time.year, time.month, time.day, time.hour) + \
            datetime.timedelta(hours=hour)
        ihour = hour % 24
        probability = STORAGE[ihour]['probability']
        amount = STORAGE[ihour]['amount']

        data = {
            'validAt': validAt.strftime(DATE_FORMAT),
            'precipitationProbabilityInPercent100based': probability,
            'precipitationPastInterval': {
                "unit": "MILLIMETER",
                "value": amount
            }
        }

        hourly.append(data)

    return result


async def forecast(request):
    latitude = 0
    longitude = 0
    forecast_data = generate_forecast(latitude, longitude)
    return web.Response(text=json.dumps(forecast_data))


def convert_type(value, clazz):
    if value is None:
        return None
    try:
        return clazz(value)
    except ValueError:
        return None


def check_bounds(value, minimum, maximum):
    if value is None:
        return None
    if value < minimum or value > maximum:
        return None
    return value


def convert(params):
    hour = check_bounds(convert_type(params.get('hour'), int), 0, 23)
    probability = check_bounds(convert_type(params.get('probability'), int), 0, 100)
    amount = check_bounds(convert_type(params.get('amount'), float), 0, 100000)
    return hour, probability, amount


def bad_status(param, hour=None):
    if hour is None:
        msg = 'Wrong {} has been passed'.format(param)
    else:
        msg = 'Wrong {} for hour {} has been passed'.format(param, hour)

    return web.Response(status=400, text=msg)


async def reconfig(params):
    hour, probability, amount = convert(params)
    if hour is None:
        return bad_status('hour')

    if probability is None:
        return bad_status('probability', hour)

    if amount is None:
        return bad_status('amount', hour)

    STORAGE[hour]['probability'] = probability
    STORAGE[hour]['amount'] = amount
    return web.Response(text="OK")


async def save(request):
    return web.Response(text=json.dumps(STORAGE))


async def restore(request):
    data = await request.json(loads=json.loads)
    result = []
    res = map(lambda d: {
            'probability':d.get('probability'),
            'amount': d.get('amount')
        }, data)
    for hour, d in enumerate(res):
        _, probability, amount = convert(d)

        if probability is None:
            return bad_status('probability', hour)

        if amount is None:
            return bad_status('amount', hour)

        d['probability'] = probability
        d['amount'] = amount
        result.append(d)

    if len(result) != 24:
        return bad_status('hour amount')

    STORAGE[:] = result
    return web.Response(text="OK")


async def params(request):
    if request.method == hdrs.METH_GET:
        return request.query
    elif request.method == hdrs.METH_POST:
        return await request.post()


async def config(request):
    return await reconfig(await params(request))


async def config_single(request):
    reset(request)
    return await config(request)


def reset(request):
    result = []
    for i in range(24):
        result.append({'probability': 0, 'amount': 0.0})

    STORAGE[:] = result
    return web.Response(text="OK")


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
    app.router.add_get('/reset', reset)
    app.router.add_get('/forecast', forecast)
    app.router.add_get('/config', config)
    app.router.add_post('/config', config)
    app.router.add_get('/config_single', config_single)
    app.router.add_post('/config_single', config_single)
    app.router.add_get('/save', save)
    app.router.add_post('/restore', restore)


def run_server(host, port):
    if uvloop:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    app = web.Application()
    setup_routes(app)
    web.run_app(app, host=host, port=port)


def main():
    parser = arg_parser()
    args = parser.parse_args()

    reset(None)
    try:
        run_server(args.host, args.port)
    except KeyboardInterrupt:
        ...


if __name__ == '__main__':
    main()
