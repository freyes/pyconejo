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

    return parser.parse_args(argv)


class TestClient(object):

    def __init__(self, transport):
        target = messaging.Target(topic='test', namespace='control',
                                  version='2.0')
        self._client = messaging.RPCClient(transport, target)

    def test(self, ctxt, arg):
        return self._client.call(ctxt, 'test', arg=arg)


def main(argv=None):
    opts = setup_options(argv)
    core.setup_logging(level=logging.WARN if opts.quiet else logging.DEBUG)
    if core.forkme_and_wait(opts.processes):
        # I'm the father and I'm done
        sys.exit(0)

    transport = messaging.get_transport(cfg.CONF)
    t = TestClient(transport)
    ctxt = {'a': 1}
    i = 0
    try:
        while opts.num_messages == 0 or i < opts.num_messages:
            arg = str(uuid.uuid4())
            LOG.debug("Requesting echo(%s)" % arg)
            response = t.test(ctxt, arg)
            LOG.info("Got %r" % (response,))
            assert arg == response, "%s != %s" % (arg, response)
            i += 1
            time.sleep(opts.publish_interval)
    except KeyboardInterrupt:
        # TODO: clean connections and asdf
        sys.exit(0)


if __name__ == "__main__":
    main()
