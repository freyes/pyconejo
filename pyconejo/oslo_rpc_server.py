from __future__ import print_function
import eventlet
eventlet.monkey_patch()

import logging
import oslo_messaging
import time
from pyconejo import core
from oslo_config import cfg


LOG = logging.getLogger('pyconejo.oslo_rpc_server')


def setup_options(argv=None):
    parser = core.common_options_server(description=('RPC server using '
                                                     'oslo.messaging'))

    parser.add_argument('-t', '--topic', dest='topic', metavar='TOPIC',
                        default=core.DEFAULT_TOPIC, help='Topic')
    parser.add_argument('-s', '--server', dest='server_name', metavar='NAME',
                        default=core.DEFAULT_SERVER_NAME,
                        help=('server name to use, clients optionally can '
                              'dispatch messages directed to a specific '
                              'server'))
    return parser.parse_args(argv)


class ServerControlEndpoint(object):

    target = oslo_messaging.Target(namespace='control',
                                   version='2.0')

    def __init__(self, server):
        self.server = server
        self._counter = 0
        self.response_delay = 0
        self.num_messages = 0

    def stop(self, ctx):
        if self.server:
            self.server.stop()

    def echo(self, ctx, arg):
        self._counter += 1
        LOG.info('Received message # %s (%s): %s',
                 self._counter, str(ctx), arg)
        if self.response_delay > 0:
            LOG.debug('Delaying reply %.2f secs' % self.response_delay)
            time.sleep(self.response_delay)

        if self.num_messages > 0 and self._counter >= self.num_messages:
            LOG.debug('Reached max number of messages to reply, stopping...')
            self.stop(ctx)

        return arg


def main(argv=None):
    opts = setup_options(argv)
    core.setup_logging(level=logging.WARN if opts.quiet else logging.DEBUG)

    transport_url = core.rabbit_connection_url(driver='rabbit')
    transport = oslo_messaging.get_transport(cfg.CONF, transport_url)
    target = oslo_messaging.Target(topic=opts.topic, server=opts.server_name)
    control = ServerControlEndpoint(None)
    control.response_delay = opts.response_delay
    control.num_messages = opts.num_messages
    endpoints = [
        control,
    ]
    server = oslo_messaging.get_rpc_server(transport, target, endpoints,
                                           executor='eventlet')
    control.server = server
    control.num_messages = opts.num_messages
    t_start = time.time()

    try:
        server.start()
        server.wait()
        t_end = time.time()
    except KeyboardInterrupt:
        t_end = time.time()
        server.stop()

    print('*** Stats ***')
    msgs_per_sec = float(control._counter) / float(t_end - t_start)
    print('msgs/sec:\t%.2f' % (msgs_per_sec, ))
    print('msgs:\t%d' % control._counter)
    print('secs:\t%d' % (t_end - t_start, ))
    LOG.info("Exciting...")


if __name__ == "__main__":
    main()
