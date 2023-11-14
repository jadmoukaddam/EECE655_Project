import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
import socket
import aiocoap


# receiver will open threads to listen to both protocols at the same time