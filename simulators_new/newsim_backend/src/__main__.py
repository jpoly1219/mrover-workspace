# from .simHandler import runSimulator
from rover_common import aiolcm
# from abc import ABC
# import math  # , abstractmethod
# import threading  # for later for perf improvements
# import time  # for later, for more accurate information and logging
import asyncio
from rover_common.aiohelper import run_coroutines
from rover_msgs import (
    Ping, Obstacle, TennisBall, NavStatus,
    Joystick, GPS, AutonState, Course,
    Odometry, Waypoint, Target, NewsimData
)
# import mathUtils

# 0. Grab from LCM, or whatever intermediary
# 1. Detect whether the point is within the radius "r" of the rover's view.
#   (a) Find distance between rover and point
#   (b) Compare with FOV range
# 2. Check if the point is within the FOV angle.
#   (a) Compute the range using FOV angle and the angle of the rover
#   (b) Compute the angle of the point
#   (c) Note the range is continuous,
#       but contain points greater than 360, or less than 0,
#       so need to compare the point, and the point + 360 deg
#       (TODO: Check logic)
# NOTE: Found boolean is equivalent to setting to distance to -1
# 3. Export to LCM, or whatever intermediary
#   (a) ???
# 4. PROFIT!!!

# Algorithm, LCM


class SimulatorMetaClass:

    # variables defined here are common to all classes
    # ideally it shouldn't matter bc we only ever need one instance
    # this is bad practice imho, just defined vars in the block below
    def __init__(self):  # other args if ya want em
        # all initially defined variables should be here
        # while not technically globals, this is basically where they are
        # defined for the sim, since the entire instance is the SimMetaClass

        # below: class list, one class for each message type
        # published or recieved. instantiate them at the bottom
        # of this message definition block
        # use the provided imported classes and dump these later
        # you still need to set all the defaults
        self.PingMsg = Ping()
        self.PingMsg.test = 1.0

        self.ObstacleMsg = Obstacle()
        self.ObstacleMsg.detected = 0
        self.ObstacleMsg.bearing = 0.0
        self.ObstacleMsg.distance = 0.0

        self.TennisBallMsg = TennisBall()
        self.TennisBallMsg.found = 0
        self.TennisBallMsg.bearing = 0
        self.TennisBallMsg.distance = -1

        self.NavStatusMsg = NavStatus()
        self.NavStatusMsg.nav_state = 0
        self.NavStatusMsg.completed_wps = 0
        self.NavStatusMsg.missed_wps = 0
        self.NavStatusMsg.total_wps = 0
        self.NavStatusMsg.found_tbs = 0
        self.NavStatusMsg.total_tbs = 0

        self.JoystickMsg = Joystick()
        self.JoystickMsg.forward_back = 0
        self.JoystickMsg.left_right = 0
        self.JoystickMsg.dampen = 0
        self.JoystickMsg.kill = 0
        self.JoystickMsg.restart = 0

        self.GPSMsg = GPS()
        self.GPSMsg.latitude_deg = 39
        self.GPSMsg.latitude_min = 0
        self.GPSMsg.longitude_deg = -110
        self.GPSMsg.longitude_min = 0
        self.GPSMsg.bearing_deg = 0
        self.GPSMsg.speed = -999  # this value is never used
        # so it's being set to a dummy value. DO NOT USE IT

        self.AutonStateMsg = AutonState()
        self.AutonStateMsg.is_auton = False

        self.CourseMsg = Course()
        self.CourseMsg.num_waypoints = 0
        self.CourseMsg.hash = 0
        self.CourseMsg.waypoints = []

        self.OdometryMsg = Odometry()
        self.OdometryMsg.latitude_deg = 50
        self.OdometryMsg.latitude_min = 0
        self.OdometryMsg.longitude_deg = -110
        self.OdometryMsg.longitude_min = 0
        self.OdometryMsg.bearing_deg = 0
        self.OdometryMsg.speed = -999  # this value is never used
        # so it's being set to a dummy value. DO NOT USE IT

        self.WaypointMsg = Waypoint()
        self.WaypointMsg.search = False
        self.WaypointMsg.gate = False
        self.WaypointMsg.odom = Odometry()

        self.TargetMsg = Target()
        self.TargetMsg.distance = 0
        self.TargetMsg.bearing = 0

        self.NewsimDataMsg = NewsimData()
        self.NewsimDataMsg.waypointCoord = [[]]
        self.NewsimDataMsg.tagCoord = [[]]
        self.NewsimDataMsg.gate1Coord = [[]]
        self.NewsimDataMsg.gate2Coord = [[]]
        self.NewsimDataMsg.obstacleCoord = [[]]

    # definitions for message processing are below, with callbacks (cb)
    # at the top and publishing at the bottom
    # in this setup, camelCasing denotes a class instance
    # while under_scored_variables indicate a variable within the class
    # to avoid confusion

    def ping_cb(self, channel, msg):
        m = Ping.decode(msg)
        self.PingMsg.test = m.test
        # print(m.test)

    def obstacle_cb(self, channel, msg):
        m = Obstacle.decode(msg)
        self.ObstacleMsg.detected = m.detected
        self.ObstacleMsg.bearing = m.bearing
        self.ObstacleMsg.distance = m.distance
        # print(m.bearing)

    def tennisball_cb(self, channel, msg):
        m = TennisBall.decode(msg)
        self.TennisBallMsg.found = m.found
        self.TennisBallMsg.bearing = m.bearing
        self.TennisBallMsg.distance = m.distance

    def navstatus_cb(self, channel, msg):
        m = NavStatus.decode(msg)
        self.NavStatusMsg.nav_state = m.nav_state
        self.NavStatusMsg.completed_wps = m.completed_wps
        self.NavStatusMsg.missed_wps = m.missed_wps
        self.NavStatusMsg.total_wps = m.total_wps
        self.NavStatusMsg.found_tbs = m.found_tbs
        self.NavStatusMsg.total_tbs = m.total_tbs

    def joystick_cb(self, channel, msg):
        m = Joystick.decode(msg)
        self.JoystickMsg.forward_back = m.forward_back
        self.JoystickMsg.left_right = m.left_right
        self.JoystickMsg.dampen = m.dampen
        # 1-dampen/2
        self.JoystickMsg.kill = m.kill
        self.JoystickMsg.restart = m.restart

    def gps_cb(self, channel, msg):
        m = GPS.decode(msg)
        self.GPSMsg.latitude_deg = m.latitude_deg
        self.GPSMsg.latitude_min = m.latitude_min
        self.GPSMsg.longitude_deg = m.longitude_deg
        self.GPSMsg.longitude_min = m.longitude_min
        self.GPSMsg.bearing_deg = m.bearing_deg
        self.GPSMsg.speed = m.speed

    def autonstate_cb(self, channel, msg):
        m = AutonState.decode(msg)
        self.AutonStateMsg.is_auton = m.is_auton

    def course_cb(self, channel, msg):
        m = Course.decode(msg)
        self.CourseMsg.num_waypoints = m.num_waypoints
        self.CourseMsg.hash = m.hash
        self.CourseMsg.waypoints = m.waypoints

    def odometry_cb(self, channel, msg):
        m = Odometry.decode(msg)
        self.OdometryMsg.latitude_deg = m.latitude_deg
        self.OdometryMsg.latitude_min = m.latitude_min
        self.OdometryMsg.longitude_deg = m.longitude_deg
        self.OdometryMsg.longitude_min = m.longitude_min
        self.OdometryMsg.bearing_deg = m.bearing_deg
        self.OdometryMsg.speed = m.speed

    def waypoint_cb(self, channel, msg):
        m = Waypoint.decode(msg)
        self.WaypointMsg.search = m.search
        self.WaypointMsg.gate = m.gate
        self.WaypointMsg.odom = m.odom

    def target_cb(self, channel, msg):
        m = Target.decode(msg)
        self.TargetMsg.distance = m.distance
        self.TargetMsg.bearing = m.bearing
    
    def newsimdata_cb(self, channel, msg):
        m = NewsimData.decode(msg)
        self.NewsimDataMsg.waypointCoord = m.waypointCoord
        self.NewsimDataMsg.tagCoord = m.tagCoord
        self.NewsimDataMsg.gate1Coord = m.gate1Coord
        self.NewsimDataMsg.gate2Coord = m.gate2Coord
        self.NewsimDataMsg.obstacleCoord = m.obstacleCoord

    async def publish_ping(self, lcm):
        while True:
            lcm.publish("/ping", self.PingMsg.encode())
            await asyncio.sleep(10)

    async def publish_obstacle(self, lcm):
        while True:
            lcm.publish("/obstacle", self.ObstacleMsg.encode())
            await asyncio.sleep(10)

    async def publish_tennisball(self, lcm):
        while True:
            lcm.publish("/tennisball", self.TennisBallMsg.encode())
            await asyncio.sleep(10)

    async def publish_navstatus(self, lcm):
        while True:
            lcm.publish("/navstatus", self.NavStatusMsg.encode())
            await asyncio.sleep(10)

    async def publish_joystick(self, lcm):
        while True:
            lcm.publish("/joystick", self.JoystickMsg.encode())
            await asyncio.sleep(10)

    async def publish_gps(self, lcm):
        while True:
            lcm.publish("/gps", self.GPSMsg.encode())
            await asyncio.sleep(10)

    async def publish_autonstate(self, lcm):
        while True:
            lcm.publish("/autonstate", self.AutonStateMsg.encode())
            await asyncio.sleep(10)

    async def publish_course(self, lcm):
        while True:
            lcm.publish("/course", self.CourseMsg.encode())
            await asyncio.sleep(10)

    async def publish_odometry(self, lcm):
        while True:
            lcm.publish("/odometry", self.OdometryMsg.encode())
            await asyncio.sleep(10)

    async def publish_waypoint(self, lcm):
        while True:
            lcm.publish("/waypoint", self.WaypointMsg.encode())
            await asyncio.sleep(10)

    async def publish_target(self, lcm):
        while True:
            lcm.publish("/target", self.TargetMsg.encode())
            await asyncio.sleep(10)

    async def publish_newsimdata(self, lcm):
        while True:
            lcm.publish("/newsimdata", self.NewsimDataMsg.encode())
            await asyncio.sleep(10)

    """
    def nav_test(self, channel, msg):
        pass
        # define this as per the spec

    # callback function: takes in variable from LCM, sets values locally

    # async def publish_bearing(self, lcm):
    #     while True:
    #         lcm.publish("\bearing", self.BearingMsg.encode())
    #         await asyncio.sleep(10)

    async def publish_auton_state(self, lcm):
        while True:
            lcm.publish("\auton", self.AutonStateMsg.encode())
            await asyncio.sleep(10)

    # async def publish_gps_state(self, lcm):
    #     while True:
    #         lcm.publish("\GPS", self.GPSMsg.encode())
    #         await asyncio.sleep(10)

    # bearing publish

    async def publish_GPS(self, lcm):
        while True:
            lcm.publish("\GPS", self.GPSMsg.encode())
            await asyncio.sleep(10)

    async def publish_course(self, lcm):
        while True:
            lcm.publish("\course", self.CourseMsg.encode())
            await asyncio.sleep(10)

    async def publish_obstacle(self, lcm):
        while True:
            lcm.publish("\obstacle", self.ObstacleMsg.encode())
            await asyncio.sleep(10)

    async def publish_tennisball(self, lcm):
        while True:
            lcm.publish("/tennisball", self.TennisBallMsg.encode())
            await asyncio.sleep(10)
    """
    # SimObject definitions are below
    # SimObj is the abstract base class that contains properties
    # common to all objects. define additional simulator objects
    # as if you would the Rover class, including proper
    # superclass init

    # identical to the GPS message, minus speed, bc it's a useful
    # object to have internally

    class Ping:
        def __init__(self, test):
            self.testdouble = test

    class Obstacle:
        def __init__(self, detected, bearing, distance):
            self.detectedbool = detected
            self.bearingdouble = bearing
            self.distancedouble = distance

    class TennisBall:
        def __init__(self, found, bearing, distance):
            self.foundbool = found
            self.bearingdouble = bearing
            self.distancedouble = distance

    class GPS:
        def __init__(self, latitude_deg, latitude_min, longitude_deg,
                     longitude_min, bearing_deg, speed):
            self.latitude_deg = latitude_deg
            self.latitude_min = latitude_min
            self.longitude_deg = longitude_deg
            self.longitude_deg = longitude_min
            self.bearing = bearing_deg
            self.speed = speed

    class NavStatus:
        def __init__(self, nav_state, completed_wps, missed_wps,
                     total_wps, found_tbs, total_tbs):
            self.nav_state = nav_state
            self.completed_wps = completed_wps
            self.missed_wps = missed_wps
            self.total_wps = total_wps
            self.found_tbs = found_tbs
            self.total_tbs = total_tbs

    class Joystick:
        def __init__(self, forward_back, left_right, dampen,
                     kill, restart):
            self.forward_back = forward_back
            self.left_right = left_right
            self.dampen = dampen
            self.kill = kill
            self.restart = restart

    class AutonState:
        def __init__(self, is_auton):
            self.is_auton = is_auton

    class Course:
        def __init__(self, num_waypoints, hash, waypoints):
            self.num_waypoints = num_waypoints
            self.hash = hash
            self.waypoints = waypoints

    class Odometry:
        def __init__(self, latitude_deg, latitude_min, longitude_deg,
                     longitude_min, bearing_deg, speed):
            self.latitude_deg = latitude_deg
            self.latitude_min = latitude_min
            self.longitude_deg = longitude_deg
            self.longitude_min = longitude_min
            self.bearing = bearing_deg
            self.speed = speed

    class Waypoint:
        def __init__(self, search, gate, odom):
            self.search = search
            self.gate = gate
            self.odom = odom

    class Target:
        def __init__(self, distance, bearing):
            self.distance = distance
            self.bearing = bearing
    
    class NewsimData:
        def __init__(self, waypointCoord, tagCoord, gate1Coord, gate2Coord, obstacleCoord):
            self.waypointCoord = waypointCoord
            self.tagCoord = tagCoord
            self.gate1Coord = gate1Coord
            self.gate2Coord = gate2Coord
            self.obstacleCoord = obstacleCoord

    # parent class of sim objects. Has all properties common to all
    # objects
    """
    class SimObj(ABC):
        # define initial location and other properties
        def __init__(self, GPS):
            self.lat_deg = GPS.latitude_deg
            self.lat_min = GPS.latitude_min
            self.lon_deg = GPS.longitude_deg
            self.lon_min = GPS.longitude_min
            self.bearing = GPS.bearing_deg
            self.shape = 0  # need to create a seed system?

        # any methods common to all classes should be defined
        def get_coords(self):
            return [self.lat_deg, self.lat_min,
                    self.lon_deg, self.lon_min]

        def get_bearing(self):
            return self.bearing

        # here is an abstract method, may be useful
        # @abstractmethod
        # def sample_abs_method(self):
        #     pass
    class Field(SimObj):
        def __init__(self, GPS, radius=2):  # other properties
            super().__init__(GPS)
            self.radius = radius  # in degrees, if not specified
            # radius is 2

    class Rover(SimObj):
        def __init__(self, GPS, speed_trans=1,
                     speed_rot=1):
            super().__init__(GPS)
            self.fov = 120  # units of degrees,
            # 120 if not specified
            self.cv_thresh = 5
            self.speed_translational = speed_trans
            # speed multiplier, 1 if not specified
            self.speed_rotational = speed_rot

    class TennisBall(SimObj):
        def __init__(self, GPS):  # other properties
            super().__init__(GPS)
            self.other_prop = 0

    class Obstacle(SimObj):
        def __init__(self, GPS):  # other properties
            super().__init__(GPS)

    class Waypoint(SimObj):
        def __init__(self, GPS, searchable=0):
            super().__init__(GPS)
            self.search = searchable  # defaults to false if not set
    """


def main():
    # how you get lcm messages
    lcm = aiolcm.AsyncLCM()

    # instantiates Simulator class
    Simulator = SimulatorMetaClass()

    # constantly queries lcm server
    lcm.subscribe("/ping", Simulator.ping_cb)
    lcm.subscribe("/obstacle", Simulator.obstacle_cb)
    lcm.subscribe("/tennisball", Simulator.tennisball_cb)
    lcm.subscribe("/navstatus", Simulator.navstatus_cb)
    lcm.subscribe("/joystick", Simulator.joystick_cb)
    lcm.subscribe("/gps", Simulator.gps_cb)
    lcm.subscribe("/autonstate", Simulator.autonstate_cb)
    lcm.subscribe("/course", Simulator.course_cb)
    lcm.subscribe("/odometry", Simulator.odometry_cb)
    lcm.subscribe("/waypoint", Simulator.waypoint_cb)
    lcm.subscribe("/target", Simulator.target_cb)
    lcm.subscribe("/newsimdata", Simulator.newsimdata_cb)
    # lcm.subscribe("\nav_state", Simulator.nav_state_cb)
    # lcm.subscribe("\drive_control", Simulator.joystick_cb)

    # creates loop to execute this code repeatedly with the lcm
    run_coroutines(
        lcm.loop(),
        Simulator.publish_ping(lcm),
        Simulator.publish_obstacle(lcm),
        Simulator.publish_tennisball(lcm),
        Simulator.publish_navstatus(lcm),
        Simulator.publish_joystick(lcm),
        Simulator.publish_gps(lcm),
        Simulator.publish_autonstate(lcm),
        Simulator.publish_course(lcm),
        Simulator.publish_odometry(lcm),
        Simulator.publish_waypoint(lcm),
        Simulator.publish_target(lcm),
        Simulator.publish_newsimdata(lcm)
        # runSimulator(Simulator)
    )

    # as a general improvement, it may be worth threading all of the
    # lcm-related bruhaha to offload the worst of the performance hits
    # as the sim becomes more complex and computationally intensive

    # time to run this mf'er
    # runSimulator(Simulator)


# also necessary for the build system, idk why
if __name__ == "__main__":
    main()
