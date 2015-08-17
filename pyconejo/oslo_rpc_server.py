import eventlet
eventlet.monkey_patch()

import logging
import oslo_messaging
from pyconejo import core
from oslo_config import cfg


LOG = logging.getLogger('pyconejo.oslo_rpc_server')


def setup_options(argv=None):
    parser = core.common_options_server()

    return parser.parse_args(argv)


class ServerControlEndpoint(object):

    target = oslo_messaging.Target(namespace='control',
                                   version='2.0')

    def __init__(self, server):
        self.server = server
        self._counter = 0

    def stop(self, ctx):
        if self.server:
            self.server.stop()

    def test(self, ctx, arg):
        self._counter += 1
        LOG.info('Received message # %s (%s): %s',
                 self._counter, str(ctx), arg)
        return arg


class TestEndpoint(object):

    def test(self, ctx, arg):
        return arg


def main(argv=None):
    opts = setup_options(argv)
    core.setup_logging(level=logging.WARN if opts.quiet else logging.DEBUG)

    transport = oslo_messaging.get_transport(cfg.CONF)
    target = oslo_messaging.Target(topic='test', server='server1')
    endpoints = [
        ServerControlEndpoint(None),
        TestEndpoint(),
    ]
    server = oslo_messaging.get_rpc_server(transport, target, endpoints,
                                           executor='eventlet')
    endpoints[0].server = server
    try:
        server.start()
        server.wait()
    except KeyboardInterrupt:
        LOG.info("Exciting...")


if __name__ == "__main__":
    main()
