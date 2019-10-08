#!/usr/bin/env python

"""Image Checker

   Cross references the current image_viewer procs with the
   image assets in the last /director/scene msg.  If there are lingering procs
   kill it with fire
"""

import json
import rospy
import subprocess
from lg_common.srv import USCSMessage
from interactivespaces_msgs.msg import GenericMessage
from copy import copy

PGREP_CMD = ['pgrep', '-a', 'feh']
EGREP_CMD = ['egrep', '-o', 'http?://[^ ]+']
PARTIAL_KILLER_CMD = ['pkill', '-9', '-f']
IMAGE_PROCS_TO_KILL = ['image_viewer.py', 'feh', 'pqiv']
LOOP_TIMEOUT = 5


class ImageChecker():
    def __init__(self, last_uscs_message):
        self.last_uscs_message = last_uscs_message

    def handle_director(self, data):
        rospy.logerr('handle_director')
        assets_to_remove = []
        new_image_windows = []
        message = json.loads(data.message)
        rospy.sleep(2)
        for window in message.get('windows', []):
            if window.get('activity', '') == 'image':
                new_image_windows.append(window['assets'][0])

        feh_assets = self._get_feh_assets()
        for feh_asset in feh_assets:
            if feh_asset not in new_image_windows:
                assets_to_remove.append(feh_asset)
        if assets_to_remove:
            rospy.logerr('ASSETS TO REMOVE')
            if json.loads(self.last_uscs_message().message) == message:
                for image_proc in IMAGE_PROCS_TO_KILL:
                    subprocess.call(PARTIAL_KILLER_CMD + [image_proc])

    def _get_feh_assets(self):
        feh_assets = []
        pgrep = subprocess.Popen(PGREP_CMD, stdout=subprocess.PIPE)
        feh_proc = subprocess.Popen(
            EGREP_CMD,
            stdin=pgrep.stdout,
            stdout=subprocess.PIPE
        )
        feh_proc_assets = feh_proc.communicate()
        if feh_proc_assets[0]:
            feh_assets = feh_proc_assets[0].strip().split('\n')
        return feh_assets


def main():
    rospy.init_node('image_checker')
    rospy.wait_for_service('/uscs/message', 10)
    last_uscs_message = rospy.ServiceProxy('/uscs/message', USCSMessage)
    checker = ImageChecker(last_uscs_message)
    rospy.Subscriber('/director/scene', GenericMessage, checker.handle_director)
    rospy.spin()

if __name__ == '__main__':
    main()
