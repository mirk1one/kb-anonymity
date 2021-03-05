class ArgumentError(Exception):
    """
    Exception raised for errors in the input arguments.
    """

    def __init__(self, argument, value, argument2=None, value2=None, message="Argument Exception error"):
        self.argument = argument
        self.value = value
        self.argument2 = argument2
        self.value2 = value2
        self.message = message
        if argument2 is None and value2 is None:
            super().__init__(self.message, self.argument, self.value)
        else:
            super().__init__(self.message, self.argument, self.value, self.argument2, self.value2)
