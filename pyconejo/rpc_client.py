#!/usr/bin/env python
import argparse
import logging
import pika
import os
import uuid
import sys
import uuid
from pyconejo import core

LOG = logging.getLogger('pyconejo.rpc_client')

def setup_options(argv=None):
    parser = argparse.ArgumentParser(description='Publisher of messages.')
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        help='quiet, produces output suitable for scripts')
    parser.add_argument('-n', '--num-messages', dest='num_messages',
                        metavar='N', default=0, type=int,
                        help=("number of messages before exiting, "
                              "0 means don't stop"))
    parser.add_argument('-r', '--routing-key', dest='routing_key',
                        default='rpc_queue', help='routing key')
    parser.add_argument('-c', '--concurrent', dest='processes',
                        metavar='N', default=1, type=int,
                        help='number of multiple requests to make at a time')

    return parser.parse_args(argv)


class RpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)
        self.routing_key = 'rpc_queue'

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=self.routing_key,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


def main():
    args = setup_options()
    core.setup_logging(level=logging.WARN if args.quiet else logging.DEBUG)

    if core.forkme_and_wait(args.processes):
        # I'm the father and I'm done
        sys.exit(0)

    rpc = RpcClient()
    rpc.routing_key = args.routing_key

    i = 0
    while i < args.num_messages:
        arg = str(uuid.uuid4())
        LOG.debug("Requesting echo(%s)" % arg)
        response = rpc.call(arg)
        LOG.info("Got %r" % (response,))
        assert arg == response, "%s != %s" % (arg, response)
        i += 1


if __name__ == "__main__":
    main()
