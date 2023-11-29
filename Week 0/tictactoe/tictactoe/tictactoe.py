"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    noughts, crosses = 0, 0

    for row in board:
        for cell in row:
            if cell == "O":
                noughts += 1
            elif cell == "X":
                crosses += 1

    if noughts == crosses:
        return "X"
    else:
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    possible_moves = []
    
    for row in range(3):
        for cell in range(3):
            if board[row][cell] == None:
                possible_moves.append((row, cell))

    return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    test_board = copy.deepcopy(board)

    if player(board) == "X":
        test_board[action[0]][action[1]] = "X"
        return test_board
    else:
        test_board[action[0]][action[1]] = "O"
        return test_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    left, centre, right = True, True, True
    left_value, centre_value, right_value = None, None, None
    
    for row in range(len(board)):
        # Checks the rows for winners
        if board[row][0] == "X" and board[row][1] == "X" and board[row][2] == "X":
            return "X"
        elif board[row][0] == "O" and board[row][1] == "O" and board[row][2] == "O":
            return "O"
        
        # Checks the columns for winners
        if left == True:
            if board[row][0] == None:
                left = False
            elif left_value == None or left_value == board[row][0]:
                left_value = board[row][0]
            else:
                left = False
        if centre == True:
            if board[row][1] == None:
                centre = False
            elif centre_value == None or centre_value == board[row][1]:
                centre_value = board[row][1]
            else:
                centre = False
        if right == True:
            if board[row][2] == None:
                right = False
            elif right_value == None or right_value == board[row][2]:
                right_value = board[row][2]
            else:
                right = False

    # Checks the diagonals for winners
    if board[1][1] in ["X", "O"]:
        central_value = board[1][1]

        if board[0][0] == central_value and board[2][2] == central_value:
            return central_value
        elif board[0][2] == central_value and board[2][0] == central_value:
            return central_value

    # Returns a value if column checks return a winner
    if left == True:
        return left_value
    elif centre == True:
        return centre_value
    elif right == True:
        return right_value

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) in ["X", "O"]:
        return True
    else:
        for row in board:
            for cell in row:
                print(cell)
                if cell == None:
                    return False
                
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    result = winner(board)
    if result == "X":
        return 1
    elif result == "O":
        return -1
    else:
        return 0


def optimal_value(board):
    """
    Returns the optimal action value
    """

    # Finds which players turn it is and sets up a best move value which always improves
    active_player = player(board)
    if active_player == "X":
        best_move_value = -2
    else:
        best_move_value = 2

    # Iterates through possible actions to find the optimal one
    for move in actions(board):
        new_board = result(board, move)
        
        # If the game hasn't ended recursion is used to find future moves values for optimal play
        if terminal(new_board) == False:
            move_value = optimal_value(new_board)
        else:
            move_value = utility(new_board)

        # Sets the best move value according to the player who's turn it is
        if active_player == "X" and move_value > best_move_value:
            best_move_value = move_value
            if best_move_value == 1:
                return 1
        elif active_player == "O" and move_value < best_move_value:
            best_move_value = move_value
            if best_move_value == -1:
                return -1
            
    return best_move_value



def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    active_player = player(board)
    best_move = None
    if active_player == "X":
        best_move_value = -2
    else:
        best_move_value = 2

    # Iterates through possible actions to find the optimal one
    for move in actions(board):
        new_board = result(board, move)
        
        # If the game hasn't ended recursion is used to find future moves values for optimal play
        if terminal(new_board) == False:
            move_value = optimal_value(new_board)
        else:
            move_value = utility(new_board)

        # Sets the best move value according to the player who's turn it is
        if active_player == "X" and move_value > best_move_value:
            best_move_value = move_value
            best_move = move
            if best_move_value == 1:
                return best_move
        elif active_player == "O" and move_value < best_move_value:
            best_move_value = move_value
            best_move = move
            if best_move_value == -1:
                return best_move
            
    return best_move
