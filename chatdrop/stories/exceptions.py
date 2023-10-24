class StoryError(Exception):
    def __init__(self, message='Story Exception'):
        self.message = message
        super().__init__(self.message)