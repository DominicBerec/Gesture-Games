import random

def check_winner(b):
    """Check if there's a winner on the board"""
    # Check rows
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != ' ':
            return b[i][0]
    # Check columns
    for i in range(3):
        if b[0][i] == b[1][i] == b[2][i] != ' ':
            return b[0][i]
    # Check diagonals
    if b[0][0] == b[1][1] == b[2][2] != ' ':
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != ' ':
        return b[0][2]
    return None

def is_board_full(board):
    """Check if the board is full (tie condition)"""
    return all(board[i][j] != ' ' for i in range(3) for j in range(3))

def call_tt(board):
    """Instant AI move using minimax algorithm (Hard difficulty)"""
   
    def minimax(b, is_maximizing):
        winner = check_winner(b)
        if winner == 'X':
            return 1
        if winner == 'O':
            return -1
        if is_board_full(b):
            return 0
       
        if is_maximizing:
            best_score = -float('inf')
            for i in range(3):
                for j in range(3):
                    if b[i][j] == ' ':
                        b[i][j] = 'X'
                        score = minimax(b, False)
                        b[i][j] = ' '
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if b[i][j] == ' ':
                        b[i][j] = 'O'
                        score = minimax(b, True)
                        b[i][j] = ' '
                        best_score = min(score, best_score)
            return best_score
   
    # Find best move for X
    best_score = -float('inf')
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'X'
                score = minimax(board, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
   
    return best_move

def easy_tt_random(board):
    """Easy AI move by selecting a random available square"""
    available_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == ' ']
    return random.choice(available_moves) if available_moves else None

def medium_tt(board):
    """Medium AI move: block opponent's winning move or pick random"""
    # Check if O can win next move, block it
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                if check_winner(board) == 'O':
                    board[i][j] = ' '
                    return (i, j)
                board[i][j] = ' '
    
    # Check if X can win next move, take it
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'X'
                if check_winner(board) == 'X':
                    board[i][j] = ' '
                    return (i, j)
                board[i][j] = ' '
    
    # Otherwise, pick random
    return easy_tt_random(board)