from google import genai
from dotenv import load_dotenv
from utils import load_memory, write_memory

# Load environment variables from .env file
load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

memory_file = "memory.zip"

memory = []

print("Rock Paper Scissors")

load_memory(memory_file, memory)

memory.append("[Start of session]")
memory.append("System: System: This is a game of rock paper scissors. You will only be allowed to output one word with your choice, a new line, and who won the round, so two words in total, nothing else"
". while the game is ongoing. If the user wins output only 'User wins' if you win output 'System wins'. Accept creative choices by the user like 'gun' and plan a counterattack. Only output creative moves outside of the normal ones if the user already used a creative move. Accept when you lose to a creative move. Don't be biased and choose the incorrect move sometimes to let the user win at least a 40 percent of the time, more if they are clever. Reward the user for strategy by letting the user win more. Punish the user by not letting them win if they are repeating moves or being simple in the move choices.")

if len(memory) > 2:
    returning_prompt = "System: Previous memory was found. " \
    "Because previous memory was found, write a start of game message to the user referencing your memory, don't limit yourself to one word. Write an entire sentence. Try writing something that will get the player fired up."
    return_message = client.models.generate_content(
        model="gemini-2.5-flash", contents="\n".join(memory) + "\n" + returning_prompt
    )

    memory.append("Gemini: " + return_message.text)
    print("Gemini: " + return_message.text)

user_input = input("Enter your move: ")

while user_input != "exit":
    memory.append("User:" + user_input)

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="\n".join(memory)
    )

    print("Gemini: " + response.text)

    user_input = input("Enter your move: ")

write_memory(memory_file, memory)

def gemini_rps(move):
    client = genai.Client()

    memory_file = "memory.zip"

    memory = []

    load_memory(memory_file, memory)

    memory.append("[Start of session]")
    memory.append("System: System: This is a game of rock paper scissors. You will only be allowed to output one word with your choice, a new line, and who won the round, so two words in total, nothing else"
    ". while the game is ongoing. If the user wins output only 'User wins' if you win output 'System wins'. Accept creative choices by the user like 'gun' and plan a counterattack. Only output creative moves outside of the normal ones if the user already used a creative move. Accept when you lose to a creative move. Don't be biased and choose the incorrect move sometimes to let the user win at least a 40 percent of the time, more if they are clever. Reward the user for strategy by letting the user win more. Punish the user by not letting them win if they are repeating moves or being simple in the move choices.")

    memory.append("User:" + user_input)

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents="\n".join(memory)
    )

    write_memory(memory_file, memory)

    return response.text