from haok.base_agent.action_to_module import action_to_module
from haok.history.action import ActionHistory

word_sorting_code = """words = 'stick gelatine'.split()
words.sort()
result = ' '.join(words)
print(result)"""
word_sorting_action_history = ActionHistory(
    tool = "python",
    tool_input= {
        "code": word_sorting_code,
        "dependencies": []
    },
    log = "Sort the following words alphabetically: Example:\n Question: stick gelatine\nAnswer: gelatine stick",
    task = "Sort the following words alphabetically:",
    result=""
)

navigate_code = """def return_to_start(instructions):
    x, y = 0, 0
    direction = 'N'
    for instruction in instructions:
        if instruction.startswith('Take'):
            steps = int(instruction.split()[1])
            if direction == 'N':
                y += steps
            elif direction == 'E':
                x += steps
            elif direction == 'S':
                y -= steps
            elif direction == 'W':
                x -= steps
        elif instruction == 'Turn right':
            if direction == 'N':
                direction = 'E'
            elif direction == 'E':
                direction = 'S'
            elif direction == 'S':
                direction = 'W'
            elif direction == 'W':
                direction = 'N'
        elif instruction == 'Turn around':
            if direction == 'N':
                direction = 'S'
            elif direction == 'E':
                direction = 'W'
            elif direction == 'S':
                direction = 'N'
            elif direction == 'W':
                direction = 'E'
    return x == 0 and y == 0

instructions = ['Take 7 steps', 'Turn around', 'Take 4 steps', 'Take 5 steps']
result = return_to_start(instructions)
print(result)"""
navigate_action_history = ActionHistory(
    tool = "python",
    tool_input={
        "code": navigate_code,
        "dependencies": [],
    },
    log = "If you follow these instructions, do you return to the starting point?Just Return True or False. Example:\nQuestion:Take 9 steps. Turn around. Take 6 steps. Turn right. Take 9 steps.\nAnswer: False",
    task="If you follow these instructions, do you return to the starting point?Just Return True or False.",
    result=""
)

dyck_languages_code = """def complete_sequence(s):
    # Mapping of opening and closing brackets
    brackets = {'(': ')', '[': ']', '{': '}', '<': '>'}
    stack = []
    for char in s:
        if char in brackets:
            stack.append(char)
        elif stack and char == brackets[stack[-1]]:
            stack.pop()
        else:
            # If the character is not an opening bracket or the correct closing bracket,
            # it's an invalid sequence, but we don't need to handle it as per instructions.
            pass
    # Complete the sequence by closing all open brackets
    completion = ''.join(brackets[open_bracket] for open_bracket in reversed(stack))
    return completion

sequence = '< { [ ( )'
completion = complete_sequence(sequence)
print(completion)"""

dyck_languages_action_history = ActionHistory(
    tool = 'python',
    tool_input={
        "code": dyck_languages_code,
        "dependencies": [],
    },
    log = 'You will receive a sequence, please complete it, making sure that the parentheses are closed properly. Do not judge whether the sequence is legal. The sequence can always be made valid through completion; you just need to find a way to complete it. Example:\nQuestion:( ( ) ) < [ ( { ( ) } )\nAnswer: ] >',
    task = 'You will receive a sequence, please complete it, making sure that the parentheses are closed properly. Do not judge whether the sequence is legal. The sequence can always be made valid through completion; you just need to find a way to complete it.',
    result=''
)

tracking_shuffled_five_objects_code = """# Initial ball colors for each player
players = {'Alice': 'pink', 'Bob': 'white', 'Claire': 'red', 'Dave': 'purple', 'Eve': 'yellow'}

# Sequence of swaps
swaps = [('Alice', 'Dave'), ('Claire', 'Eve'), ('Alice', 'Bob'), ('Dave', 'Claire'), ('Alice', 'Claire')]

# Perform the swaps
for swap in swaps:
    players[swap[0]], players[swap[1]] = players[swap[1]], players[swap[0]]

# Get the color of the ball Alice has at the end
alice_ball_color = players['Alice']
print(alice_ball_color+' ball.)"""
tracking_shuffled_five_objects_action_history = ActionHistory(
    tool = 'python',
    tool_input={
        'code': tracking_shuffled_five_objects_code,
        'dependencies': [],
    },
    log = 'Example:\n Question: Alice, Bob, Claire, Dave, and Eve are playing a game. At the start of the game, they are each holding a ball: Alice has a pink ball, Bob has a white ball, Claire has a red ball, Dave has a purple ball, and Eve has a yellow ball. As the game progresses, pairs of players trade balls. First, Alice and Dave swap balls. Then, Claire and Eve swap balls. Then, Alice and Bob swap balls. Then, Dave and Claire swap balls. Finally, Alice and Claire swap balls. At the end of the game, Alice has the \nAnswer: pink ball.',
    task = 'tracking shuffled balls.',
    result= ''
)

if __name__ == '__main__':
    action_histories = [dyck_languages_action_history]

    for action_history in action_histories:
        print(action_history)
        action_to_module(action_history)