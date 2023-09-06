class InvalidSalaryRange(Exception):

    def __init__(self):
        self.message = 'The provided salary range is invalid, maximum salary must be greater minimum salary'

    def __str__(self):
        return self.message
