from rover_common import aiolcm
import asyncio
from rover_common.aiohelper import run_coroutines
from rover_msgs import GPS

# publish messages

msg = GPS()
msg.latitude_deg = 0
msg.latitude_min = 1.0
msg.longitude_deg = 2
msg.longitude_min = 3.0
msg.bearing_deg = 4.0
msg.speed = 5.0

lcm.publish()

# receive messages