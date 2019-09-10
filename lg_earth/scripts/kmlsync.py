#!/usr/bin/env python3

import rospy
import tornado.web
import tornado.ioloop
from lg_earth import KmlMasterHandler, KmlUpdateHandler, KmlQueryHandler
from lg_earth.srv import KmlState, PlaytourQuery, PlanetQuery
from lg_common.webapp import ros_tornado_spin
from interactivespaces_msgs.msg import GenericMessage
from std_msgs.msg import String
from lg_common.helpers import run_with_influx_exception_handler


NODE_NAME = 'kmlsync_http_server'


class PlanetWatcher:
    def __init__(self, topic):
        rospy.Subscriber(topic, String, self.record_planet)
        self.current_planet = None

    def record_planet(self, data):
        if data.data == '':
            data.data = 'earth'
        self.current_planet = data.data

    def get_planet(self):
        return self.current_planet


def main():
    rospy.init_node(NODE_NAME)
    port = rospy.get_param('~port', 8765)
    current_planet = None

    req_timeout_probe = float(rospy.get_param('~request_timeout'))
    if req_timeout_probe is not None:
        rospy.logwarn('request_timeout parameter is not active (value is zero, no polling)')
    KmlUpdateHandler.timeout = 0

    kmlsync_server = tornado.web.Application([
        (r'/master.kml', KmlMasterHandler),
        (r'/network_link_update.kml', KmlUpdateHandler),
        (r'/query.html', KmlQueryHandler),
    ], debug=True)

    global_dependency_timeout = int(rospy.get_param('~global_dependency_timeout', 15))
    rospy.wait_for_service('/kmlsync/state', global_dependency_timeout)
    rospy.wait_for_service('/kmlsync/playtour_query', global_dependency_timeout)
    rospy.wait_for_service('/kmlsync/planet_query', global_dependency_timeout)

    director_scene_topic = rospy.get_param('~director_topic', '/director/scene')
    rospy.Subscriber(director_scene_topic, GenericMessage, KmlUpdateHandler.get_scene_msg)
    planet_announce_topic = rospy.get_param('~planet_announce_topic', '/earth/planet')
    pw = PlanetWatcher(planet_announce_topic)

    kml_state = KmlState()
    kmlsync_server.playtour = PlaytourQuery()
    kmlsync_server.asset_service = rospy.ServiceProxy('/kmlsync/state', kml_state, persistent=True)
    kmlsync_server.playtour_service = rospy.ServiceProxy('/kmlsync/playtour_query', kmlsync_server.playtour, persistent=True)
    kmlsync_server.planet = PlanetQuery()
    kmlsync_server.planet_service = rospy.ServiceProxy('/kmlsync/planet_query', kmlsync_server.planet, persistent=True)
    kmlsync_server.get_planet = pw.get_planet
    kmlsync_server.listen(port)
    ros_tornado_spin()


if __name__ == '__main__':
    run_with_influx_exception_handler(main, NODE_NAME)
