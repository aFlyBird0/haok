import os
import openai
import yaml
import alfworld
import alfworld.agents.environment

import haok.exp2.prompts.alfworld
from haok.config.settings import get_settings
from openai import OpenAI
from haok.exp2.plan_extract_agent import convert_json_to_string
from haok.exp2.plan_store import default_plan_store
import json

client = OpenAI(
    api_key=get_settings().llm.api_key,
    base_url=get_settings().llm.api_base
)

with open('base_config.yaml') as reader:
    config = yaml.safe_load(reader)

split = "eval_out_of_distribution"

env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
env = env.init_env(batch_size=1)

# folder = './data/prompts/'
# prompt_file = 'alfworld_3prompts.json'
# with open(folder + prompt_file, 'r') as f:
#     d = json.load(f)

d = haok.exp2.prompts.alfworld.d

def chat(prompt, model=get_settings().llm.default_model, stop=None):
    if stop is None:
        stop = ["\n"]
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        stop=stop,
    )
    return response.choices[0].message.content

def process_ob(ob):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ') + 2:]
    return ob

import sys

log_dir = "result/exp2/logs"
# 先跑 agent_type 等于 react 的，然后跑 extract_all_logs_to_plan.py，最后再跑 react_with_hoak
# agent_type = "react"
agent_type = "react_with_haok"
def alfworld_run(prompt, task_id, task_name, task_type, to_print=True, ob=''):
    task_name = task_name.replace("/", "_")
    log_file = f'{log_dir}/{agent_type}/{task_id}___{task_type}___{task_name}.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    def save_log(final_log):
        with open(log_file, 'w') as f:
            f.write(final_log)
    final_log = ""
    init_prompt = prompt + ob + '\n>'
    prompt = ''
    if to_print:
        print(ob)
        final_log += ob + "\n"
        sys.stdout.flush()
    for i in range(1, 31):
        action = chat(init_prompt + prompt, stop=['\n']).strip()
        observation, reward, done, info = env.step([action])
        observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
        # admissible_commands = info['admissible_commands'][0]
        if action.startswith('think:'):
            observation = 'OK.'
        if to_print:
            act_and_obs = f'Act {i}: {action}\nObs {i}: {observation}'
            print(act_and_obs)
            final_log += act_and_obs + '\n'
            # print(f'Act {i}: {action}\nObs {i}: {observation}, admissible commands: {admissible_commands}')
            sys.stdout.flush()
        prompt += f' {action}\n{observation}\n>'
        # prompt += f' {action}\n{observation}\nadmissible_commands:{admissible_commands}\n>'
        if done:
            final_log += "Result: Task Success!\n"
            save_log(final_log)
            return reward, i
    save_log(final_log)
    return False, i

prefixes = {
    'pick_and_place': 'put',
    'pick_clean_then_place': 'clean',
    'pick_heat_then_place': 'heat',
    'pick_cool_then_place': 'cool',
    'look_at_obj': 'examine',
    'pick_two_obj': 'puttwo'
}
cnts = [0] * 6  #总数，一共6个任务
rs = [0] * 6    #结果，一共6个任务
success_info = []
llm_call_cnts = []

res_file = f'result/exp2/res/{agent_type}.jsonl'


def write_res_file(task_id, task_type, task_name, success: bool, llm_call_cnts: int):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(res_file), exist_ok=True)

    # Create a dictionary with the task details
    task_details = {
        'task_id': task_id,
        'task_type': task_type,
        'task_name': task_name,
        'success': success,
        'llm_call_cnts': llm_call_cnts
    }

    # Write the dictionary to the jsonl file
    with open(res_file, 'a') as f:
        f.write(json.dumps(task_details) + '\n')

def count_non_empty_lines(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            non_empty_lines = sum(1 for line in file if line.strip())
        return non_empty_lines
    except FileNotFoundError:
        return 0

exisit_res_lines = count_non_empty_lines(file_name=res_file)
print(f'检测到已经完成{exisit_res_lines}项，即将跳过')


# ob是任务描述，最后一行格式是 "Your task is to: put a clean spatula in drawer."
# 提取得到 "put a clean spatula in drawer."
def extract_task_from_ob(s):
    # 找到最后一个冒号的位置
    last_colon_index = s.rfind(':')

    # 如果没有找到冒号，返回空字符串
    if last_colon_index == -1:
        return ''

    # 提取冒号后面的内容，注意我们需要跳过冒号和空格
    task = s[last_colon_index + 2:]

    return task


# for _ in range(134):
for _ in range(60):
    # 跳过已经存在的行数
    if exisit_res_lines > 0:
        exisit_res_lines -= 1
        continue
    ob, info = env.reset()  # info 中包含了 won (list，布尔值）、'admissible_commands'（二级list，可行指令）、任务文件信息
    ob = '\n'.join(ob[0].split('\n\n')[1:]) # ob是任务描述，最后一行格式是 "Your task is to: put a clean spatula in drawer."
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1]) # 获得任务名前缀，判断是什么类型任务
    print(name)
    for i, (k, v) in enumerate(prefixes.items()):
        if name.startswith(k):
            experience_str = """
If you want to put a cool tomato in microwave, maybe you can:
first, find and take a tomato, then cool it, at last put it in the microwave.

If you want to "find and take a tomato", maybe you can:
> go to countertop 2
> take tomato 1 from countertop 2

If you want to "cool the tomato", maybe you can:
> go to fridge 1
> cool tomato 1 with fridge 1

If you want to "put the cool tomato in the microwave", maybe you can:
> go to microwave 1
> open microwave 1
> put tomato 1 in/on microwave 1"""
            task_prefix = 'Interact with a household to solve a task.'
            note = 'Note: "put in" or "put on" is invalid, you must use "put in/on". '
            # note = ""
            examples = 'Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + '\n'
            experience = ""
            if agent_type == "react_with_haok":
                task = extract_task_from_ob(ob)
                experience_str = convert_json_to_string(default_plan_store.find_similar_module(task=task))
                experience = f'\nHere are some experience you can refer: {experience_str}\n'
            task_begin = 'Here is the task.\n'
            prompt = task_prefix + note + examples + experience + task_begin
            # prompt = 'Interact with a household to solve a task. Note: "put in" is invalid, you should use "put in/on". Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + f'\nHere are some experience you can refer: {experience}\nHere is the task.\n'
            # prompt = 'Interact with a household to solve a task. Note: "put in" is invalid, you should use "put in/on". Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + '\nHere is the task.\n'
            print(k, v)
            r, llm_call_cnt = alfworld_run(prompt, _, name, v, ob=ob)
            success_info.append(r)
            llm_call_cnts.append(llm_call_cnt)
            rs[i] += r
            cnts[i] += 1
            write_res_file(_, v, name, r, llm_call_cnt)
            break
    print(_+1, 'r', r, 'rs', rs, 'cnts', cnts, 'sum(rs)/sum(cnts)', sum(rs) / sum(cnts))
    print('------------\n')

print(success_info)
print(llm_call_cnts)