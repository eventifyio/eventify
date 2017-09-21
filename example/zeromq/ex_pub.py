from __future__ import print_function

import time
from random import choice
from random import randrange

import zmq

if __name__ == "__main__":
    stock_symbols = ['RAX', 'EMC', 'GOOG', 'AAPL', 'RHAT', 'AMZN']

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://127.0.0.1:5570")

    while True:
        time.sleep(3)
        # pick a random stock symbol
        stock_symbol = choice(stock_symbols)
        # set a random stock price
        stock_price = randrange(1, 100)

        # compose the message
        msg = "{0} ${1}".format(stock_symbol, stock_price)

        print("Sending Message: {0}".format(msg))

        # send the message
        socket.send(['gce-vm', msg])
