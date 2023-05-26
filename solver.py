from Grid.grid import Grid
import heapq
from queue import PriorityQueue


class Solver:
    def __init__(self, heuristic, puzzle):
        self.heuristic = heuristic
        self.puzzle = puzzle

    def update_open_list(self, open_list, f_cost, g_cost, parent, state, contains_g_cost=True):
        """
        Update the f_cost of a state in the open list
        :param f_cost:          float, f-cost of the state
        :param g_cost:          float, g-cost of the state
        :param contains_g_cost: bool, whether the f-cost contains g-cost
        :param open_list:       list, a heapq-based priority queue
        :param parent:          tuple, parent of the state
        :param state:           tuple, a state (location) on the grid
        :return:
        """
        # Find the index of the state in the open list
        index = self.index_in_open_list(state, open_list)
        if index == -1:
            raise ValueError('State {} not in open list'.format(state))
        else:
            if contains_g_cost:
                # Update the f_cost, g_cost of the state
                open_list[index] = (f_cost, g_cost, parent, state)
            else:
                # Update the f_cost of the state
                open_list[index] = (f_cost, parent, state)

    @staticmethod
    def index_in_open_list(state, open_list):
        """
        Check if a state is in the open list, a heapq-based priority queue.
        This method is very slow unfortunately, as we need to iterate through the entire list to check for membership.
        :param state:     tuple, a state (location) on the grid
        :param open_list: list, a heapq-based priority queue
        :return:          int, index of item if found and -1 otherwise
        """
        for item_index in range(len(open_list)):  # starts from 0 so we are safe returning -1
            if open_list[item_index][1] == state:
                return item_index
        return -1

    def solve(self, algorithm='greedy_best_first_search'):
        if algorithm == 'greedy_best_first_search':
            return self.greedy_best_first_search()
        elif algorithm == 'a_star' or algorithm == 'A*':
            return self.a_star()
        elif algorithm == 'iterative_deepening_a_star' or algorithm == 'IDA*':
            return self.iterative_deepening_a_star()

    # ------------------------------------ Optimal Algorithms ------------------------------------

    def greedy_best_first_search(self):
        """
        Note: Greedy BFS is neither optimal nor complete
        greedy_best_first_search algorithm that takes in a grid, a heuristic, a start state, and a goal state,
          and returns a path from the start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of states (locations on the grid) and the cost of the path
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        if self.puzzle.get_start() == self.puzzle.get_goal():
            return [self.puzzle.get_start()], 0
        elif not self.puzzle.valid_puzzle():
            raise ValueError('Start or goal state is an obstacle')
        # Initialize the current state to the initial state
        current_state = self.puzzle.get_start()
        # Initialize the current cost to the heuristic cost of the initial state
        current_f_cost = self.heuristic(current_state, self.puzzle.get_goal())
        # Initialize the closed list to be empty
        closed_list = dict()  # We need to store the parent! Sets do not suffice. Keys -> states, Values -> parents
        # Initialize the open list to contain the initial state; we use heapq to implement the priority queue
        open_list = []
        heapq.heappush(open_list, (current_f_cost, None, current_state))
        max_iter = 100
        iteration = 0
        while len(open_list) > 0 \
                and iteration < max_iter:  # while the open list is not empty, we can continue expanding states
            iteration += 1
            # pop the state with the lowest f-cost from the open list
            expanded_state = heapq.heappop(open_list)
            current_f_cost, current_state_parent, current_state = expanded_state
            closed_list[current_state] = current_state_parent  # add the current state to the closed list
            successors = self.puzzle.get_successors(current_state)
            print('Current state: ', current_state)
            if not successors:
                # print('Expanding a state with no successors! Current state: ', current_state)
                pass
            else:
                for successor in successors:
                    if successor == self.puzzle.get_goal():
                        successor_f_cost = self.heuristic(successor, self.puzzle.get_goal())
                        closed_list[successor] = current_state  # add the current state to the closed list
                        # If the successor is the goal, return the path from the initial state to the goal state
                        path = [successor]
                        parent = closed_list[successor]
                        start = self.puzzle.get_start()
                        while parent != start:
                            path.append(parent)
                            parent = closed_list[parent]
                        path.append(start)
                        path.reverse()
                        return path, successor_f_cost
                    # print('Successor: ', successor)
                    index_in_open_list = self.index_in_open_list(successor, open_list)
                    # If the successor is not in the closed list and not in the open list, add it to the open list
                    #   and set the parent of the successor to the current state
                    # print('Index in open list: ', index_in_open_list)
                    if successor in closed_list.keys():  # successor in closed list
                        continue
                    else:
                        successor_f_cost = self.heuristic(successor, self.puzzle.get_goal())
                        if index_in_open_list == -1:  # successor not in open list
                            # Add the successor to the open list; we are using heapq to implement the priority queue
                            heapq.heappush(open_list, (successor_f_cost, current_state, successor))
                            # print('Added successor to open list: ', successor)
                        else:  # successor in open list
                            # If the current f-cost is lower than the f-cost of the successor, update the f-cost of the
                            #   successor
                            if successor_f_cost < current_f_cost:
                                self.update_open_list(open_list, f_cost=successor_f_cost,
                                                      g_cost=None, state=successor,
                                                      parent=current_state, contains_g_cost=False)
                                # print('Updated f-cost of successor: ', successor)
                            else:
                                # print('Not a better path to successor: ', successor)
                                continue
            # print('------------------------------------')
            # print('Open list: ', open_list)
            # print('Closed list: ', closed_list)
            # print('------------------------------------')

        # If the open list is empty, return False; path is impossible or the algorithm has failed as incomplete
        raise ValueError('Path is impossible or the algorithm has failed!')

    def a_star(self):
        """
        Note: A* is optimal and complete
        A* algorithm that takes in a grid, a heuristic, a start state, and a goal state, and returns a path from
          the start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of states (locations on the grid) and the cost of the path
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        # Initialize the current state to the initial state
        current_state = self.puzzle.get_start()
        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_f_cost = self.heuristic(current_state, self.puzzle.get_goal()) + current_g_cost
        # Initialize the closed list to be empty
        closed_list = dict()  # We need to store the parent! Sets do not suffice. Keys -> states, Values -> parents
        # Initialize the open list to contain the initial state; we use heapq to implement the priority queue
        open_list = []
        heapq.heappush(open_list, (current_f_cost, current_g_cost, current_state))
        max_iter = 100
        iteration = 0
        while len(open_list) > 0 \
                and iteration < max_iter:  # while the open list is not empty, we can continue expanding states
            iteration += 1
            # pop the state with the lowest f-cost from the open list
            expanded_state = heapq.heappop(open_list)
            current_f_cost, current_g_cost, current_state_parent, current_state = expanded_state
            closed_list[current_state] = current_state_parent  # add the current state to the closed list
            successors = self.puzzle.get_successors(current_state)
            print('Current state: ', current_state)
            if not successors:
                # print('Expanding a state with no successors! Current state: ', current_state)
                pass
            else:
                for successor in successors:
                    if successor == self.puzzle.get_goal():
                        successor_g_cost = current_g_cost + 1
                        successor_f_cost = self.heuristic(successor, self.puzzle.get_goal()) + successor_g_cost
                        closed_list[successor] = current_state  # add the current state to the closed list
                        # If the successor is the goal, return the path from the initial state to the goal state
                        path = [successor]
                        parent = closed_list[successor]
                        start = self.puzzle.get_start()
                        while parent != start:
                            path.append(parent)
                            parent = closed_list[parent]
                        path.append(start)
                        path.reverse()
                        return path, successor_f_cost
                    # print('Successor: ', successor)
                    index_in_open_list = self.index_in_open_list(successor, open_list)
                    # If the successor is not in the closed list and not in the open list, add it to the open list
                    #   and set the parent of the successor to the current state
                    # print('Index in open list: ', index_in_open_list)
                    if successor in closed_list.keys():  # successor in closed list
                        continue
                    else:
                        successor_g_cost = current_g_cost + 1
                        successor_f_cost = self.heuristic(successor, self.puzzle.get_goal()) + successor_g_cost
                        if index_in_open_list == -1:  # successor not in open list
                            # Add the successor to the open list; we are using heapq to implement the priority queue
                            heapq.heappush(open_list, (successor_f_cost, successor_g_cost, current_state, successor))
                            # print('Added successor to open list: ', successor)
                        else:  # successor in open list
                            # If the current f-cost is lower than the f-cost of the successor, update the f-cost of the
                            #   successor
                            if successor_f_cost < current_f_cost:
                                self.update_open_list(open_list, f_cost=successor_f_cost,
                                                      g_cost=successor_g_cost, state=successor,
                                                      parent=current_state, contains_g_cost=False)
                                # print('Updated f-cost of successor: ', successor)
                            else:
                                # print('Not a better path to successor: ', successor)
                                continue
            # print('------------------------------------')
            # print('Open list: ', open_list)
            # print('Closed list: ', closed_list)
            # print('------------------------------------')

        # If the open list is empty, return False; path is impossible or the algorithm has failed (which theoretically
        #   should not happen)
        return False, False

    def iterative_deepening_a_star(self):
        """
        Iterative deepening A* search algorithm that takes in a grid, a heuristic, a start state, and a goal state, and
        returns a path from the start state to the goal state if possible; and False is returned if otherwise
        :return: either: a tuple of a list of states (locations on the grid) and the cost of the path
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """

        # Initialize the current state to the initial state
        current_state = self.puzzle.get_start()
        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_f_cost = self.heuristic(current_state, self.puzzle.get_goal()) + current_g_cost

        # ------------------------ Iterative Deepening A* ------------------------
        # Initialize the current f-cost limit to the current cost
        f_cost_limit = current_f_cost
        # ------------------------------------------------------------------------

        # Initialize the closed list to be empty
        closed_list = dict()
        # Initialize the open list to contain the initial state; we use heapq to implement the priority queue
        open_list = []
        heapq.heappush(open_list, (current_f_cost, current_g_cost, current_state))
        max_iter = 100
        iteration = 0

        while len(open_list) > 0 \
                and iteration < max_iter:
            iteration += 1
            # pop the state with the lowest f-cost from the open list
            expanded_state = heapq.heappop(open_list)
            current_f_cost, current_g_cost, current_state_parent, current_state = expanded_state
            closed_list[current_state] = current_state_parent  # add the current state to the closed list
            successors = self.puzzle.get_successors(current_state)
            print('Current state: ', current_state)
            if not successors:
                # print('Expanding a state with no successors! Current state: ', current_state)
                pass
            else:
                for successor in successors:
                    if successor == self.puzzle.get_goal():
                        closed_list[successor] = current_state  # add the current state to the closed list
                        # If the successor is the goal, return the path from the initial state to the goal state
                        path = [successor]
                        parent = closed_list[successor]
                        start = self.puzzle.get_start()
                        while parent != start:
                            path.append(parent)
                            parent = closed_list[parent]
                        path.append(start)
                        path.reverse()
                        return path, current_f_cost

    # ------------------------------------ Suboptimal Algorithms ------------------------------------
    """
    The weight is a parameter that can be adjusted to change the behavior of the algorithm. A weight of 1 is 
     equivalent to A* search. A weight greater than 1 will cause the algorithm to favor a greedy approach in terms
        of reducing the heuristic, and vice versa for a weight less than 1.
    """

    def weighted_a_star(self, weight):
        """
        Weighted A* algorithm that takes in a grid, a heuristic, a start state, and a goal state, and returns a path
        from the start state to the goal state if possible; and False is returned if otherwise
        :param: weight: float, a weight to be applied to the heuristic
        :return: either: a tuple of a list of states (locations on the grid) and the cost of the path
                     or: ValueError, if a path is impossible (unreachable goal, detected by re-expansion of states)
        """
        # Initialize the current state to the initial state
        current_state = self.puzzle.get_start()
        # Initialize the current g-cost to 0
        current_g_cost = 0
        # Initialize the current cost to the heuristic cost of the initial state
        current_f_cost = weight * self.heuristic(current_state, self.puzzle.get_goal()) + current_g_cost
        # Initialize the closed list to be empty
        closed_list = dict()  # We need to store the parent! Sets do not suffice. Keys -> states, Values -> parents
        # Initialize the open list to contain the initial state; we use heapq to implement the priority queue
        open_list = []
        heapq.heappush(open_list, (current_f_cost, current_g_cost, current_state))
        max_iter = 100
        iteration = 0
        while len(open_list) > 0 \
                and iteration < max_iter:  # while the open list is not empty, we can continue expanding states
            iteration += 1
            # pop the state with the lowest f-cost from the open list
            expanded_state = heapq.heappop(open_list)
            current_f_cost, current_g_cost, current_state_parent, current_state = expanded_state
            closed_list[current_state] = current_state_parent  # add the current state to the closed list
            successors = self.puzzle.get_successors(current_state)
            print('Current state: ', current_state)
            if not successors:
                # print('Expanding a state with no successors! Current state: ', current_state)
                pass
            else:
                for successor in successors:
                    if successor == self.puzzle.get_goal():
                        successor_g_cost = current_g_cost + 1
                        successor_f_cost = self.heuristic(successor, self.puzzle.get_goal()) + successor_g_cost
                        closed_list[successor] = current_state  # add the current state to the closed list
                        # If the successor is the goal, return the path from the initial state to the goal state
                        path = [successor]
                        parent = closed_list[successor]
                        start = self.puzzle.get_start()
                        while parent != start:
                            path.append(parent)
                            parent = closed_list[parent]
                        path.append(start)
                        path.reverse()
                        return path, successor_f_cost
                    # print('Successor: ', successor)
                    index_in_open_list = self.index_in_open_list(successor, open_list)
                    # If the successor is not in the closed list and not in the open list, add it to the open list
                    #   and set the parent of the successor to the current state
                    # print('Index in open list: ', index_in_open_list)
                    if successor in closed_list.keys():  # successor in closed list
                        continue
                    else:
                        successor_f_cost = weight * self.heuristic(successor, self.puzzle.get_goal())
                        successor_g_cost = current_g_cost + 1
                        if index_in_open_list == -1:  # successor not in open list
                            # Add the successor to the open list; we are using heapq to implement the priority queue
                            heapq.heappush(open_list, (successor_f_cost, successor_g_cost, current_state, successor))
                            # print('Added successor to open list: ', successor)
                        else:  # successor in open list
                            # If the current f-cost is lower than the f-cost of the successor, update the f-cost of the
                            #   successor
                            if successor_f_cost < current_f_cost:
                                self.update_open_list(open_list, f_cost=successor_f_cost,
                                                      g_cost=successor_g_cost, state=successor,
                                                      parent=current_state, contains_g_cost=False)
                                # print('Updated f-cost of successor: ', successor)
                            else:
                                # print('Not a better path to successor: ', successor)
                                continue
            # print('------------------------------------')
            # print('Open list: ', open_list)
            # print('Closed list: ', closed_list)
            # print('------------------------------------')

        # If the open list is empty, return False; path is impossible or the algorithm has failed (which theoretically
        #   should not happen)
        return False, False
