class ParsingError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        self.message = None

    def __str__(self):
        if self.message:
            return self.message
        return "Parsing error"
