class StateSpace:

    def __init__(self):
        self.successor = None
        self.actions = None
        self.heuristic = None

    def handle(self, action, state, **kwargs):
        try:
            if self.successor is not None:
                return self.successor(action, state, **kwargs)
        except AttributeError:
            raise NotImplementedError('Must provide a handle method')
        else:
            return True

    def set_successor(self, successor):
        self.successor = successor
        return True

    def set_actions(self, actions):
        self.actions = actions
        return True

    def set_heuristic(self, heuristic):
        self.heuristic = heuristic
        return True

    def get_successor(self):
        return self.successor

    def get_actions(self):
        return self.actions

    def get_heuristic(self):
        return self.heuristic

    def out_of_state_space(self, state):
        pass

    def get_successors(self, **kwargs):
        pass
