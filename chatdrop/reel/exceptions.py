class ReelError(Exception):
    def __init__(self, message='Reel Exception'):
        self.message = message
        super().__init__(self.message)

class CommentError(Exception):
    def __init__(self, message='Comment Exception'):
        self.message = message
        super().__init__(self.message)

class LikeError(Exception):
    def __init__(self, message='Like Exception'):
        self.message = message
        super().__init__(self.message)

class AudioError(Exception):
    def __init__(self, message='Audio Exception'):
        self.message = message
        super().__init__(self.message)