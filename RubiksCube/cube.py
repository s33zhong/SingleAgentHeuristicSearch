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

    def reset(self):
        """
        Input: None
        Description: Reset the cube to its inital state
        Output: None
        """
        self.current_state = [[[c for x in range(self.n)] for y in range(self.n)] for c in self.colours]

    def solved(self):
        """
        Input: None
        Description: Determine if the cube is solved or not
        Output: boolean representing if the cube is solved or not
        """
        for side in self.current_state:
            hold = []
            check = True
            for row in side:
                if len(set(row)) == 1:
                    hold.append(row[0])
                else:
                    check = False
                    break
            if check == False:
                break
            if len(set(hold)) > 1:
                check = False
                break
        return check

    def stringify(self):
        """
        Input: None
        Description: Create string representation of the current state of the cube
        Output: string representing the cube current state
        """
        return ''.join([i for r in self.current_state for s in r for i in s])

    def shuffle(self, l_rot = 5, u_rot = 100):
        """
        Input: l_rot - integer representing the lower bounds of amount of moves (Default = 5) [OPTIONAL]
               u_rot - integer representing the upper bounds of amount of moves (Default = 100) [OPTIONAL]
        Description: Shuffles rubiks' cube to random solvable state
        Output: None
        """
        moves = randint(l_rot, u_rot)
        actions = [
            ('h', 0),
            ('h', 1),
            ('v', 0),
            ('v', 1),
            ('s', 0),
            ('s', 1)
        ]
        for i in range(moves):
            a = choice(actions)
            j = randint(0, self.n - 1)
            if a[0] == 'h':
                self.horizontal_twist(j, a[1])
            elif a[0] == 'v':
                self.vertical_twist(j, a[1])
            elif a[0] == 's':
                self.side_twist(j, a[1])

    def show(self):
        """
        Input: None
        Description: Show the rubiks cube
        Output: None
        """
        spacing = f'{" " * (len(str(self.current_state[0][0])) + 2)}'
        l1 = '\n'.join(spacing + str(c) for c in self.current_state[0])
        l2 = '\n'.join('  '.join(str(self.current_state[i][j]) for i in range(1, 5)) for j in range(len(self.current_state[0])))
        l3 = '\n'.join(spacing + str(c) for c in self.current_state[5])
        print(f'{l1}\n\n{l2}\n\n{l3}')

    def horizontal_twist(self, row, direction):
        """
        Input: row - integer representing which row you would like to twist
               direction - boolean representing if you want to twist right or left [left - 0, right - 1]
        Description: Twist desired row of rubiks cube
        Output: None
        """
        if row < len(self.current_state[0]):
            if direction == 0: #Twist left
                self.current_state[1][row], self.current_state[2][row], self.current_state[3][row], self.current_state[4][row] = (self.current_state[2][row],
                                                                                                                                  self.current_state[3][row],
                                                                                                                                  self.current_state[4][row],
                                                                                                                                  self.current_state[1][row])

            elif direction == 1: #Twist right
                self.current_state[1][row], self.current_state[2][row], self.current_state[3][row], self.current_state[4][row] = (self.current_state[4][row],
                                                                                                                                  self.current_state[1][row],
                                                                                                                                  self.current_state[2][row],
                                                                                                                                  self.current_state[3][row])
            else:
                print(f'ERROR - direction must be 0 (left) or 1 (right)')
                return
            #Rotating connected face
            if direction == 0: #Twist left
                if row == 0:
                    self.current_state[0] = [list(x) for x in zip(*reversed(self.current_state[0]))] #Transpose top
                elif row == len(self.current_state[0]) - 1:
                    self.current_state[5] = [list(x) for x in zip(*reversed(self.current_state[5]))] #Transpose bottom
            elif direction == 1: #Twist right
                if row == 0:
                    self.current_state[0] = [list(x) for x in zip(*self.current_state[0])][::-1] #Transpose top
                elif row == len(self.current_state[0]) - 1:
                    self.current_state[5] = [list(x) for x in zip(*self.current_state[5])][::-1] #Transpose bottom
        else:
            print(f'ERROR - desired row outside of rubiks cube range. Please select a row between 0-{len(self.current_state[0]) - 1}')
            return

    def vertical_twist(self, column, direction):
        """
        Input: column - integer representing which column you would like to twist
               direction - boolean representing if you want to twist up or down [down - 0, up - 1]
        Description: Twist desired column of rubiks cube
        Output: None
        """
        if column < len(self.current_state[0]):
            for i in range(len(self.current_state[0])):
                if direction == 0: #Twist down
                    self.current_state[0][i][column], self.current_state[2][i][column], self.current_state[4][-i - 1][-column - 1], self.current_state[5][i][column] = (self.current_state[4][-i - 1][-column - 1],
                                                                                                                                                                        self.current_state[0][i][column],
                                                                                                                                                                        self.current_state[5][i][column],
                                                                                                                                                                        self.current_state[2][i][column])
                elif direction == 1: #Twist up
                    self.current_state[0][i][column], self.current_state[2][i][column], self.current_state[4][-i - 1][-column - 1], self.current_state[5][i][column] = (self.current_state[2][i][column],
                                                                                                                                                                        self.current_state[5][i][column],
                                                                                                                                                                        self.current_state[0][i][column],
                                                                                                                                                                        self.current_state[4][-i - 1][-column - 1])
                else:
                    print(f'ERROR - direction must be 0 (down) or 1 (up)')
                    return
            #Rotating connected face
            if direction == 0: #Twist down
                if column == 0:
                    self.current_state[1] = [list(x) for x in zip(*self.current_state[1])][::-1] #Transpose left
                elif column == len(self.current_state[0]) - 1:
                    self.current_state[3] = [list(x) for x in zip(*self.current_state[3])][::-1] #Transpose right
            elif direction == 1: #Twist up
                if column == 0:
                    self.current_state[1] = [list(x) for x in zip(*reversed(self.current_state[1]))] #Transpose left
                elif column == len(self.current_state[0]) - 1:
                    self.current_state[3] = [list(x) for x in zip(*reversed(self.current_state[3]))] #Transpose right
        else:
            print(f'ERROR - desired column outside of rubiks cube range. Please select a column between 0-{len(self.current_state[0]) - 1}')
            return

    def side_twist(self, column, direction):
        """
        Input: column - integer representing which column you would like to twist
               direction - boolean representing if you want to twist up or down [down - 0, up - 1]
        Description: Twist desired side column of rubiks cube
        Output: None
        """
        if column < len(self.current_state[0]):
            for i in range(len(self.current_state[0])):
                if direction == 0: #Twist down
                    self.current_state[0][column][i], self.current_state[1][-i - 1][column], self.current_state[3][i][-column - 1], self.current_state[5][-column - 1][-1 - i] = (self.current_state[3][i][-column - 1],
                                                                                                                                                                                  self.current_state[0][column][i],
                                                                                                                                                                                  self.current_state[5][-column - 1][-1 - i],
                                                                                                                                                                                  self.current_state[1][-i - 1][column])
                elif direction == 1: #Twist up
                    self.current_state[0][column][i], self.current_state[1][-i - 1][column], self.current_state[3][i][-column - 1], self.current_state[5][-column - 1][-1 - i] = (self.current_state[1][-i - 1][column],
                                                                                                                                                                                  self.current_state[5][-column - 1][-1 - i],
                                                                                                                                                                                  self.current_state[0][column][i],
                                                                                                                                                                                  self.current_state[3][i][-column - 1])
                else:
                    print(f'ERROR - direction must be 0 (down) or 1 (up)')
                    return
            #Rotating connected face
            if direction == 0: #Twist down
                if column == 0:
                    self.current_state[4] = [list(x) for x in zip(*reversed(self.current_state[4]))] #Transpose back
                elif column == len(self.current_state[0]) - 1:
                    self.current_state[2] = [list(x) for x in zip(*reversed(self.current_state[2]))] #Transpose top
            elif direction == 1: #Twist up
                if column == 0:
                    self.current_state[4] = [list(x) for x in zip(*self.current_state[4])][::-1] #Transpose back
                elif column == len(self.current_state[0]) - 1:
                    self.current_state[2] = [list(x) for x in zip(*self.current_state[2])][::-1] #Transpose top
        else:
            print(f'ERROR - desired column outside of rubiks cube range. Please select a column between 0-{len(self.current_state[0]) - 1}')
            return