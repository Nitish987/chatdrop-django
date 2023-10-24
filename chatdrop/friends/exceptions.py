class FriendError(Exception):
    def __init__(self, message='Friend Exception'):
        self.message = message
        super().__init__(self.message)