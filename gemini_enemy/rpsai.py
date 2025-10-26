import random

class RPS:
    def __init__(self):
        self.choices = ['rock', 'paper', 'scissors']
        self.player_score = 0
        self.computer_score = 0
        self.game_finished = False
        self.rounds_played = 0
        self.max_rounds = 3
        self.last_result = None
        self.computer_choice = None
        
    def play(self, player_choice):
        if self.game_finished:
            return
        
        player_choice = player_choice.lower()
        if player_choice not in self.choices:
            return
        
        self.computer_choice = random.choice(self.choices)
        result = self.determine_winner(player_choice, self.computer_choice)
        self.rounds_played += 1
        
        if result == "player":
            self.player_score += 1
            self.last_result = f"You chose {player_choice}, Computer chose {self.computer_choice}. You win!"
        elif result == "computer":
            self.computer_score += 1
            self.last_result = f"You chose {player_choice}, Computer chose {self.computer_choice}. Computer wins!"
        else:
            self.last_result = f"You both chose {player_choice}. It's a tie!"
        
        print(self.last_result)
        print(f"Score - You: {self.player_score}, Computer: {self.computer_score}")
        
        if self.rounds_played >= self.max_rounds:
            self.game_finished = True
            self.announce_winner()
    
    def determine_winner(self, player, computer):
        if player == computer:
            return "tie"
        
        wins = {
            'rock': 'scissors',
            'scissors': 'paper',
            'paper': 'rock'
        }
        
        if wins[player] == computer:
            return "player"
        return "computer"
    
    def announce_winner(self):
        print("\n=== GAME OVER ===")
        if self.player_score > self.computer_score:
            print("You won the game!")
        elif self.computer_score > self.player_score:
            print("Computer won the game!")
        else:
            print("It's a tie game!")