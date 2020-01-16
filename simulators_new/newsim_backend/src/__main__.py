from .simHandler import runSimulator
from rover_common import aiolcm
from abc import ABC
# import math  # , abstractmethod
# import threading  # for later for perf improvements
# import time  # for later, for more accurate information and logging
import asyncio
from rover_common.aiohelper import run_coroutines
from rover_msgs import (
    AutonState, Course, GPS,
    Joystick, NavStatus, Obstacle,
    Obstacles, Odometry, Target,
    Targets, TargetList, Waypoint
)


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

        self.AutonStateMsg = AutonState()
        self.AutonStateMsg.is_auton = True

        self.CourseMsg = Course()
        self.CourseMsg.num_waypoints = 0
        self.CourseMsg.hash = 0
        self.CourseMsg.waypoints = []

        self.GPSMsg = GPS()
        self.GPSMsg.latitude_deg = 39
        self.GPSMsg.latitude_min = 0
        self.GPSMsg.longitude_deg = -110
        self.GPSMsg.longitude_min = 0
        self.GPSMsg.bearing_deg = 0
        self.GPSMsg.speed = -999  # this value is never used
        # so it's being set to a dummy value. DO NOT USE IT

        self.JoystickMsg = Joystick()
        self.JoystickMsg.forward_back = 0
        self.JoystickMsg.left_right = 0
        self.JoystickMsg.dampen = 0
        self.JoystickMsg.kill = False
        self.JoystickMsg.restart = False

        self.NavStatusMsg = NavStatus()
        self.NavStatusMsg.nav_state = 0
        self.NavStatusMsg.nav_state_name = ""
        self.NavStatusMsg.completed_wps = 0
        self.NavStatusMsg.missed_wps = 0
        self.NavStatusMsg.total_wps = 0
        self.NavStatusMsg.found_tbs = 0
        self.NavStatusMsg.total_tbs = 0

        self.ObstacleMsg = Obstacle()
        self.ObstacleMsg.detected = False
        self.ObstacleMsg.bearing = 0.0
        self.ObstacleMsg.distance = 0.0

        self.ObstaclesMsg = Obstacles()
        self.ObstaclesMsg.num_obstacles = 0
        self.ObstaclesMsg.hash = 0
        self.ObstaclesMsg.obstacles = []

        self.OdometryMsg = Odometry()
        self.OdometryMsg.latitude_deg = 0
        self.OdometryMsg.latitude_min = 0
        self.OdometryMsg.longitude_deg = 0
        self.OdometryMsg.longitude_min = 0
        self.OdometryMsg.bearing_deg = 0
        self.OdometryMsg.speed = 0

        self.TargetMsg = Target()
        self.TargetMsg.distance = 0
        self.TargetMsg.bearing = 0

        self.TargetsMsg = Targets()
        self.TargetsMsg.targets = []

        self.TargetListMsg = TargetList()
        self.TargetListMsg.targetList = [Target(), Target()]

        self.WaypointMsg = Waypoint()
        self.WaypointMsg.search = False
        self.WaypointMsg.gate = False
        self.WaypointMsg.odom = Odometry()

    # definitions for message processing are below, with callbacks (cb)
    # at the top and publishing at the bottom
    # in this setup, camelCasing denotes a class instance
    # while under_scored_variables indicate a variable within the class
    # to avoid confusion

    def autonstate_cb(self, channel, msg):
        m = AutonState.decode(msg)
        self.AutonStateMsg.is_auton = m.is_auton

    def course_cb(self, channel, msg):
        m = Course.decode(msg)
        self.CourseMsg.num_waypoints = m.num_waypoints
        self.CourseMsg.hash = m.hash
        self.CourseMsg.waypoints = m.waypoints

    def gps_cb(self, channel, msg):
        m = GPS.decode(msg)
        self.GPSMsg.latitude_deg = m.latitude_deg
        self.GPSMsg.latitude_min = m.latitude_min
        self.GPSMsg.longitude_deg = m.longitude_deg
        self.GPSMsg.longitude_min = m.longitude_min
        self.GPSMsg.bearing_deg = m.bearing_deg
        self.GPSMsg.speed = m.speed

    def joystick_cb(self, channel, msg):
        m = Joystick.decode(msg)
        self.JoystickMsg.forward_back = m.forward_back
        self.JoystickMsg.left_right = m.left_right
        self.JoystickMsg.dampen = m.dampen
        # 1-dampen/2
        self.JoystickMsg.kill = m.kill
        self.JoystickMsg.restart = m.restart

    def navstatus_cb(self, channel, msg):
        m = NavStatus.decode(msg)
        self.NavStatusMsg.nav_state = m.nav_state
        self.NavStatusMsg.nav_state_name = m.nav_state_name
        self.NavStatusMsg.completed_wps = m.completed_wps
        self.NavStatusMsg.missed_wps = m.missed_wps
        self.NavStatusMsg.total_wps = m.total_wps
        self.NavStatusMsg.found_tbs = m.found_tbs
        self.NavStatusMsg.total_tbs = m.total_tbs

    def obstacle_cb(self, channel, msg):
        m = Obstacle.decode(msg)
        self.ObstacleMsg.detected = m.detected
        self.ObstacleMsg.bearing = m.bearing
        self.ObstacleMsg.distance = m.distance

    def obstacles_cb(self, channel, msg):
        m = Obstacles.decode(msg)
        self.ObstaclesMsg.num_obstacles = m.num_obstacles
        self.ObstaclesMsg.hash = m.hash
        self.ObstaclesMsg.obstacles = m.obstacles

    def odometry_cb(self, channel, msg):
        m = Odometry.decode(msg)
        self.OdometryMsg.latitude_deg = m.latitude_deg
        self.OdometryMsg.latitude_min = m.latitude_min
        self.OdometryMsg.longitude_deg = m.longitude_deg
        self.OdometryMsg.longitude_min = m.longitude_min
        self.OdometryMsg.bearing_deg = m.bearing_deg
        self.OdometryMsg.speed = m.speed

    def target_cb(self, channel, msg):
        m = Target.decode(msg)
        self.TargetMsg.distance = m.distance
        self.TargetMsg.bearing = m.bearing

    def targets_cb(self, channel, msg):
        m = Targets.decode(msg)
        self.TargetsMsg.targets = m.targets

    def targetlist_cb(self, channel, msg):
        m = TargetList.decode(msg)
        self.TargetListMsg.targetList = m.targetList

    def waypoint_cb(self, channel, msg):
        m = Waypoint.decode(msg)
        self.WaypointMsg.search = m.search
        self.WaypointMsg.gate = m.gate
        self.WaypointMsg.odom = m.odom

    async def publish_autonstate(self, lcm):
        while True:
            lcm.publish("/autonstate", self.AutonStateMsg.encode())
            await asyncio.sleep(1)

    async def publish_course(self, lcm):
        while True:
            lcm.publish("/course", self.CourseMsg.encode())
            await asyncio.sleep(1)

    async def publish_gps(self, lcm):
        while True:
            lcm.publish("/gps", self.GPSMsg.encode())
            await asyncio.sleep(1)

    async def publish_joystick(self, lcm):
        while True:
            lcm.publish("/joystick", self.JoystickMsg.encode())
            await asyncio.sleep(1)

    async def publish_navstatus(self, lcm):
        while True:
            lcm.publish("/navstatus", self.NavStatusMsg.encode())
            await asyncio.sleep(1)

    async def publish_obstacle(self, lcm):
        while True:
            lcm.publish("/obstacle", self.ObstacleMsg.encode())
            await asyncio.sleep(1)

    async def publish_obstacles(self, lcm):
        while True:
            lcm.publish("/obstacles", self.ObstaclesMsg.encode())
            await asyncio.sleep(1)

    async def publish_odometry(self, lcm):
        while True:
            lcm.publish("/odometry", self.OdometryMsg.encode())
            await asyncio.sleep(1)

    async def publish_target(self, lcm):
        while True:
            lcm.publish("/target", self.TargetMsg.encode())
            await asyncio.sleep(1)

    async def publish_targets(self, lcm):
        while True:
            lcm.publish("/targets", self.TargetsMsg.encode())
            await asyncio.sleep(1)

    async def publish_targetlist(self, lcm):
        while True:
            lcm.publish("/targetlist", self.TargetListMsg.encode())
            await asyncio.sleep(1)

    async def publish_waypoint(self, lcm):
        while True:
            lcm.publish("/waypoint", self.WaypointMsg.encode())
            await asyncio.sleep(1)

    # callback function: takes in variable from LCM, sets values locally

    # SimObject definitions are below
    # SimObj is the abstract base class that contains properties
    # common to all objects. define additional simulator objects
    # as if you would the Rover class, including proper
    # superclass init

    # identical to the GPS message, minus speed, bc it's a useful
    # object to have internally

    class AutonState:
        def __init__(self, is_auton):
            self.is_auton = is_auton

    class Course:
        def __init__(self, num_waypoints, hash, waypoints):
            self.num_waypoints = num_waypoints
            self.hash = hash
            self.waypoints = waypoints

    class GPS:
        def __init__(self, latitude_deg, latitude_min, longitude_deg,
                     longitude_min, bearing_deg, speed):
            self.latitude_deg = latitude_deg
            self.latitude_min = latitude_min
            self.longitude_deg = longitude_deg
            self.longitude_min = longitude_min
            self.bearing_deg = bearing_deg
            self.speed = speed

    class Joystick:
        def __init__(self, forward_back, left_right, dampen,
                     kill, restart):
            self.forward_back = forward_back
            self.left_right = left_right
            self.dampen = dampen
            self.kill = kill
            self.restart = restart

    class NavStatus:
        def __init__(self, nav_state, nav_state_name, completed_wps,
                     missed_wps, total_wps, found_tbs, total_tbs):
            self.nav_state = nav_state
            self.nav_state_name = nav_state_name
            self.completed_wps = completed_wps
            self.missed_wps = missed_wps
            self.total_wps = total_wps
            self.found_tbs = found_tbs
            self.total_tbs = total_tbs

    class Obstacle:
        def __init__(self, detected, bearing, distance):
            self.detected = detected
            self.bearing = bearing
            self.distance = distance

    # keep the code, merge it to new LCM channel
    class Obstacles:
        def __init__(self, num_obstacles, hash, obstacles):
            self.num_obstacles = num_obstacles
            self.hash = hash
            self.obstacles = obstacles
            # pull exact coordinates from GPS
            self.lat_deg = GPS.latitude_deg
            self.lat_min = GPS.latitude_min
            self.lon_deg = GPS.longitude_deg
            self.lon_min = GPS.longitude_min
            self.bearing = GPS.bearing_deg

    class Odometry:
        def __init__(self, latitude_deg, latitude_min, longitude_deg,
                     longitude_min, bearing_deg, speed):
            self.latitude_deg = latitude_deg
            self.latitude_min = latitude_min
            self.longitude_deg = longitude_deg
            self.longitude_min = longitude_min
            self.bearing = bearing_deg
            self.speed = speed

    class Target:
        def __init__(self, distance, bearing):
            self.distance = distance
            self.bearing = bearing

    class Targets:
        def __init__(self, targets):
            self.targets = targets

    class TargetList:
        def __init__(self, targetList):
            self.targetList = targetList

    class Waypoint:
        def __init__(self, search, gate, odom):
            self.search = search
            self.gate = gate
            self.odom = odom

    # parent class of sim objects. Has all properties common to all
    # objects

    class SimObj(ABC):
        # define initial location and other properties
        def __init__(self, GPS):
            self.lat_deg = GPS.latitude_deg
            self.lat_min = GPS.latitude_min
            self.lon_deg = GPS.longitude_deg
            self.lon_min = GPS.longitude_min
            self.bearing = GPS.bearing_deg
            self.speed = GPS.speed  # need to create a seed system?

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
    """
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
    lcm.subscribe("/autonstate", Simulator.autonstate_cb)
    lcm.subscribe("/course", Simulator.course_cb)
    lcm.subscribe("/gps", Simulator.gps_cb)
    lcm.subscribe("/joystick", Simulator.joystick_cb)
    lcm.subscribe("/navstatus", Simulator.navstatus_cb)
    lcm.subscribe("/obstacle", Simulator.obstacle_cb)
    lcm.subscribe("/obstacles", Simulator.obstacles_cb)
    lcm.subscribe("/odometry", Simulator.odometry_cb)
    lcm.subscribe("/target", Simulator.target_cb)
    lcm.subscribe("/targetlist", Simulator.targetlist_cb)
    lcm.subscribe("/waypoint", Simulator.waypoint_cb)

    # creates loop to execute this code repeatedly with the lcm
    run_coroutines(
        lcm.loop(),
        Simulator.publish_autonstate(lcm),
        Simulator.publish_course(lcm),
        Simulator.publish_gps(lcm),
        Simulator.publish_joystick(lcm),
        Simulator.publish_navstatus(lcm),
        Simulator.publish_obstacle(lcm),
        Simulator.publish_obstacles(lcm),
        Simulator.publish_odometry(lcm),
        Simulator.publish_target(lcm),
        Simulator.publish_targets(lcm),
        Simulator.publish_targetlist(lcm),
        Simulator.publish_waypoint(lcm),
        runSimulator(Simulator)
    )

    # as a general improvement, it may be worth threading all of the
    # lcm-related bruhaha to offload the worst of the performance hits
    # as the sim becomes more complex and computationally intensive

    # time to run this mf'er
    runSimulator(Simulator)


# also necessary for the build system, idk why
if __name__ == "__main__":
    main()
