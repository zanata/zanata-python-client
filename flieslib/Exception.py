__all__ = (
        "NoSuchProjectException", "InvalidOptionException",
    )

import exceptions

class NoSuchProjectException(Exception):
	def __init__(self, expr, msg):
        	self.expr = expr
        	self.msg = msg

class InvalidOptionException(Exception):
	def __init__(self, expr, msg):
                self.expr = expr
                self.msg = msg


