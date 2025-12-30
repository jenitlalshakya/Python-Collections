import random
import os

# ---------- Utility Functions ----------

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(mat):
    clear_screen()
    print("\n2048 Game:\n")
    for row in mat:
        print('+----'*4 + '+')
        print(''.join(f'|{num:^4}' if num != 0 else '|    ' for num in row) + '|')
    print('+----'*4 + '+\n')

# ---------- Game Logic Functions ----------

def start_game():
    mat = [[0]*4 for _ in range(4)]
    add_new_2(mat)
    add_new_2(mat)
    return mat

def find_empty(mat):
    empty_cells = [(i,j) for i in range(4) for j in range(4) if mat[i][j]==0]
    return random.choice(empty_cells) if empty_cells else (None, None)

def add_new_2(mat):
    r, c = find_empty(mat)
    if r is not None:
        mat[r][c] = 4 if random.random() < 0.1 else 2

def get_current_state(mat):
    for row in mat:
        if 2048 in row:
            return 'WON'

    for row in mat:
        if 0 in row:
            return 'GAME NOT OVER'

    for i in range(4):
        for j in range(3):
            if mat[i][j] == mat[i][j+1] or mat[j][i] == mat[j+1][i]:
                return 'GAME NOT OVER'

    return 'LOST'

# ---------- Movement Functions ----------

def compress(mat):
    changed = False
    new_mat = [[0]*4 for _ in range(4)]
    for i in range(4):
        pos = 0
        for j in range(4):
            if mat[i][j] != 0:
                new_mat[i][pos] = mat[i][j]
                if j != pos:
                    changed = True
                pos += 1
    return new_mat, changed

def merge(mat):
    changed = False
    for i in range(4):
        for j in range(3):
            if mat[i][j] == mat[i][j+1] and mat[i][j] != 0:
                mat[i][j] *= 2
                mat[i][j+1] = 0
                changed = True
    return mat, changed

def reverse(mat):
    return [row[::-1] for row in mat]

def transpose(mat):
    return [list(row) for row in zip(*mat)]

def move_left(mat):
    new_mat, changed1 = compress(mat)
    new_mat, changed2 = merge(new_mat)
    changed = changed1 or changed2
    new_mat, _ = compress(new_mat)
    return new_mat, changed

def move_right(mat):
    new_mat = reverse(mat)
    new_mat, changed = move_left(new_mat)
    new_mat = reverse(new_mat)
    return new_mat, changed

def move_up(mat):
    new_mat = transpose(mat)
    new_mat, changed = move_left(new_mat)
    new_mat = transpose(new_mat)
    return new_mat, changed

def move_down(mat):
    new_mat = transpose(mat)
    new_mat, changed = move_right(new_mat)
    new_mat = transpose(new_mat)
    return new_mat, changed

# ---------- Main Game Loop ----------

def play_game():
    mat = start_game()

    while True:
        print_board(mat)
        status = get_current_state(mat)
        if status == 'WON':
            print("🎉 Congratulations! You reached 2048!")
            break
        elif status == 'LOST':
            print("💀 Game Over! No moves left.")
            break

        move = input("Enter move (W/A/S/D): ").lower()
        if move == 'w':
            mat, changed = move_up(mat)
        elif move == 's':
            mat, changed = move_down(mat)
        elif move == 'a':
            mat, changed = move_left(mat)
        elif move == 'd':
            mat, changed = move_right(mat)
        else:
            print("Invalid move! Use W/A/S/D only.")
            continue

        if changed:
            add_new_2(mat)

if __name__ == "__main__":
    play_game()
