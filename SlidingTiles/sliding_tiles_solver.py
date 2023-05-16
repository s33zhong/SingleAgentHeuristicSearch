from sliding_tiles import SlidingTiles


class SlidingTilesSolver:
    def __init__(self, sliding_tiles: SlidingTiles):
        self.sliding_tiles = sliding_tiles
        self.heuristic = sliding_tiles.manhattan_distance
        self.g_cost_per_move = 1

    def visualize_board(self, state=None):
        if state is None:
            for i in self.sliding_tiles.current_state:
                print(str(i) + ' ')
                if i % self.sliding_tiles.width == self.sliding_tiles.width - 1 and i != 0:
                    print()
        else:
            for i in state:
                print(str(i) + ' ')
                if i % self.sliding_tiles.width == self.sliding_tiles.width - 1 and i != 0:
                    print()
        return True

    def a_star(self, start_state=None, verbose=False):
        """
        A* algorithm that takes in a board, a heuristic, a start state, and a goal state, and returns a path from the
        start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of actions and the cost of the actions (the g-cost, as the h-cost is 0)
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        if start_state is None:
            # Initialize the start state to a random state
            start_state = self.sliding_tiles.generate_random_state()
        else:
            # Check that the start state is solvable
            if not self.sliding_tiles.is_solvable(start_state):
                raise ValueError('Invalid start state: {}'.format(start_state))
        # Initialize the current state to the start state
        self.sliding_tiles.current_state = start_state
        list_of_actions = []

        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_h_cost = self.heuristic(start_state)
        current_f_cost = current_g_cost + current_h_cost
        max_iterations = 5
        iteration = 0
        while not self.sliding_tiles.is_solved():
            if verbose:
                print('Iteration: {}, actions so far:　{}'.format(iteration, list_of_actions))
                print('Current state: {}'.format(self.sliding_tiles.current_state))
                print('Current g-cost: {}'.format(current_g_cost))
                print('Current h-cost: {}'.format(current_h_cost))
                # self.visualize_board(self.sliding_tiles.current_state)
            iteration += 1
            if iteration > max_iterations:
                raise ValueError('Max iterations reached')
            available_actions = []
            available_successors = []
            lowest_f_cost = -1
            lowest_f_cost_successor = None
            lowest_f_cost_action = None
            for action in self.sliding_tiles.actions:
                successor = self.sliding_tiles.get_successors(action)
                print("The result of the action {} is {}: ".format(action, successor))
                if successor:  # if successor is not False, which means the action is valid
                    available_actions.append(action)
                    available_successors.append(successor)
                    successor_g_cost = current_g_cost + self.g_cost_per_move
                    successor_h_cost = self.heuristic(state=successor)
                    successor_f_cost = successor_g_cost + successor_h_cost
                    if verbose:
                        print('Iteration: {}, action taken:　{}'.format(iteration, action))
                        print('Successor state: {}'.format(successor))
                        print('Successor g-cost: {}'.format(successor_g_cost))
                        print('Successor h-cost: {}'.format(successor_h_cost))
                    if lowest_f_cost == -1 or successor_f_cost < lowest_f_cost:
                        lowest_f_cost = successor_f_cost
                        lowest_f_cost_successor = successor
                        lowest_f_cost_action = action
            if lowest_f_cost_successor is None:  # all successors are False, no valid actions!
                # unintended behavior! this should never happen in a sliding tile puzzle; at least one tile is movable
                #   at any given state!
                raise ValueError('No available successor! This should not happen!')
            current_f_cost = lowest_f_cost
            list_of_actions.append(lowest_f_cost_action)
            self.sliding_tiles.current_state = lowest_f_cost_successor
        # self.visualize_board(self.sliding_tiles.current_state)
            current_g_cost += self.g_cost_per_move

        print("The puzzle is solved! The starting state is: {}".format(start_state))
        return list_of_actions, current_f_cost

    def weighted_a_star(self, start_state=None, weight=1):
        """
        Weighted A* algorithm that takes in a board, a heuristic, a start state, and a goal state, and returns a
          list of actions from the start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of (str) actions and the cost of the actions (the g-cost, as the h-cost is 0)
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        if start_state is None:
            # Initialize the start state to a random state
            start_state = self.sliding_tiles.generate_random_state()
        else:
            # Check that the start state is solvable
            if not self.sliding_tiles.is_solvable(start_state):
                raise ValueError('Invalid start state: {}'.format(start_state))
        # Initialize the current state to the start state
        self.sliding_tiles.current_state = start_state
        list_of_actions = []

        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_h_cost = weight*self.heuristic(start_state)
        current_f_cost = current_g_cost + current_h_cost

        while not self.sliding_tiles.is_solved():
            available_actions = []
            available_successors = []
            lowest_f_cost = -1  # h-cost is non-negative, and g-cost is non-negative and increasing, so this is safe
            lowest_f_cost_successor = None
            lowest_f_cost_action = None
            for action in self.sliding_tiles.actions:
                successor = self.sliding_tiles.successor(action)
                if successor:  # if successor is not False, which means the action is valid
                    available_actions.append(action)
                    available_successors.append(successor)
                    successor_g_cost = current_g_cost + self.g_cost_per_move
                    successor_h_cost = self.heuristic(state=successor)
                    successor_f_cost = successor_g_cost + weight*successor_h_cost
                    if lowest_f_cost == -1 or successor_f_cost < lowest_f_cost:
                        lowest_f_cost = successor_f_cost
                        lowest_f_cost_successor = successor
                        lowest_f_cost_action = action
            if lowest_f_cost_successor is None:  # all successors are False, no valid actions!
                # unintended behavior! this should never happen in a sliding tile puzzle; at least one tile is movable
                #   at any given state!
                raise ValueError('No available successor! This should not happen!')

            current_f_cost = lowest_f_cost
            list_of_actions.append(lowest_f_cost_action)  # add this action to the list of actions
            self.sliding_tiles.current_state = lowest_f_cost_successor  # update the current state
            current_g_cost += self.g_cost_per_move

        return list_of_actions, current_f_cost

    def budgeted_tree_search(self, start_state=None):
        """
        Budgeted tree search algorithm that takes in a board, a heuristic, a start state, and a goal state, and returns
          a list of actions from the start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of (str) actions and the cost of the actions (the g-cost, as the h-cost is 0)
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        if start_state is None:
            # Initialize the start state to a random state
            start_state = self.sliding_tiles.generate_random_state()
        else:
            # Check that the start state is solvable
            if not self.sliding_tiles.is_solvable(start_state):
                raise ValueError('Invalid start state: {}'.format(start_state))
        # Initialize the current state to the start state
        self.sliding_tiles.current_state = start_state
        list_of_actions = []

        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_h_cost = self.heuristic(start_state)
        current_f_cost = current_g_cost + current_h_cost

        while not self.sliding_tiles.is_solved():
            available_actions = []
            available_successors = []
            lowest_f_cost = -1
            lowest_f_cost_successor = None
            lowest_f_cost_action = None
            for action in self.sliding_tiles.actions:
                successor = self.sliding_tiles.successor(action)
                if successor:
                    available_actions.append(action)
                    available_successors.append(successor)
                    successor_g_cost = current_g_cost + self.g_cost_per_move
                    successor_h_cost = self.heuristic(state=successor)
                    successor_f_cost = successor_g_cost + successor_h_cost
                    if lowest_f_cost == -1 or successor_f_cost < lowest_f_cost:
                        lowest_f_cost = successor_f_cost
                        lowest_f_cost_successor = successor
                        lowest_f_cost_action = action
            if lowest_f_cost_successor is None:  # all successors are False, no valid actions!
                # unintended behavior! this should never happen in a sliding tile puzzle; at least one tile is movable
                #   at any given state!
                raise ValueError('No available successor! This should not happen!')






