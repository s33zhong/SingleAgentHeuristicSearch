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
        self.current_state = None
        self.goal = list(range(1, number_of_tiles))  # The goal state is always the sorted list: [1, ..., n-1, 0]
        self.empty_tile = 0  # Note: The empty tile is always the last tile denoted as 0
        self.goal.append(self.empty_tile)  # For the sake of clarity; we define the empty tile explicitly
        self.start = None
        self.actions = sliding_tiles_actions

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

    def manhattan_distance(self, state=None):
        """
        Calculate the Manhattan distance between the current state and the goal state (solved state), which is
          the sum of the moves each tile need to take to reach its goal position, ignoring all tiles in their way.
        This is a relaxation from the problem, and an admissible heuristic function used in the A* algorithm.
        This method takes O(n) time and O(1) space as it iterates over the entire state once.
        :param state: the state to calculate the Manhattan distance for; if None, then the current state is used
        :return:      the Manhattan distance between the current state and the goal state
        """
        distance = 0
        if state is None:
            for i in range(self.number_of_tiles):
                if i != self.empty_tile:  # ignore the empty tile
                    #  The distance is the sum of the vertical and horizontal distances
                    height_difference = abs(self.goal.index(i) // self.width -
                                            self.current_state.index(i) // self.width)  # vertical dist
                    width_difference = abs(self.goal.index(i) % self.width -
                                           self.current_state.index(i) % self.width)  # horizontal dist
                    distance += height_difference + width_difference
        else:
            for i in range(self.number_of_tiles):
                if i != self.empty_tile:  # ignore the empty tile
                    #  The distance is the sum of the vertical and horizontal distances
                    height_difference = abs(self.goal.index(i) // self.width -
                                            state.index(i) // self.width)  # vertical dist
                    width_difference = abs(self.goal.index(i) % self.width -
                                           state.index(i) % self.width)  # horizontal dist
                    distance += height_difference + width_difference
        return distance

    def get_available_successors(self):
        """
        Get the neighbours (indices) of the empty block (0) in the current state. Then, we get to see
          which tiles can be moved (they are the successors).
        This method is used to generate the successors of the current state by applying all possible
          actions on it. Both the time and space complexity of this method is O(1) as there are at most
          4 actions.
        :return: a dict of neighbours (indices) that is available to be moved as values and the
                 possible actions that can be taken as keys.
        """
        available_neighbours = dict()
        empty_block_index = self.current_state.index(0)  # see where the empty block is
        if empty_block_index % self.width != 0:  # if the empty block is not on the left edge
            available_neighbours['left'] = empty_block_index - 1  # add the left tile to the neighbours
        if empty_block_index % self.width != self.width - 1:  # if the empty block is not on the right edge
            available_neighbours['right'] = empty_block_index + 1  # add the right tile to the neighbours
        if empty_block_index > self.width:  # if the empty block is not on the top edge
            available_neighbours['up'] = empty_block_index - self.width  # add the top tile to the neighbours
        if empty_block_index < self.number_of_tiles - self.width:  # if the empty block is not on the bottom edge
            available_neighbours['down'] = empty_block_index + self.width  # add the bottom tile to the neighbours
        return available_neighbours

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

    def get_successors(self, action, verbose=False):
        """
        Get the successors of the current state by applying the given action on it.
        This method would require O(1) time and O(n) space where n is the number of tiles (which would be constant,
            so O(1) as well). In particular, the time complexity is O(1) because the number of actions is 4.
        :param verbose:   whether to print the action and its consequence or not
        :param action:    str, the action to be applied on the current state, one of ['up', 'down', 'left', 'right']
        :return:  either: list, the successor state of the current state with the given action applied on it;
                      or: False, if the given action is invalid
        """
        available_successors = self.get_available_successors()  # get all the possible successors given all actions
        if action not in available_successors.keys():
            Warning('Invalid action')
            return False
        else:
            neighbour_index = available_successors[action]  # get the index of the neighbour to be swapped
            empty_index = self.current_state.index(0)  # get the index of the empty block
            if verbose:
                print('Swapping index {} with {}'.format(empty_index, neighbour_index))
                print('Swapping {} with {}'.format(self.current_state[empty_index], self.current_state[neighbour_index]))
                print('Current state: {}'.format(np.array(self.current_state).reshape(self.width, self.width)))
            successor = self.swap_neighbours(self.current_state, neighbour_index, empty_index)  # swap the tiles
            if verbose:
                print('Successor state: {}'.format(np.array(successor).reshape(self.width, self.width)))
            return successor

    def is_solved(self, state=None):
        """
        Check if a state is the goal state (solved state) if a state is not supplied, check the current state
          of the board.
        This method takes O(n) time and O(1) space where n is the number of tiles (which would be constant,
            so O(1) as well).
        :return: True if the current state is the goal state, False otherwise
        """
        if state is None:
            return self.current_state == self.goal
        else:
            return state == self.goal
