class Tristate(object):

    def __init__(self, value=None):
       if any(value is v for v in (True, False, None)):
          self.value = value
       else:
           raise ValueError("Tristate value must be True, False, or None")

    def __eq__(self, other):
       return (self.value is other.value if isinstance(other, Tristate)
               else self.value is other)

    def __ne__(self, other):
       return not self == other

    def __nonzero__(self):   # Python 3: __bool__()
       raise TypeError("Tristate object may not be used as a Boolean")

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Tristate(%s)" % self.value
