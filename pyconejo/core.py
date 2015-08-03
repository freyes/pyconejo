import logging
import os
import pika
import sys
import urllib


LOG_FORMAT = ('%(levelname) -6s %(asctime)s %(process)d %(name)s: %(message)s')


def rabbit_connection_url(host=None, port=None, username=None, password=None,
                          vhost=None):

    params = {
        'host': host or os.environ.get('PYCONEJO_HOST', 'localhost'),
        'port': int(port or os.environ.get('PYCONEJO_PORT', 5672)),
        'username': username or os.environ.get('PYCONEJO_USERNAME', 'guest'),
        'password': password or os.environ.get('PYCONEJO_PASSWORD', 'guest'),
        'virtual_host': urllib.quote(vhost or os.environ.get('PYCONEJO_VHOST',
                                                             '/'), safe=''),
    }

    return ("amqp://%(username)s:%(password)s@%(host)s:%(port)s"
            "/%(virtual_host)s") % params


def rabbit_connect(host=None, port=None, username=None, password=None,
                   vhost=None):
    creds = pika.credentials.PlainCredentials(
        username=username or os.environ.get('PYCONEJO_USERNAME', 'guest'),
        password=password or os.environ.get('PYCONEJO_PASSWORD', 'guest'))

    params = {
        'host': host or os.environ.get('PYCONEJO_HOST', 'localhost'),
        'port': int(port or os.environ.get('PYCONEJO_PORT', 5672)),
        'credentials': creds,
        'virtual_host': vhost or os.environ.get('PYCONEJO_VHOST', '/'),
    }
    conn = pika.BlockingConnection(pika.ConnectionParameters(**params))
    return conn


def setup_logging(stream=None, level=logging.DEBUG):
    logging.basicConfig(stream=stream or sys.stderr,
                        level=level, format=LOG_FORMAT)

    # pika can be overly verbose in debug mode
    pika_logger = logging.getLogger('pika')
    pika_logger.setLevel(logging.INFO if level <= logging.DEBUG else level)
