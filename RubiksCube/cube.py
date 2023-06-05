from copy import deepcopy
import numpy as np
from state_space import StateSpace
from random import randint, choice

URF = 0
URB = 1
ULB = 2
ULF = 3
DRF = 4
DRB = 5
DLB = 6
DLF = 7

UF = 0
UR = 1
UB = 2
UL = 3
DF = 4
DR = 5
DB = 6
DL = 7
FR = 8
BR = 9
BL = 10
FL = 11


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
        self.corner_position = np.arange(8)
        self.corner_rotation = np.zeros(8)  # rotations of first 7 corner cubies
        self.corner_map = {
            "0": "White_Green_Red",
            "1": "White_Red_Blue",
            "2": "White_Blue_Orange",
            "3": "White_Green_Orange",
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
        self.edge_position = np.arange(12)
        self.edge_rotation = np.zeros(12)
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

        twist = 1
        if action == action.lower():
            twist = 3
        elif '2' in action:
            twist = 2
        twist_count = range(twist)
        action_upper = action.upper()

        if 'U' in action_upper:
            for i in twist_count:
                temp = self.corner_position[URF]
                self.corner_position[URF] = self.corner_position[URB]
                self.corner_position[URB] = self.corner_position[ULB]
                self.corner_position[ULB] = self.corner_position[ULF]
                self.corner_position[ULF] = temp

                temp_rot = self.corner_rotation[URF]
                self.corner_rotation[URF] = self.corner_rotation[URB]
                self.corner_rotation[URB] = self.corner_rotation[ULB]
                self.corner_rotation[ULB] = self.corner_rotation[ULF]
                self.corner_rotation[ULF] = temp_rot

                temp = self.edge_position[UF]
                self.edge_position[UF] = self.edge_position[UR]
                self.edge_position[UR] = self.edge_position[UB]
                self.edge_position[UB] = self.edge_position[UL]
                self.edge_position[UL] = temp

                temp_rot = self.edge_rotation[UF]
                self.edge_rotation[UF] = self.edge_rotation[UR]
                self.edge_rotation[UR] = self.edge_rotation[UB]
                self.edge_rotation[UB] = self.edge_rotation[UL]
                self.edge_rotation[UL] = temp_rot

        #
        # elif action == 'u':
        #     temp = self.corner[ULF]
        #     self.corner[ULF] = self.corner[ULB]
        #     self.corner[ULB] = self.corner[URB]
        #     self.corner[URB] = self.corner[URF]
        #     self.corner[URF] = temp
        #
        #     temp = self.corner[UL]
        #     self.corner[UL] = self.corner[UB]
        #     self.corner[UB] = self.corner[UR]
        #     self.corner[UR] = self.corner[UF]
        #     self.corner[UF] = temp
        #
        # elif action == 'U2':
        #     temp1 = self.corner[URF]
        #     temp2 = self.corner[URB]
        #     self.corner[URF] = self.corner[ULB]
        #     self.corner[ULB] = temp1
        #     self.corner[URB] = self.corner[ULF]
        #     self.corner[ULF] = temp2
        #
        #     temp1 = self.corner[UF]
        #     temp2 = self.corner[UR]
        #     self.corner[UF] = self.corner[UB]
        #     self.corner[UB] = temp1
        #     self.corner[UR] = self.corner[UL]
        #     self.corner[UL] = temp2

        elif 'D' in action_upper:
            for i in twist_count:
                temp = self.corner_position[DLF]
                self.corner_position[DLF] = self.corner_position[DLB]
                self.corner_position[DLB] = self.corner_position[DRB]
                self.corner_position[DRB] = self.corner_position[DRF]
                self.corner_position[DRF] = temp
                temp_rot = self.corner_rotation[DLF]
                self.corner_rotation[DLF] = self.corner_rotation[DLB]
                self.corner_rotation[DLB] = self.corner_rotation[DRB]
                self.corner_rotation[DRB] = self.corner_rotation[DRF]
                self.corner_rotation[DRF] = temp_rot

                temp = self.edge_position[DL]
                self.edge_position[DL] = self.edge_position[DB]
                self.edge_position[DB] = self.edge_position[DR]
                self.edge_position[DR] = self.edge_position[DF]
                self.edge_position[DF] = temp
                temp_rot = self.edge_rotation[DL]
                self.edge_rotation[DL] = self.edge_rotation[DB]
                self.edge_rotation[DB] = self.edge_rotation[DR]
                self.edge_rotation[DR] = self.edge_rotation[DF]
                self.edge_rotation[DF] = temp_rot

        # elif action == 'd':
        #     temp = self.corner[DRF]
        #     self.corner[DRF] = self.corner[DRB]
        #     self.corner[DRB] = self.corner[DLB]
        #     self.corner[DLB] = self.corner[DLF]
        #     self.corner[DLF] = temp
        #
        #     temp = self.corner[DF]
        #     self.corner[DF] = self.corner[DR]
        #     self.corner[DR] = self.corner[DB]
        #     self.corner[DB] = self.corner[DL]
        #     self.corner[DL] = temp
        #
        # elif action == 'D2':
        #     temp1 = self.corner[DRF]
        #     temp2 = self.corner[DRB]
        #     self.corner[DRF] = self.corner[DLB]
        #     self.corner[UB] = temp1
        #     self.corner[DRB] = self.corner[DLF]
        #     self.corner[DLF] = temp2
        #
        #     temp1 = self.corner[DF]
        #     temp2 = self.corner[DR]
        #     self.corner[DF] = self.corner[DB]
        #     self.corner[DB] = temp1
        #     self.corner[DR] = self.corner[DL]
        #     self.corner[DL] = temp2

        elif 'F' in action_upper:
            for i in twist_count:
                temp = self.corner_position[URF]
                self.corner_position[URF] = self.corner_position[ULF]
                self.corner_position[ULF] = self.corner_position[DLF]
                self.corner_position[DLF] = self.corner_position[DRF]
                self.corner_position[DRF] = temp

                temp_rot = self.corner_rotation[URF]
                self.corner_rotation[URF] = (self.corner_rotation[ULF] + 2) % 3
                self.corner_rotation[ULF] = (self.corner_rotation[DLF] + 1) % 3
                self.corner_rotation[DLF] = (self.corner_rotation[DRF] + 2) % 3
                self.corner_rotation[DRF] = (temp_rot + 1) % 3

                temp = self.edge_position[UF]
                self.edge_position[UF] = self.edge_position[FL]
                self.edge_position[FL] = self.edge_position[DF]
                self.edge_position[DF] = self.edge_position[FR]
                self.edge_position[FR] = temp
                temp_rot = self.edge_rotation[UF]
                self.edge_rotation[UF] = 1 - self.edge_rotation[FL]
                self.edge_rotation[FL] = 1 - self.edge_rotation[DF]
                self.edge_rotation[DF] = 1 - self.edge_rotation[FR]
                self.edge_rotation[FR] = 1 - temp_rot


        # elif action == 'f':
        #     temp = self.corner[URF]
        #     self.corner[URF] = self.corner[DRF]
        #     self.corner[DRF] = self.corner[DLF]
        #     self.corner[DLF] = self.corner[ULF]
        #     self.corner[ULF] = temp
        #
        #     temp = self.corner[UF]
        #     self.corner[UF] = self.corner[FR]
        #     self.corner[FR] = self.corner[DF]
        #     self.corner[DF] = self.corner[FL]
        #     self.corner[FL] = temp
        #
        # elif action == 'F2':
        #     temp1 = self.corner[URF]
        #     temp2 = self.corner[DLF]
        #     self.corner[URF] = self.corner[ULF]
        #     self.corner[ULF] = temp1
        #     self.corner[DLF] = self.corner[DRF]
        #     self.corner[DRF] = temp2
        #
        #     temp1 = self.corner[FR]
        #     temp2 = self.corner[FL]
        #     self.corner[FR] = self.corner[UF]
        #     self.corner[UF] = temp1
        #     self.corner[FL] = self.corner[DF]
        #     self.corner[DF] = temp2

        elif 'B' in action_upper:
            for i in twist_count:
                temp = self.corner_position[URB]
                self.corner_position[URB] = self.corner_position[DRB]
                self.corner_position[DRB] = self.corner_position[DLB]
                self.corner_position[DLB] = self.corner_position[ULB]
                self.corner_position[ULB] = temp
                temp_rot = self.corner_rotation[URB]
                self.corner_rotation[URB] = (self.corner_rotation[DRB] + 1) % 3
                self.corner_rotation[DRB] = (self.corner_rotation[DLB] + 2) % 3
                self.corner_rotation[DLB] = (self.corner_rotation[ULB] + 1) % 3
                self.corner_rotation[ULB] = (temp_rot + 2) % 3

                temp = self.edge_position[BL]
                self.edge_position[BL] = self.edge_position[UB]
                self.edge_position[UB] = self.edge_position[BR]
                self.edge_position[BR] = self.edge_position[DB]
                self.edge_position[DB] = temp
                temp_rot = self.edge_rotation[BL]
                self.edge_rotation[BL] = 1 - self.edge_rotation[UB]
                self.edge_rotation[UB] = 1 - self.edge_rotation[BR]
                self.edge_rotation[BR] = 1 - self.edge_rotation[DB]
                self.edge_rotation[DB] = 1 - temp_rot

        # elif action == 'b':
        #     temp = self.corner[DRB]
        #     self.corner[DRB] = self.corner[URB]
        #     self.corner[URB] = self.corner[ULB]
        #     self.corner[ULB] = self.corner[DLB]
        #     self.corner[DLB] = temp
        #
        #     temp = self.corner[UB]
        #     self.corner[UB] = self.corner[BL]
        #     self.corner[BL] = self.corner[DB]
        #     self.corner[DB] = self.corner[BR]
        #     self.corner[BR] = temp
        #
        # elif action == 'B2':
        #     temp1 = self.corner[URB]
        #     temp2 = self.corner[DRB]
        #     self.corner[URB] = self.corner[DLB]
        #     self.corner[DLB] = temp1
        #     self.corner[DRB] = self.corner[ULB]
        #     self.corner[ULB] = temp2
        #
        #     temp1 = self.corner[UB]
        #     temp2 = self.corner[BL]
        #     self.corner[UB] = self.corner[DB]
        #     self.corner[DB] = temp1
        #     self.corner[BL] = self.corner[BR]
        #     self.corner[BR] = temp2

        elif 'R' in action_upper:
            for i in twist_count:
                temp = self.corner_position[URF]
                self.corner_position[URF] = self.corner_position[DRF]
                self.corner_position[DRF] = self.corner_position[DRB]
                self.corner_position[DRB] = self.corner_position[URB]
                self.corner_position[URB] = temp
                temp_rot = self.corner_rotation[URF]
                self.corner_rotation[URF] = (self.corner_rotation[DRF] + 1) % 3
                self.corner_rotation[DRF] = (self.corner_rotation[DRB] + 2) % 3
                self.corner_rotation[DRB] = (self.corner_rotation[URB] + 1) % 3
                self.corner_rotation[URB] = (temp_rot + 2) % 3

                temp = self.edge_position[UR]
                self.edge_position[UR] = self.edge_position[FR]
                self.edge_position[FR] = self.edge_position[DR]
                self.edge_position[DR] = self.edge_position[BR]
                self.edge_position[BR] = temp
                temp_rot = self.edge_rotation[UR]
                self.edge_rotation[UR] = self.edge_rotation[FR]
                self.edge_rotation[FR] = self.edge_rotation[DR]
                self.edge_rotation[DR] = self.edge_rotation[BR]
                self.edge_rotation[BR] = temp_rot

        # elif action == 'r':
        #     temp = self.corner[URF]
        #     self.corner[URF] = self.corner[URB]
        #     self.corner[URB] = self.corner[DRB]
        #     self.corner[DRB] = self.corner[DRF]
        #     self.corner[DRF] = temp
        #
        #     temp = self.corner[UR]
        #     self.corner[UR] = self.corner[BR]
        #     self.corner[BR] = self.corner[DR]
        #     self.corner[DR] = self.corner[FR]
        #     self.corner[FR] = temp
        #
        # elif action == 'R2':
        #     temp1 = self.corner[URF]
        #     temp2 = self.corner[URB]
        #     self.corner[URF] = self.corner[DRB]
        #     self.corner[DRB] = temp1
        #     self.corner[URB] = self.corner[DRF]
        #     self.corner[DRF] = temp2
        #
        #     temp1 = self.corner[UR]
        #     temp2 = self.corner[FR]
        #     self.corner[UR] = self.corner[DR]
        #     self.corner[DR] = temp1
        #     self.corner[FR] = self.corner[BR]
        #     self.corner[BR] = temp2

        elif 'L' in action_upper:
            for i in twist_count:
                temp = self.corner_position[ULF]
                self.corner_position[ULF] = self.corner_position[ULB]
                self.corner_position[ULB] = self.corner_position[DLB]
                self.corner_position[DLB] = self.corner_position[DLF]
                self.corner_position[DLF] = temp
                temp_rot = self.corner_rotation[ULF]
                self.corner_rotation[ULF] = (self.corner_rotation[ULB] + 2) % 3
                self.corner_rotation[ULB] = (self.corner_rotation[DLB] + 1) % 3
                self.corner_rotation[DLB] = (self.corner_rotation[DLF] + 2) % 3
                self.corner_rotation[DLF] = (temp_rot + 1) % 3

                temp = self.edge_position[UL]
                self.edge_position[UL] = self.edge_position[BL]
                self.edge_position[BL] = self.edge_position[DL]
                self.edge_position[DL] = self.edge_position[FL]
                self.edge_position[FL] = temp
                temp_rot = self.edge_rotation[UL]
                self.edge_rotation[UL] = self.edge_rotation[BL]
                self.edge_rotation[BL] = self.edge_rotation[DL]
                self.edge_rotation[DL] = self.edge_rotation[FL]
                self.edge_rotation[FL] = temp_rot

        # elif action == 'l':
        #     temp = self.corner[DLF]
        #     self.corner[DLF] = self.corner[DLB]
        #     self.corner[DLB] = self.corner[ULB]
        #     self.corner[ULB] = self.corner[ULF]
        #     self.corner[ULF] = temp
        #
        #     temp = self.corner[BL]
        #     self.corner[BL] = self.corner[UL]
        #     self.corner[UL] = self.corner[FL]
        #     self.corner[FL] = self.corner[DL]
        #     self.corner[DL] = temp
        #
        # elif action == 'L2':
        #     temp1 = self.corner[ULF]
        #     temp2 = self.corner[DLF]
        #     self.corner[ULF] = self.corner[DLB]
        #     self.corner[DLB] = temp1
        #     self.corner[DLF] = self.corner[ULB]
        #     self.corner[ULB] = temp2
        #
        #     temp1 = self.corner[UL]
        #     temp2 = self.corner[FL]
        #     self.corner[UL] = self.corner[DL]
        #     self.corner[DL] = temp1
        #     self.corner[FL] = self.corner[BL]
        #     self.corner[BL] = temp2

        return True

    def twist_sequence(self, action_sequence):
        for action in action_sequence:
            self.twist(action)
            print('Action twisted: ', action)
        return True

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def undo_action(action):
        if '2' in action:
            return action
        return action.swapcase()

    def generate_undo_sequence(self, action_sequence):
        seq = []
        for action in action_sequence[::-1]:
            undo = self.undo_action(action)
            seq.append(undo)
            print('Action {} undone by: {}'.format(action, undo))
        return seq

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

    def prune_action(self, last_action, second_last_action):
        """
        This function prunes the moves that are redundant with the previous move.
        :param last_action:        str, last move made
        :param second_last_action: str, second last move made
        :return:
        """

        available_actions = self.actions.copy()
        if last_action == '':
            return available_actions
        # Removing the 2 to reduce conditions
        if '2' in last_action:
            last_action = last_action.replace('2', '')
        if '2' in second_last_action:
            second_last_action = second_last_action.replace('2', '')

        # Reducing branching factor to 15
        available_actions.remove(last_action.capitalize())
        available_actions.remove(last_action.lower())
        available_actions.remove(last_action.capitalize() + '2')

        if second_last_action == '':
            return available_actions
        elif self.opposite_face_actions[second_last_action.capitalize()] == last_action:
            # Reducing branching factor to 12
            available_actions.remove(second_last_action.capitalize())
            available_actions.remove(second_last_action.lower())
            available_actions.remove(second_last_action.capitalize() + '2')

        return available_actions

    def reset_cube(self):
        self.edge_position = np.arange(12)
        self.edge_rotation = np.zeros(12)
        self.corner_position = np.arange(8)
        self.corner_rotation = np.zeros(8)

    def show_cube_color(self):
        edge_colors = [self.edge_map[str(edge)] for edge in self.edge_position]
        corner_colors = [self.corner_map[str(corner)] for corner in self.corner_position]

        first_layer = [corner_colors[URF], edge_colors[UR], corner_colors[URB], edge_colors[UB], corner_colors[ULB],
                       edge_colors[UL], corner_colors[ULF], edge_colors[UF]]
        second_layer = [edge_colors[FR], edge_colors[BR],  edge_colors[BL], edge_colors[FL]]
        third_layer = [corner_colors[DRF], edge_colors[DR], corner_colors[DRB], edge_colors[DB], corner_colors[DLB],
                       edge_colors[DL], corner_colors[DLF], edge_colors[DF]]

        return first_layer, second_layer, third_layer

    def get_state(self):
        return self.corner_position, self.corner_rotation, self.edge_position, self.edge_rotation

    def is_solved(self):
        position_correct = np.all(self.corner_position == np.arange(8)) and np.all(self.edge_position == np.arange(12))
        orientation_correct = np.all(self.corner_rotation == np.zeros(8)) and np.all(self.edge_rotation == np.zeros(12))
        return position_correct, orientation_correct

    def display_state(self):
        print("Corner cubies: ", self.corner_position)
        print("Corner cubies rotations: ", self.corner_rotation)
        print("Edge cubies: ", self.edge_position)
        print("Edge cubies rotations: ", self.edge_rotation)

    def get_successors(self, last_move, second_last_move):
        """
        This function returns the successors of the current state.
        :param second_last_move: str, second last move made
        :param last_move:        str, last move made
        :return:                list, list of successors (RubiksCube objects)
        """
        successors = []
        available_actions = self.prune_action(last_action=last_move, second_last_action=second_last_move)
        for action in available_actions:
            cube_copy = deepcopy(self)
            cube_copy.twist(action)
            successors.append((action, cube_copy))
        return successors
