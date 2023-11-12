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


logging.basicConfig(level=logging.ERROR)
Times = [0]
Threads=[]
async def sendmsg(index):
	i=0
	total=0
	protocol = await Context.create_client_context()
	request = Message(code=GET, uri='coap://192.168.0.140/time')
	while(i<100):
		start = time.time()
#		try:
		response = await asyncio.wait_for(protocol.request(request).response, timeout=1)
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
