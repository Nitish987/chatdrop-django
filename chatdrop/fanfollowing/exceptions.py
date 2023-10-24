class FollowError(Exception):
    def __init__(self, message='Follow Exception'):
        self.message = message
        super().__init__(self.message)