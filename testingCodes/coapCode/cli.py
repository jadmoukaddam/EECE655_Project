#!/usr/bin/env python3

# SPDX-FileCopyrightText: Christian AmsÃ¼ss and the aiocoap contributors
#
# SPDX-License-Identifier: MIT

"""This is a usage example of aiocoap that demonstrates how to implement a
simple client. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import logging
import asyncio
import threading
import time
from aiocoap import *
class TransportTuning2(TransportTuning):
    """Base parameters that guide CoAP transport behaviors

    The values in here are recommended values, often defaults from RFCs. They
    can be tuned in subclasses (and then passed into a message as
    ``transport_tuning``), although users should be aware that alteing some of
    these can cause the library to behave in ways violating the specification,
    especially with respect to congestion control.
    """

    #   +-------------------+---------------+
    #   | name              | default value |
    #   +-------------------+---------------+
    #   | ACK_TIMEOUT       | 2 seconds     |
    #   | ACK_RANDOM_FACTOR | 1.5           |
    #   | MAX_RETRANSMIT    | 4             |
    #   | NSTART            | 1             |
    #   | DEFAULT_LEISURE   | 5 seconds     |
    #   | PROBING_RATE      | 1 Byte/second |
    #   +-------------------+---------------+

    ACK_TIMEOUT = 2.0
    """The time, in seconds, to wait for an acknowledgement of a
    confirmable message. The inter-transmission time doubles
    for each retransmission."""

    ACK_RANDOM_FACTOR = 1.5
    """Timeout multiplier for anti-synchronization."""

    MAX_RETRANSMIT = 100
    """The number of retransmissions of confirmable messages to
    non-multicast endpoints before the infrastructure assumes no
    acknowledgement will be received."""

    NSTART = 1
    """Maximum number of simultaneous outstanding interactions
       that endpoint maintains to a given server (including proxies)"""

    #   +-------------------+---------------+
    #   | name              | default value |
    #   +-------------------+---------------+
    #   | MAX_TRANSMIT_SPAN |          45 s |
    #   | MAX_TRANSMIT_WAIT |          93 s |
    #   | MAX_LATENCY       |         100 s |
    #   | PROCESSING_DELAY  |           2 s |
    #   | MAX_RTT           |         202 s |
    #   | EXCHANGE_LIFETIME |         247 s |
    #   | NON_LIFETIME      |         145 s |
    #   +-------------------+---------------+

    @property
    def MAX_TRANSMIT_SPAN(self):
        """Maximum time from the first transmission
        of a confirmable message to its last retransmission."""
        return self.ACK_TIMEOUT * (2 ** self.MAX_RETRANSMIT - 1) * self.ACK_RANDOM_FACTOR

    @property
    def MAX_TRANSMIT_WAIT(self):
        """Maximum time from the first transmission
        of a confirmable message to the time when the sender gives up on
        receiving an acknowledgement or reset."""
        return self.ACK_TIMEOUT * (2 ** (self.MAX_RETRANSMIT + 1) - 1) * self.ACK_RANDOM_FACTOR

    MAX_LATENCY = 100.0
    """Maximum time a datagram is expected to take from the start
    of its transmission to the completion of its reception."""

    @property
    def PROCESSING_DELAY(self):
        """"Time a node takes to turn around a
        confirmable message into an acknowledgement."""
        return self.ACK_TIMEOUT

    @property
    def MAX_RTT(self):
        """Maximum round-trip time."""
        return 2 * self.MAX_LATENCY + self.PROCESSING_DELAY

    @property
    def EXCHANGE_LIFETIME(self):
        """time from starting to send a confirmable message to the time when an
        acknowledgement is no longer expected, i.e. message layer information about the
        message exchange can be purged"""
        return self.MAX_TRANSMIT_SPAN + self.MAX_RTT

    DEFAULT_BLOCK_SIZE_EXP = MAX_REGULAR_BLOCK_SIZE_EXP
    """Default size exponent for blockwise transfers."""

    EMPTY_ACK_DELAY = 0.1
    """After this time protocol sends empty ACK, and separate response"""

    REQUEST_TIMEOUT = MAX_TRANSMIT_WAIT
    """Time after which server assumes it won't receive any answer.
       It is not defined by IETF documents.
       For human-operated devices it might be preferable to set some small value
       (for example 10 seconds)
       For M2M it's application dependent."""

    DEFAULT_LEISURE = 5

    @property
    def MULTICAST_REQUEST_TIMEOUT(self):
        return self.REQUEST_TIMEOUT + self.DEFAULT_LEISURE

    OBSERVATION_RESET_TIME = 128
    """Time in seconds after which the value of the observe field are ignored.

    This number is not explicitly named in RFC7641.
    """

logging.basicConfig(level=logging.ERROR)
Times = [0]
Threads=[]
async def sendmsg(index):
	i=0
	total=0
	protocol = await Context.create_client_context()
	request = Message(code=GET, uri='coap://192.168.1.11/time', transport_tuning=TransportTuning2)
	while(i<100):
		start = time.time()
#		try:
		response = await asyncio.wait_for(protocol.request(request).response,timeout=200)
#		except:
#			protocol = await Context.create_client_context()
#			continue
		end = time.time()
		total += end-start
		i+=1
	Times[index]=total


async def main():
    try:
        for i in range(1):
                coroutines = [sendmsg(0)]
                # Use asyncio.gather() to execute the coroutines concurrently
                await asyncio.gather(*coroutines)
                
        
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: '+str(sum(Times)/100))

if __name__ == "__main__":
    asyncio.run(main())
