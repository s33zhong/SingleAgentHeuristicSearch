
class Heuristic:
    def __init__(self, heuristic=None):
        self._heuristic = heuristic

    def handle(self, state):
        try:
            result = self._heuristic.handle(state)
        except AttributeError:
            raise NotImplementedError('Must provide a heuristic (call set_heuristic)')
        else:
            return result

    def set_heuristic(self, heuristic):
        self._heuristic = heuristic
        return True
