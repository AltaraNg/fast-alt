class InvalidDataframeType(ValueError):

    def __init__(self):
        self.message = 'Invalid dataframe input supplied, make sure your input is a valid pandas.DataFrame'

    def __str__(self):
        return self.message
