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
        self.current_player = 1
        self.game_over = False
    
    def mark_square(self, player, x, y):
            self.current_player = player
            self.board[x][y] = self.current_player
            
    def print_board(self):
        print(self.board[0])
        print(self.board[1])
        print(self.board[2])

'''
b = Board()
b.print_board()
'''