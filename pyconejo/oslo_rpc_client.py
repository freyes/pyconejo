import logging
import oslo_messaging as messaging
import sys
import time
import uuid
from oslo_config import cfg
from pyconejo import core


LOG = logging.getLogger('pyconejo.oslo_rpc_client')


def setup_options(argv=None):
    parser = core.common_options_client()

    parser.add_argument('--reuse-transport', action='store_true',
                        dest='reuse_transport',
                        help='Reuse the transport for each call, this makes '
                             'use of the same reply_* queue all the time')
    parser.add_argument('--do-not-cleanup', action='store_false',
                        dest='transport_cleanup',
                        help='Do not release the resources associated with '
                             'the transport')
    parser.add_argument('--renew-transport-after', type=int,
                        dest='renew_transport')

    return parser.parse_args(argv)


class TestClient(object):

    def __init__(self, transport):
        target = messaging.Target(topic=core.DEFAULT_TOPIC,
                                  namespace='control', version='2.0')
        self._client = messaging.RPCClient(transport, target)

    def echo(self, ctxt, arg):
        return self._client.call(ctxt, 'echo', arg=arg)


def main(argv=None):
    opts = setup_options(argv)
    core.setup_logging(level=logging.WARN if opts.quiet else logging.DEBUG)

    if core.forkme_and_wait(opts.processes):
        # I'm the father and I'm done
        sys.exit(0)

    transport_url = core.rabbit_connection_url(driver='rabbit')
    transport = messaging.get_transport(cfg.CONF, transport_url)
    t = TestClient(transport)
    ctxt = {'a': 1}
    i = 0
    errors = 0
    try:
        while opts.num_messages == 0 or i < opts.num_messages:
            arg = opts.message + str(uuid.uuid4())
            LOG.debug("Requesting echo(%s)" % arg)
            try:
                response = t.echo(ctxt, arg)
                LOG.info("Got %r" % (response,))
                assert arg == response, "%s != %s" % (arg, response)
                i += 1
            except messaging.exceptions.MessagingTimeout as ex:
                LOG.warn('Received MessagingTimeout exception: %s' % str(ex))
                errors += 1

            if opts.publish_interval > 0:
                time.sleep(opts.publish_interval)

            if not opts.reuse_transport:
                renew = True
                if opts.renew_transport > 0 and i % opts.renew_transport != 0:
                    renew = False

                if renew:
                    if opts.transport_cleanup:
                        # removes the reply_* queue associated with this transport
                        t._client.transport.cleanup()

                    transport = messaging.get_transport(cfg.CONF, transport_url)
                    t = TestClient(transport)

    except KeyboardInterrupt:
        # TODO: clean connections and asdf
        sys.exit(0)


if __name__ == "__main__":
    main()
