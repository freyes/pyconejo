# pyconejo

[![Build Status](https://travis-ci.org/freyes/pyconejo.svg?branch=master)](https://travis-ci.org/freyes/pyconejo)

A simple tool to stress a [RabbitMQ](http://www.rabbitmq.com/) service. It
provides different commands depening on the pattern you want to use, for the
moment publisher/consumer and RPC (an echo function) are supported, I hope to
add more in the future.

## Install

### From github

```
pip install git+https://github.com/freyes/pyconejo.git#egg=pyconejo
```

## Usage

### Connection

By default pyconejo uses `amqp://guest:guest@localhost:5672/%2F`, each
parameter can be overriden by an environment variable:

* `PYCONEJO_USERNAME`
* `PYCONEJO_PASSWORD`
* `PYCONEJO_HOST`
* `PYCONEJO_PORT`
* `PYCONEJO_VHOST`

### Publisher/Consumer

* Start the server running `pyconejo-consumer`
* Start the client running `pyconejo-publisher`
* And that's it

By default this will just push one message every second, not very ideal if you
want to stress it, so the publisher has a few flags to increase the throughput

* `-c` increases the number of concurrent processes that will push messages into the queue
* `-i` reduces the interval at which each messages is pushed

So using `pyconejo-publisher -c 20 -i 0.01` the program will push ~2000 msgs/sec


### RPC

* Start the server running `pyconejo-rpc-server`
* Start the client running `pyconejo-rpc-client`

By default this will make a 1 call every second, to increase the throughput
adjust `-c` , the have the same meaning as in `pyconejo-publisher`. So using
`pyconejo-rpc-client -c 20` the have 20 concurrent processes pushing messages.
