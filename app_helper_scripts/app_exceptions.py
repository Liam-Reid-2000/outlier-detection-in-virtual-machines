class InvalidValueForCalculationError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        """Raised when input is less than 0"""
        return '{} contains invalid input. Metric calculations can only accept' \
                ' positive integers'.format(str(self.value))

class InvalidPercentageFloatValueError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        """Raised when input < 0 or > 1"""
        return '{} is invalid input. This value should represent a precentage' \
                ' therefore this value must be betwwen 0 and 1'.format(self.value)