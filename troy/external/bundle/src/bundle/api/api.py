class BundleError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class ComputeBundle:
    def __init__(self):
        raise  NotImplementedError("Abstract super class, please use ComputeBundle implementation class in bundle namespace")
