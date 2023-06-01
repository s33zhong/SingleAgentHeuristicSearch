import numpy as np
from state_space import StateSpace
from random import randint, choice


class RubiksCube(StateSpace):

    def __init__(self, n=3, colours=None):
        """
        :param n:         The dimension of the cube
        :param colours:   The colours of the cube
        :param state:     The state of the cube

        """
        super().__init__()
        self.n = n
        if colours is None:
            self.colours = ['w', 'o', 'g', 'r', 'b', 'y']
        else:
            self.colours = colours
        self.start = [[[c for x in range(self.n)] for y in range(self.n)] for c in self.colours]
        self.current_state = self.start
        #  Note that we do not include the middle layer moves like M, E, S, etc. because they are redundant
        #   with the other moves. For example, M is the same as R followed by L' and E is the same as U' followed
        #   by D. With this, we can reduce the branching factor from 27 to 18.
        self.actions = ['F', 'B', 'L', 'R', 'U', 'D',
                        'f', 'b', 'l', 'r', 'u', 'd',
                        'F2', 'B2', 'L2', 'R2', 'U2', 'D2']
        #  Then, since we should not move the same face twice in a row, we can remove the moves that are redundant
        #   with the previous move. With this, we can reduce the branching factor from 18 to 15.

        #  Finally, we would define the opposite face; if we turned a face and then its opposite face, we should not
        #   turn the original face again. This means, for the third move, the branching factor is 12. This means,
        #   whenever we are making the moves on opposite faces, the third move has a branching factor of 12.
        #   Equivalently, whenever a middle layer move is made, the next move has less branching factor. This is some
        #   compensation for the depth increase for not adding the middle layer moves.

        #  By reducing the branching factor which leads to duplicates, we improve the efficiency of IDA*.

        self.opposite_face_actions = {'F': 'B', 'B': 'F', 'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}

        #  We define a state of the cube as two lists; one containing the edge cubies and the other containing the
        #   corner cubies. Each cubie is represented by a tuple of the form (rotation, position). As a common tradition,
        #   we define the white face to be the top, the green face to be the front, and the orange face to be the
        #   left face. The rotation is defined as the number of clockwise rotations of the cubie.

        # 8 corner cubies are represented as:
        # DEFINE  CORNER_URF       WGR                   0
        # DEFINE  CORNER_URB       WRB                   1
        # DEFINE  CORNER_ULB       WBO                   2
        # DEFINE  CORNER_ULF       WOG                   3
        # DEFINE  CORNER_DRF       GRY                   4
        # DEFINE  CORNER_DRB       RBY                   5
        # DEFINE  CORNER_DLB       BOY                   6
        # DEFINE  CORNER_DLF       GOY                   7

        # Note: 7 rotations dictates the last rotation
        # 3 rotations are defined as:
        # DEFINE ROTATION_0                            0
        # DEFINE ROTATION_90                           1
        # DEFINE ROTATION_180                          2
        self.corner = np.arange(8)
        self.corner_rotations = np.zeros(7)  # rotations of first 7 corner cubies
        self.corner_map = {
            "0": "White_Green_Red",
            "1": "White_Red_Blue",
            "2": "White_Blue_Orange",
            "3": "White_Orange_Green",
            "4": "Green_Red_Yellow",
            "5": "Red_Blue_Yellow",
            "6": "Blue_Orange_Yellow",
            "7": "Green_Orange_Yellow",
        }

        # 12 edge cubies are represented as:
        # DEFINE  EDGE_UF          WG                   0
        # DEFINE  EDGE_UR          WR                   1
        # DEFINE  EDGE_UB          WB                   2
        # DEFINE  EDGE_UL          WO                   3
        # DEFINE  EDGE_DF          GY                   4
        # DEFINE  EDGE_DR          RY                   5
        # DEFINE  EDGE_DB          BY                   6
        # DEFINE  EDGE_DL          OY                   7
        # DEFINE  EDGE_FR          GR                   8
        # DEFINE  EDGE_BR          RB                   9
        # DEFINE  EDGE_BL          BO                  10
        # DEFINE  EDGE_FL          GO                  11

        # Note: 11 rotations dictates the last rotation
        # 3 rotations are defined as:
        # DEFINE ROTATION_0                            0
        # DEFINE ROTATION_180                          1
        self.edge = np.arange(12)
        self.edge_rotations = np.zeros(11)
        self.edge_map = {
            "0": "White_Green",
            "1": "White_Red",
            "2": "White_Blue",
            "3": "White_Orange",
            "4": "Green_Yellow",
            "5": "Red_Yellow",
            "6": "Blue_Yellow",
            "7": "Orange_Yellow",
            "8": "Green_Red",
            "9": "Red_Blue",
            "10": "Blue_Orange",
            "11": "Green_Orange"
        }

    def twist(self, action):
        if action not in self.actions:
            raise Exception("Invalid action")

        if action == 'U':
            temp = self.corner[0]
            self.corner[0] = self.corner[1]
            self.corner[1] = self.corner[2]
            self.corner[2] = self.corner[3]
            self.corner[3] = temp

            temp = self.edge[0]
            self.edge[0] = self.edge[1]
            self.edge[1] = self.edge[2]
            self.edge[2] = self.edge[3]
            self.edge[3] = temp

        elif action == 'u':
            temp = self.corner[3]
            self.corner[3] = self.corner[2]
            self.corner[2] = self.corner[1]
            self.corner[1] = self.corner[0]
            self.corner[0] = temp

            temp = self.edge[3]
            self.edge[3] = self.edge[2]
            self.edge[2] = self.edge[1]
            self.edge[1] = self.edge[0]
            self.edge[0] = temp

        elif action == 'U2':
            temp1 = self.corner[0]
            temp2 = self.corner[1]
            self.corner[0] = self.corner[2]
            self.corner[2] = temp1
            self.corner[1] = self.corner[3]
            self.corner[3] = temp2

            temp1 = self.edge[0]
            temp2 = self.edge[1]
            self.edge[0] = self.edge[2]
            self.edge[2] = temp1
            self.edge[1] = self.edge[3]
            self.edge[3] = temp2

        elif action == 'D':
            temp = self.corner[4]
            self.corner[4] = self.corner[5]
            self.corner[5] = self.corner[6]
            self.corner[6] = self.corner[7]
            self.corner[7] = temp

            temp = self.edge[4]
            self.edge[4] = self.edge[5]
            self.edge[5] = self.edge[6]
            self.edge[6] = self.edge[7]
            self.edge[7] = temp

        elif action == 'd':
            temp = self.corner[4]
            self.corner[4] = self.corner[5]
            self.corner[5] = self.corner[6]
            self.corner[6] = self.corner[7]
            self.corner[7] = temp

            temp = self.edge[4]
            self.edge[4] = self.edge[5]
            self.edge[5] = self.edge[6]
            self.edge[6] = self.edge[7]
            self.edge[7] = temp

        elif action == 'D2':
            temp1 = self.corner[4]
            temp2 = self.corner[5]
            self.corner[4] = self.corner[6]
            self.edge[2] = temp1
            self.corner[5] = self.corner[7]
            self.corner[7] = temp2

            temp1 = self.edge[4]
            temp2 = self.edge[5]
            self.edge[4] = self.edge[6]
            self.edge[6] = temp1
            self.edge[5] = self.edge[7]
            self.edge[7] = temp2

        elif action == 'F':
            temp = self.corner[0]
            self.corner[0] = self.corner[3]
            self.corner[3] = self.corner[7]
            self.corner[7] = self.corner[4]
            self.corner[4] = temp

            temp = self.edge[0]
            self.edge[8] = self.edge[0]
            self.edge[0] = self.edge[11]
            self.edge[11] = self.edge[4]
            self.edge[4] = temp

        elif action == 'f':
            temp = self.corner[0]
            self.corner[0] = self.corner[4]
            self.corner[4] = self.corner[7]
            self.corner[7] = self.corner[3]
            self.corner[3] = temp

            temp = self.edge[4]
            self.edge[8] = self.edge[4]
            self.edge[4] = self.edge[11]
            self.edge[11] = self.edge[0]
            self.edge[0] = temp

        elif action == 'F2':
            temp = self.corner[0]
            self.corner[0] = self.corner[3]
            self.corner[3] = self.corner[7]
            self.corner[7] = self.corner[4]
            self.corner[4] = temp

            temp = self.edge[8]
            self.edge[8] = self.edge[0]
            self.edge[0] = self.edge[11]
            self.edge[11] = self.edge[4]
            self.edge[4] = temp

        elif action == 'B':
            temp = self.corner[1]
            self.corner[1] = self.corner[5]
            self.corner[5] = self.corner[6]
            self.corner[6] = self.corner[2]
            self.corner[2] = temp

            temp = self.edge[2]
            self.edge[2] = self.edge[10]
            self.edge[10] = self.edge[6]
            self.edge[6] = self.edge[9]
            self.edge[9] = temp

        elif action == 'b':
            temp = self.corner[5]
            self.corner[5] = self.corner[1]
            self.corner[1] = self.corner[2]
            self.corner[2] = self.corner[6]
            self.corner[6] = temp

            temp = self.edge[10]
            self.edge[10] = self.edge[2]
            self.edge[2] = self.edge[9]
            self.edge[9] = self.edge[6]
            self.edge[6] = temp

        elif action == 'B2':
            temp1 = self.corner[1]
            temp2 = self.corner[5]
            self.corner[1] = self.corner[6]
            self.corner[6] = temp1
            self.corner[5] = self.corner[2]
            self.corner[2] = temp2

            temp1 = self.edge[2]
            temp2 = self.edge[9]
            self.edge[2] = self.edge[10]
            self.edge[10] = temp1
            self.edge[9] = self.edge[6]
            self.edge[6] = temp2

        elif action == 'R':
            temp = self.corner[0]
            self.corner[0] = self.corner[4]
            self.corner[4] = self.corner[5]
            self.corner[5] = self.corner[1]
            self.corner[1] = temp

            temp = self.edge[1]
            self.edge[1] = self.edge[8]
            self.edge[8] = self.edge[5]
            self.edge[5] = self.edge[9]
            self.edge[9] = temp

        elif action == 'r':
            temp = self.corner[0]
            self.corner[0] = self.corner[1]
            self.corner[1] = self.corner[5]
            self.corner[5] = self.corner[4]
            self.corner[4] = temp

            temp = self.edge[1]
            self.edge[1] = self.edge[9]
            self.edge[9] = self.edge[5]
            self.edge[5] = self.edge[8]
            self.edge[8] = temp

        elif action == 'R2':
            temp1 = self.corner[0]
            temp2 = self.corner[1]
            self.corner[0] = self.corner[5]
            self.corner[5] = temp1
            self.corner[1] = self.corner[4]
            self.corner[4] = temp2

            temp1 = self.edge[1]
            temp2 = self.edge[8]
            self.edge[1] = self.edge[5]
            self.edge[5] = temp1
            self.edge[8] = self.edge[9]
            self.edge[9] = temp2

        elif action == 'L':
            temp = self.corner[3]
            self.corner[3] = self.corner[2]
            self.corner[2] = self.corner[6]
            self.corner[6] = self.corner[7]
            self.corner[7] = temp

            temp = self.edge[3]
            self.edge[3] = self.edge[10]
            self.edge[10] = self.edge[7]
            self.edge[7] = self.edge[11]
            self.edge[11] = temp

        elif action == 'l':
            temp = self.corner[7]
            self.corner[7] = self.corner[6]
            self.corner[6] = self.corner[2]
            self.corner[2] = self.corner[3]
            self.corner[3] = temp

            temp = self.edge[10]
            self.edge[10] = self.edge[3]
            self.edge[3] = self.edge[11]
            self.edge[11] = self.edge[7]
            self.edge[7] = temp

        elif action == 'L2':
            temp1 = self.corner[3]
            temp2 = self.corner[7]
            self.corner[3] = self.corner[6]
            self.corner[6] = temp1
            self.corner[7] = self.corner[2]
            self.corner[2] = temp2

            temp1 = self.edge[3]
            temp2 = self.edge[11]
            self.edge[3] = self.edge[7]
            self.edge[7] = temp1
            self.edge[11] = self.edge[10]
            self.edge[10] = temp2

        return True

    def twist_sequence(self, action_sequence):
        for action in action_sequence:
            self.twist(action)
        return True

    def generate_scramble(self, length, seed=42):
        """
        This function generates a random scramble of the cube.
        :param length: int, length of the scramble
        :param seed:   int, seed for the random number generator
        :return:
        """
        np.random.seed(seed)
        scramble = np.random.choice(self.actions, length)
        return scramble

    def prune_action(self, last_move, second_last_move):
        """
        This function prunes the moves that are redundant with the previous move.
        :param last_move:        str, last move made
        :param second_last_move: str, second last move made
        :return:
        """

        available_actions = self.actions.copy()
        # Removing the 2 to reduce conditions
        if '2' in last_move:
            last_move = last_move.replace('2', '')
        if '2' in second_last_move:
            second_last_move = second_last_move.replace('2', '')

        # Reducing branching factor to 15
        available_actions.remove(last_move.capitalize())
        available_actions.remove(last_move.lower())
        available_actions.remove(last_move + '2')

        if self.opposite_face_actions[second_last_move] == last_move:
            # Reducing branching factor to 12
            available_actions.remove(second_last_move.capitalize())
            available_actions.remove(second_last_move.lower())
            available_actions.remove(second_last_move + '2')

        return available_actions

    def reset_cube(self):
        self.edge = np.arange(12)
        self.edge_rotations = np.zeros(11)
        self.corner = np.arange(8)
        self.corner_rotations = np.zeros(7)

    def show_cube_color(self):
        edge_colors = [self.edge_map[str(edge)] for edge in self.edge]
        corner_colors = [self.corner_map[str(corner)] for corner in self.corner]

        first_layer = [corner_colors[0], edge_colors[1], corner_colors[1], edge_colors[2], corner_colors[2],
                       edge_colors[3], corner_colors[3], edge_colors[0]]
        second_layer = [edge_colors[8], edge_colors[9],  edge_colors[10], edge_colors[11]]
        third_layer = [corner_colors[4], edge_colors[5], corner_colors[5], edge_colors[6], corner_colors[6],
                       edge_colors[7], corner_colors[7], edge_colors[4]]

        return first_layer, second_layer, third_layer

    def get_state(self):
        return self.corner, self.corner_rotations, self.edge, self.edge_rotations

    def visualize_state(self):
        print("Corner cubies: ", self.corner)
        print("Corner cubies rotations: ", self.corner_rotations)
        print("Edge cubies: ", self.edge)
        print("Edge cubies rotations: ", self.edge_rotations)
