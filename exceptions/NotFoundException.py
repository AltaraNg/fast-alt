class NotFoundException(Exception):
    def __init__(self, message: str = "Item not found"):
        self.message = message
