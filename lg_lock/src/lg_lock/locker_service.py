from lg_lock.msg import State

class LockerService(object):
    """
    Lock/Unlock LG

    param password - password to unlock LG
    param state - Bool initial state
    """
    def __init__(self, statePublisher, password, state):
        self.password = password
        self.state = state
        self.publisher = statePublisher
        self.publishState()

    def lock(self, msg):
        self._lock()
        return self.state

    def unlock(self, msg):
        if (self.password == msg.password):
            self._unlock()
        return self.state

    def get_state(self, msg):
        return self.state

    def _unlock(self):
        self.state = False
        self.publishState()
    
    def _lock(self):
        self.state = True   
        self.publishState()

    def publishState(self):
        self.publisher.publish(State(self.state))