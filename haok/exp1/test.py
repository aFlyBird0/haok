def complete_sequence(sequence):
    stack = []
    mapping = {']': '[', ')': '(', '}': '{', '>': '<'}
    for char in sequence:
        if char in mapping.values():
            stack.append(char)
        elif char in mapping.keys():
            if not stack or mapping[char] != stack.pop():
                return mapping[char] + ' ' + char
    if stack:
        print(stack)
        return ' '.join([mapping[char] for char in stack])
    return ''

def add_print_to_last_line(input_str):
    lines = input_str.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():  # 找到最后一个非空行
            if not lines[i].lstrip().startswith('print'):
                first_non_whitespace_index = len(lines[i]) - len(lines[i].lstrip())
                lines[i] = lines[i][:first_non_whitespace_index] + f"print({lines[i].rstrip()[first_non_whitespace_index:]})"
            break
    return '\n'.join(lines)

code = """from itertools import permutations

# Define the initial ball colors
initial_balls = {'Alice': 'orange', 'Bob': 'white', 'Claire': 'purple'}

# Define the ball swaps
swaps = [('Bob', 'Claire'), ('Alice', 'Bob'), ('Claire', 'Bob')]

# Generate all possible permutations of swaps
perm = permutations(swaps)

# Iterate through each permutation to find the final ball color for Alice
for p in perm:
    balls = initial_balls.copy()
    for swap in p:
        balls[swap[0]], balls[swap[1]] = balls[swap[1]], balls[swap[0]]
    if balls['Alice'] == 'green':
        result = balls['Alice']
        break
    result"""

if __name__ == '__main__':


    # sequence = '( ( { ( < > )'
    # result = complete_sequence(sequence)
    # print(result)
    print(add_print_to_last_line(code))


def track_ball_swaps(alice_initial_color, bob_initial_color, claire_initial_color, dave_initial_color, swaps_sequence,
                     target_player):
    initial_ball_colors = {'Alice': alice_initial_color, 'Bob': bob_initial_color, 'Claire': claire_initial_color,
                           'Dave': dave_initial_color}
    # Perform the swaps
    for swap in swaps_sequence:
        initial_ball_colors[swap[0]], initial_ball_colors[swap[1]] = initial_ball_colors[swap[1]], initial_ball_colors[
            swap[0]]

    # Get the color of the ball the target player has at the end
    final_ball_color = initial_ball_colors[target_player]
    return final_ball_color
print(track_ball_swaps(alice_initial_color, bob_initial_color, claire_initial_color, dave_initial_color, swaps_sequence, target_player) + ' ball.')

# Example of calling the function
# target_player = 'Alice'

if __name__ == '__main__':
    swaps_sequence = [('Alice', 'Dave'), ('Claire', 'Dave'), ('Alice', 'Bob'), ('Dave', 'Claire'), ('Alice', 'Claire')]
    alice_initial_color = 'pink'
    bob_initial_color =  'white'
    claire_initial_color = 'red'
    dave_initial_color = 'purple'
    # swaps_sequence = [['Alice', 'Dave'], ['Claire', 'Eve'], ['Alice', 'Bob'], ['Dave', 'Claire'], ['Alice', 'Claire']]
    target_player = 'Alice'
    print(track_ball_swaps(alice_initial_color, bob_initial_color, claire_initial_color, dave_initial_color, swaps_sequence, target_player) + ' ball.')

