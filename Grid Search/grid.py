import math
import numpy as np
from state_space import StateSpace
from heuristic import Heuristic

grid_actions = {"right": (1, 0),
                "up": (0, 1),
                "left": (-1, 0),
                "down": (0, -1)}  # 4-directional movement


class Grid(StateSpace):
    #  We are implementing the start, goal, actions, successors, and the heuristic here.

    def __init__(self,
                 grid_x_length=10,
                 grid_y_length=10):
        super().__init__()
        self.grid_x_length = grid_x_length
        self.grid_y_length = grid_y_length
        self.actions = grid_actions
        self.current_state = None
        self.goal = None
        self.start = None

    def grid_movement(self, action, state, obstacles):
        """
        A successor function for a 2d-grid. The state is a tuple of (x, y) coordinates,
            and the action can be, for instance, (1, 0) for moving one step to the right,
            or (0, -1) for moving one step down. The obstacles are a SET of (x, y) coordinates.
            See if the move is valid; return the new state if it is, and False otherwise.
        This function should run in O(1) time, as checking membership for a SET is O(1).
        :param action:        tuple, movement in x and y directions
        :param state:         tuple, current state (location)
        :param obstacles:     set (of tuples), locations of obstacles
        :return:              tuple, new state if valid,
                              False, otherwise
        """
        x, y = state[0], state[1]
        if action == 'right':
            x += 1
        elif action == 'up':
            y += 1
        elif action == 'left':
            x -= 1
        elif action == 'down':
            y -= 1
        else:
            raise ValueError('Invalid action: {}'.format(action))

        if (x, y) in obstacles:
            Warning('This action leads to obstacle at location: ({}, {})'.format(x, y))
            return False
        elif self.out_of_state_space(state=(x, y)):
            Warning('This action leads to location that is out of state space: ({}, {})'.format(x, y))
            return False
        else:
            return x, y

    def get_successors(self, current_state, obstacles):
        successors = []
        for action in self.actions:
            result = self.grid_movement(action, current_state, obstacles)
            if result:
                successors.append(result)
        if len(successors) == 0:
            return False
        else:
            return successors

    @staticmethod  # this is a heuristic
    def euclidean_distance_2d(state_1, state_2):
        """
        Euclidean distance heuristic for a 2d grid-based Space.
        :param state_1: tuple, the first x-y location
        :param state_2: tuple, the second x-y location
        :return: the Euclidean distance between the two states (locations)
        """
        return math.sqrt((state_1[0] - state_2[0]) ** 2 + (state_1[1] - state_2[1]) ** 2)

    def generate_random_obstacles(self, obstacle_count, distribution='uniform',
                                  loc=None, scale=None, seed=42):
        np.random.seed(seed)
        obstacles = set()
        if obstacle_count > self.grid_x_length * self.grid_y_length:
            raise ValueError('Obstacle count cannot be greater than the the number of points on the grid')
        i = 0
        if distribution == 'uniform':
            while i < obstacle_count:
                x = np.random.randint(low=0, high=self.grid_x_length)
                y = np.random.randint(low=0, high=self.grid_y_length)
                if (x, y) not in obstacles:
                    obstacles.add((x, y))
                    i += 1
                else:
                    continue
        elif distribution == 'binomial':
            while i < obstacle_count:
                x = np.random.binomial(self.grid_x_length, loc)
                y = np.random.binomial(self.grid_y_length, loc)
                if (x, y) not in obstacles:
                    obstacles.add((x, y))
                    i += 1
                else:
                    continue
        elif distribution == 'normal':
            while i < obstacle_count:
                x = np.floor(np.random.normal(loc, scale))
                y = np.floor(np.random.normal(loc, scale))
                if x > self.grid_x_length:
                    x = self.grid_x_length
                elif x < 0:
                    x = 0
                if y > self.grid_y_length:
                    y = self.grid_y_length
                elif y < 0:
                    y = 0
                if (x, y) not in obstacles:
                    obstacles.add((x, y))
                    i += 1
                else:
                    continue
        return obstacles

    def out_of_state_space(self, state):
        if state[0] > self.grid_x_length-1 or state[1] > self.grid_y_length-1:
            return True
        elif state[0] < 0 or state[1] < 0:
            return True
        else:
            return False

    def set_goal(self, goal, obstacles):
        if not self.out_of_state_space(goal):
            self.goal = goal
            return True
        elif goal in obstacles:
            raise ValueError('Goal is an obstacle')
        else:
            raise ValueError('Goal is out of the grid')

    def set_start(self, start, obstacles):
        if not self.out_of_state_space(start):
            self.start = start
            return True
        elif start in obstacles:
            raise ValueError('Start is an obstacle')
        else:
            raise ValueError('Start is out of the grid')

    def set_state(self, state, obstacles):
        if not self.out_of_state_space(state):
            self.current_state = state
            return True
        elif state in obstacles:
            raise ValueError('State/location is an obstacle')
        else:
            raise ValueError('State/location is out of the grid')

    def get_goal(self):
        return self.goal

    def get_start(self):
        return self.start

    def get_state(self):
        return self.current_state


#%%
