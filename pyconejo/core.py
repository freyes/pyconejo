import argparse
import logging
import os
import pika
import json
import signal
import socket
import sys
import urllib


LOG_FORMAT = ('%(levelname) -6s %(asctime)s %(process)d %(name)s: %(message)s')
DEFAULT_TOPIC = 'pyconejo'
DEFAULT_SERVER_NAME = socket.gethostname().split('.')[0]


def rabbit_connection_url(host=None, port=None, username=None, password=None,
                          vhost=None, driver='amqp'):

    params = {
        'host': host or os.environ.get('PYCONEJO_HOST', 'localhost'),
        'port': int(port or os.environ.get('PYCONEJO_PORT', 5672)),
        'username': username or os.environ.get('PYCONEJO_USERNAME', 'guest'),
        'password': password or os.environ.get('PYCONEJO_PASSWORD', 'guest'),
        'virtual_host': urllib.quote(vhost or os.environ.get('PYCONEJO_VHOST',
                                                             '/'), safe=''),
        'driver': driver,
    }

    return ("%(driver)s://%(username)s:%(password)s@%(host)s:%(port)s"
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


def forkme_and_wait(num_processes):
    """
    :returns: False for children, True for father
    """
    i = 0
    pids = []
    while True:
        pid = os.fork()
        if pid == 0:
            return False
        pids.append(pid)
        i += 1
        if i >= num_processes:
            break

    # wait until childs exit
    while len(pids) > 0:
        i = 0
        while i < len(pids):
            pid = pids[i]
            try:
                os.waitpid(pid, 0)
                i += 1
            except OSError:
                pids.remove(pid)
            except KeyboardInterrupt:
                os.kill(pid, signal.SIGTERM)

    return True


def common_options_server(parser=None, description=''):
    if parser is None:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='quiet, produces output suitable for scripts')
    parser.add_argument('-n', '--num-messages', dest='num_messages',
                        metavar='N', default=0, type=int,
                        help=("number of messages before exiting, "
                              "0 means don't stop"))
    parser.add_argument('-r', '--routing-key', dest='routing_key',
                        default='example.*', help='routing key')

    parser.add_argument('-d', '--response-delay', dest="response_delay",
                        default=0, metavar="N", type=float,
                        help="Wait N seconds before answering to the request")
    return parser


def common_options_client(parser=None, description=''):
    if parser is None:
        parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-i', '--publish-interval', dest='publish_interval',
                        metavar='N', default=1, type=float,
                        help='publish messages every N seconds')
    parser.add_argument('-n', '--num-messages', dest='num_messages',
                        metavar='N', default=0, type=int,
                        help=("number of messages before exiting, "
                              "0 means don't stop"))
    parser.add_argument('-m', '--message', dest='message',
                        metavar='MSG', default=json.dumps({'hello': 'world'}),
                        help="message content to publish")
    parser.add_argument('-c', '--concurrent', dest='processes',
                        metavar='N', default=1, type=int,
                        help='number of multiple requests to make at a time')
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='quiet, produces output suitable for scripts')
    return parser
