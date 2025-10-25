class Board():
    #Create 2D list to store board values: E, X, O
    #empty E,
    #Player X
    #Computer O
    def __init__(self):
        self.board = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' ']
        ]

        self.game_over = False
    
    def mark_square(self, player, row, col):
        if self.board[row][col] != ' ':
            return False

        self.board[row][col] = player
        if self.win_check():
            print(f"Player {player} wins!")
            self.game_over = True
        
        return True

    def win_check(self):
        #Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != ' ':
                self.game_over = True
                return self.board[row][0]
        #Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                self.game_over = True
                return self.board[0][col]
        #Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            self.game_over = True
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            self.game_over = True
            return self.board[0][2]
        return None
            
    def print_board(self):
        print(self.board[0])
        print(self.board[1])
        print(self.board[2])