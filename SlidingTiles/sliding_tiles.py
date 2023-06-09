import numpy as np
from state_space import StateSpace

# Note: in our implementation, the action are defined as which neighbour to switch with the empty tile
#   for instance, [[0, 1]  with 'down' swaps the square below 0 with 2 resulting in [[2, 1]
#                  [2, 3]]                                                           [0, 3]].
sliding_tiles_actions = {'up', 'down', 'left', 'right'}


class SlidingTiles(StateSpace):

    def __init__(self, number_of_tiles):
        # Note that number_of_tiles determines the size of the grid and the goal state
        super().__init__()
        self.number_of_tiles = number_of_tiles  # The number of tiles in the puzzle n, n = width * height = width^2
        self.width = int(np.sqrt(number_of_tiles))  # The width of the puzzle
        self.height = int(np.sqrt(number_of_tiles))  # The height of the puzzle
        self.goal = list(range(1, number_of_tiles))  # The goal state is always the sorted list: [1, ..., n-1, 0]
        self.empty_tile = 0  # Note: The empty tile is always the last tile denoted as 0
        self.goal.append(self.empty_tile)  # For the sake of clarity; we define the empty tile explicitly
        self.start = None
        self.actions = sliding_tiles_actions

    def valid_puzzle(self):
        if self.start is None:
            raise ValueError('Start state is not defined')
        return self.is_solvable(self.start)

    def is_solvable(self, state, verbose=False):
        """
        Check if the current state is solvable (depending on the number of inversions, the incorrect pairs)
        This method takes O(n^2) time, as the if statement is executed (n-1) + (n-2) + ... + 1 = n*(n-1)/2 times.
        :param state:    list, the current state
        :param verbose:  bool, if True, print when inversion is found
        :return: either: True, if the current state is solvable (# of inversions * self.width = even),
                     or: False, if # of inversions * self.width = odd
        """
        inversions = 0
        for i in range(self.number_of_tiles-1):  # ignore the last location because there are no more "pairs"
            for j in range(i+1, self.number_of_tiles):  # ignore the first i locations because they are checked
                # if the first tile is greater than the second tile, then it is an inversion; a correct order
                #  should have a smaller tile before a larger one (except for empty tile, which is always last)
                if state[i] > state[j] and state[i] != self.empty_tile and state[j] != self.empty_tile:
                    inversions += 1
                    if verbose:
                        print('Inversion found: ({} > {}), total # of inversions: {}'.format(state[i], state[j],
                                                                                             inversions))
        # if width is odd, inversions must be even for the state to be solvable
        # if width is even, inversions plus the row of the blank square must be odd for the state to be solvable
        # Therefore, the state is solvable if inversions and widths are not odd or even together
        if self.width % 2 == 1:
            return inversions % 2 == 0
        if self.width % 2 == 0:
            return (inversions + self.get_row(state, self.empty_tile)) % 2 == 1

    def get_row(self, state, tile):
        """
        Get the row number of a tile from a given state
        :param state:  list, a given state
        :param tile:   int, the tile to find the row number for
        :return:       int, the row number of the given tile (starting from row 0)
        """
        return state.index(tile) // self.width

    def generate_random_state(self):
        """
        Generate a random state for the sliding tiles puzzle; it is guaranteed that it would be solvable.
        :return: a random state for the sliding tiles puzzle
        """
        state = list(range(self.number_of_tiles))
        np.random.shuffle(state)  # shuffle method is conducted in-place
        while not self.is_solvable(state):
            np.random.shuffle(state)
        return state

    def manhattan_distance(self, state=None, state_p=None):
        """
        Calculate the Manhattan distance between the current state and the goal state (solved state), which is
          the sum of the moves each tile need to take to reach its goal position, ignoring all tiles in their way.
        This is a relaxation from the problem, and an admissible heuristic function used in the A* algorithm.
        This method takes O(n) time and O(1) space as it iterates over the entire state once.
        :param state:    the state to calculate the Manhattan distance for; if None, then the current state is used
        :param state_p:  not used; only for compatibility with the parent class
        :return:         the Manhattan distance between the current state and the goal state
        """
        distance = 0
        for i in range(self.number_of_tiles):
            if i != self.empty_tile:  # ignore the empty tile
                #  The distance is the sum of the vertical and horizontal distances
                height_difference = abs(self.goal.index(i) // self.width -
                                        state.index(i) // self.width)  # vertical dist
                width_difference = abs(self.goal.index(i) % self.width -
                                       state.index(i) % self.width)  # horizontal dist
                distance += height_difference + width_difference
        # print('Manhattan distance: {}'.format(distance))
        return distance

    @staticmethod
    def swap_neighbours(state_list, index_1, index_2):
        """
        Swap the tiles in the given indices in the given state list; this is used to generate the successor state.
        This method would require O(1) time and O(n) space where n is the number of tiles (which would be constant,
          so O(1) as well).
        :param state_list:  list, the current state denoted by a list with indices as positions and values as tiles
        :param index_1:     int, the index of the first tile to be swapped
        :param index_2:     int, the index of the second tile to be swapped
        :return:            list, the new state after swapping the tiles
        """
        temp_list = state_list.copy()
        temp_list[index_1] = state_list[index_2]
        temp_list[index_2] = state_list[index_1]
        return temp_list

    def get_successor(self, current_state, action, verbose=False):
        empty_tile_index = current_state.index(self.empty_tile)
        # print(verbose, action, current_state, empty_tile_index)
        neighbour_index = None
        if action == 'up':
            neighbour_index = empty_tile_index - self.width
        elif action == 'down':
            neighbour_index = empty_tile_index + self.width
        elif action == 'left':
            neighbour_index = empty_tile_index - 1
        elif action == 'right':
            neighbour_index = empty_tile_index + 1
        if neighbour_index is not None:
            new_state = self.swap_neighbours(current_state, empty_tile_index, neighbour_index)
            # if verbose:
            #     print('Swapping index {} with {}'.format(empty_tile_index, neighbour_index))
            #     print('Swapping {} with {}'.format(current_state[empty_tile_index],
            #                                        current_state[neighbour_index]))
            #     print('Current state:\n{}'.format(np.array(current_state).reshape(self.width, self.width)))
            #     print('New state:\n{}'.format(np.array(new_state).reshape(self.width, self.width)))
            return new_state
        else:
            return None

    def get_successors(self, current_state, last_action, verbose=False):
        """
        Get the successors of the current state by applying the given action on it.
        This method would require O(1) time and O(n) space where n is the number of tiles (which would be constant,
            so O(1) as well). In particular, the time complexity is O(1) because the number of actions is 4.
        :param current_state:  list, the current state denoted by a list with indices as positions and values as tiles
        :param last_action:    str, the last action taken to reach the current state
        :param verbose:        whether to print the action and its consequence or not
        :return:  either: list, the successor state of the current state with the given action applied on it;
                      or: False, if the given action is invalid
        """
        available_actions = self.get_available_actions(current_state, last_action)  # get all the possible successors
        successors = []
        for action in available_actions:
            # print('verbose', verbose)
            successor = self.get_successor(current_state=current_state, action=action, verbose=verbose)
            if successor is not None:
                successors.append((action, successor))
        if len(successors) == 0:
            return False
        return successors

    def get_available_actions(self, current_state, last_action=None):
        """
        Get the actions that are available to be taken from the current state.
        This method is used to generate the successors of the current state by applying all possible
          actions on it. Both the time and space complexity of this method is O(1) as there are at most
          4 actions.
        :return: a list of possible actions that can be taken from the current state
        """
        available_actions = ['up', 'down', 'left', 'right']
        if last_action == 'up':
            available_actions.remove('down')
        elif last_action == 'down':
            available_actions.remove('up')
        elif last_action == 'left':
            available_actions.remove('right')
        elif last_action == 'right':
            available_actions.remove('left')

        empty_block_index = current_state.index(0)  # see where the empty block is
        if empty_block_index % self.width == 0:  # if the empty block is on the left edge
            available_actions.remove('left')  # moving left would be impossible
        if empty_block_index % self.width == self.width - 1:  # if the empty block is not on the right edge
            available_actions.remove('right')  # moving right would be impossible
        if empty_block_index < self.width:  # if the empty block is not on the top edge
            available_actions.remove('up')  # moving up would be impossible
        if empty_block_index > self.number_of_tiles - self.width - 1:  # if the empty block is not on the bottom edge
            available_actions.remove('down')  # moving down would be impossible
        return available_actions

    def is_solved(self, state=None):
        """
        Check if a state is the goal state (solved state) if a state is not supplied, check the current state
          of the board.
        This method takes O(n) time and O(1) space where n is the number of tiles (which would be constant,
            so O(1) as well).
        :return: True if the current state is the goal state, False otherwise
        """
        # print('Checking if the current state is the goal state...')
        # print('goal: {}'.format(self.goal))
        # print('state: {}'.format(state))
        # print('is solved: {}'.format(state == self.goal))
        return state == self.goal

    @staticmethod
    def to_string(state):
        return ''.join(str(e) for e in state)

    @staticmethod
    def from_string(state_string):
        return [int(e) for e in state_string]
