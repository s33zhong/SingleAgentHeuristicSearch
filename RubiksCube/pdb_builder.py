import json
import numpy as np
import ranking
from collections import deque
from cube import RubiksCube


class PatternDataBase:
    def __init__(self, cube: RubiksCube, opt='corner'):
        self.cube = cube
        self.db = np.zeros(40320, dtype=np.uint8)  # maximum length
        self.opt = opt
        self.queue = deque()

    def rank(self, cube=None):
        if self.opt == 'corner':
            return ranking.rank_corner(cube.corner_position, cube.corner_rotation)

    def unrank(self, rank):
        if self.opt == 'corner':
            return ranking.unrank_corner(rank)

    def add_entry(self, rank, cost):
        if self.db[rank] == 0:
            self.db[rank] = cost
        else:
            if cost < self.db[rank]:
                self.db[rank] = cost
        return True

    def export_db(self):
        f = open("{}_pdb.bin".format(self.opt+'wo_rot'), "wb")
        byte_db = bytearray(self.db)
        f.write(byte_db)
        f.close()
        return True

    def export_queue(self):
        f = open("{}_queue.txt".format(self.opt), "w")
        queue_str = str(self.queue)
        f.write(queue_str)
        f.close()
        return True

    def bfs(self):
            """
            Breadth-first search to find the shortest path to each node
            :return:
            """
            self.add_entry(0, 0)
            self.queue.append((self.cube, 0, '', ''))  # (cube, cost, last_action, second_last_action)
            current_max_depth = 0
            # no need to go deeper than 20 moves; all solvable Rubik's Cube states can be solved in 20 moves or less
            max_depth = 20
            i = 0
            less = 0
            while self.queue:
                i += 1
                if i % 1000 == 0:
                    print('Iteration: {}'.format(i))
                    print('Queue length: {}'.format(len(self.queue)))
                current_entry = self.queue.popleft()
                current_cube = current_entry[0]
                current_cost = current_entry[1]
                if current_cost > current_max_depth:
                    current_max_depth = current_cost
                    print('Current max depth: {}'.format(current_max_depth))
                last_action = current_entry[2]
                second_last_action = current_entry[3]
                available_actions = current_cube.prune_action(last_action=last_action,
                                                              second_last_action=second_last_action)

                for action in available_actions:
                    successor = current_cube.copy()
                    successor.twist(action)
                    successor_rank = self.rank(successor)
                    successor_cost = current_cost + 1
                    if self.db[successor_rank] == 0 or successor_cost < self.db[successor_rank]:
                        self.add_entry(successor_rank, successor_cost)
                        self.queue.append((successor, successor_cost, action, last_action))
                del current_cube
            return True

