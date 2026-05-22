import os
import time
import random

board = [" " for _ in range(9)]

def clear():
    os.system("clear")

def reset_board():
    global board
    board = [" " for _ in range(9)]

def print_board():
    print(f"""
     {board[0]} | {board[1]} | {board[2]}
    ---+---+---
     {board[3]} | {board[4]} | {board[5]}
    ---+---+---
     {board[6]} | {board[7]} | {board[8]}
    """)

def funny_message(msg_type):
    messages = {
        "p1_win": ["Player 1 wins!", "P1 domination!", "P2 got destroyed"],
        "p2_win": ["Player 2 wins!", "P2 domination!", "P1 got destroyed"],
        "Robot win": ["AI wins!", "Told you!", "You lost bro"],
        "Manushyan win": ["You beat AI?!", "Respect!", "Suspicious skills"],
        "draw": ["It's a draw", "Nobody wins", " Meh"],
        "invalid": ["Spot taken!", "Try again", "Invalid move"]
    }
    print(random.choice(messages[msg_type]))

def check_winner(player):
    combos = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    return any(all(board[i] == player for i in combo) for combo in combos)

def is_full():
    return " " not in board

# 🔥 MINIMAX AI
def minimax(is_max):
    if check_winner("O"):
        return 1
    if check_winner("X"):
        return -1
    if is_full():
        return 0

    if is_max:
        best = -float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"
                score = minimax(False)
                board[i] = " "
                best = max(best, score)
        return best
    else:
        best = float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = "X"
                score = minimax(True)
                board[i] = " "
                best = min(best, score)
        return best

def ai_move():
    print("\n🤖 Thinking...")
    time.sleep(1)

    best_score = -float("inf")
    move = 0

    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            score = minimax(False)
            board[i] = " "
            if score > best_score:
                best_score = score
                move = i

    board[move] = "O"

def player_move(symbol):
    while True:
        try:
            move = int(input(f"Player {symbol} move (1-9): ")) - 1
            if 0 <= move < 9 and board[move] == " ":
                board[move] = symbol
                break
            else:
                funny_message("invalid")
        except:
            print("Enter 1-9 😅")

# 👥 PLAYER vs PLAYER
def two_player():
    reset_board()
    while True:
        clear()
        print("Player vs Player\n")
        print_board()

        player_move("X")
        if check_winner("X"):
            clear(); print_board(); funny_message("p1_win"); break
        if is_full():
            clear(); print_board(); funny_message("draw"); break

        clear()
        print_board()

        player_move("O")
        if check_winner("O"):
            clear(); print_board(); funny_message("p2_win"); break
        if is_full():
            clear(); print_board(); funny_message("draw"); break

# 🤖 PLAYER vs AI
def vs_ai():
    reset_board()
    while True:
        clear()
        print(" MANUSHYAN vs ROBOT\n")
        print_board()

        player_move("X")
        if check_winner("X"):
            clear(); print_board(); funny_message("Manushyan win"); break
        if is_full():
            clear(); print_board(); funny_message("draw"); break

        ai_move()
        if check_winner("O"):
            clear(); print_board(); funny_message("Robot win"); break
        if is_full():
            clear(); print_board(); funny_message("draw"); break


def main():
    while True:
        clear()
        print("""
ARRRREEEE YOOOOUUUUU RREEEAAAAADDDYYYYY!!!!!!
1. Player vs Player 
2. Player vs AI 
3. Exit 
""")
        choice = input("Enganeya kalikkande??? ")

        if choice == "1":
            two_player()
            input("\nEnter Nekkuka")
        elif choice == "2":
            vs_ai()
            input("\nEnter Nekkuka")
        elif choice == "3":
            print("Bye Bye")
            break
        else:
            print("Rethink myyy boyyy!!!")
            time.sleep(1)

main()