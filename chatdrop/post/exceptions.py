class PostError(Exception):
    def __init__(self, message='Post Exception'):
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