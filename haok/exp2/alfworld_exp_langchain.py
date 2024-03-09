import os
import openai
import yaml
import alfworld
import alfworld.agents.environment
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough

import haok.exp2.prompts.alfworld
from haok.config.settings import get_settings
from openai import OpenAI
import json

from haok.llm.openai import OpenAIConfig

client = OpenAI(
    api_key=get_settings().llm.api_key,
    base_url=get_settings().llm.api_base
)

with open('base_config.yaml') as reader:
    config = yaml.safe_load(reader)

split = "eval_out_of_distribution"

env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
env = env.init_env(batch_size=1)

d = haok.exp2.prompts.alfworld.d

def chat(prompt, model="gpt-3.5-turbo-0125", stop=None):
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

# def get_few_shot_template(task_prefix, examples):
#     example_prompt = PromptTemplate(
#         input_variables=["example"], template="{example}"
#     )
#     prompt = FewShotPromptTemplate(
#         examples=examples,
#         example_prompt=example_prompt,
#         suffix="Question: " + task_prefix + "{input}",
#         input_variables=["input"],
#     )
#     output_parser = StrOutputParser()
#     llm = OpenAIConfig.defaultLLM()
#     chain = (
#             {"input": RunnablePassthrough()}
#             | prompt
#             | llm
#             | output_parser
#     )

def process_ob(ob):
    if ob.startswith('You arrive at loc '):
        ob = ob[ob.find('. ') + 2:]
    return ob

import sys

def alfworld_run(prompt, to_print=True, ob=''):
    init_prompt = prompt + ob + '\n>'
    prompt = ''
    if to_print:
        print(ob)
        sys.stdout.flush()
    for i in range(1, 31):
        action = chat(init_prompt + prompt, stop=['\n']).strip()
        observation, reward, done, info = env.step([action])
        observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
        # admissible_commands = info['admissible_commands'][0]
        if action.startswith('think:'):
            observation = 'OK.'
        if to_print:
            print(f'Act {i}: {action}\nObs {i}: {observation}')
            # print(f'Act {i}: {action}\nObs {i}: {observation}, admissible commands: {admissible_commands}')
            sys.stdout.flush()
        prompt += f' {action}\n{observation}\n>'
        # prompt += f' {action}\n{observation}\nadmissible_commands:{admissible_commands}\n>'
        if done:
            return reward, i
    return 0, i

def chat2(system_prompt, examples, prompt, model="gpt-3.5-turbo-0125", stop=None):
    if stop is None:
        stop = ["\n"]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": examples},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        stop=stop,
    )
    return response.choices[0].message.content

def alfworld_run2(system_prompt, examples, prompt, to_print=True, ob=''):
    init_prompt = prompt + ob + '\n>'
    prompt = ''
    if to_print:
        print(ob)
        sys.stdout.flush()
    for i in range(1, 31):
        action = chat2(system_prompt, examples,init_prompt + prompt, stop=['\n']).strip()
        observation, reward, done, info = env.step([action])
        observation, reward, done = process_ob(observation[0]), info['won'][0], done[0]
        # admissible_commands = info['admissible_commands'][0]
        if action.startswith('think:'):
            observation = 'OK.'
        if to_print:
            print(f'Act {i}: {action}\nObs {i}: {observation}')
            # print(f'Act {i}: {action}\nObs {i}: {observation}, admissible commands: {admissible_commands}')
            sys.stdout.flush()
        prompt += f' {action}\n{observation}\n>'
        # prompt += f' {action}\n{observation}\nadmissible_commands:{admissible_commands}\n>'
        if done:
            return reward, i
    return 0, i

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

# for _ in range(134):
for _ in range(5):
    ob, info = env.reset()  # info 中包含了 won (list，布尔值）、'admissible_commands'（二级list，可行指令）、任务文件信息
    ob = '\n'.join(ob[0].split('\n\n')[1:]) # ob是任务描述，最后一行格式是 "Your task is to: put a clean spatula in drawer."
    name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1]) # 获得任务名前缀，判断是什么类型任务
    print(name)
    for i, (k, v) in enumerate(prefixes.items()):
        if name.startswith(k):
            experience_str = """If you want to "Find and take a tomato", maybe you can:
- go to countertop 1
- take tomato 1 from countertop 1

If you want to "Cool the tomato", maybe you can:
- go to fridge 1
- cool tomato 1 with fridge 1

If you want to "Put the cool tomato in the microwave", maybe you can:
- go to microwave 1
- open microwave 1
- put tomato 1 in/on microwave 1"""
            task_prefix = 'Interact with a household to solve a task.'
            note = 'Note: "put in" is invalid, you should use "put in/on". '
            examples = 'Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + '\n'
            experience = f'\nHere are some experience you can refer: {experience_str}\n'
            task_begin = 'Here is the task.\n'
            prompt = task_prefix + note + experience + experience + task_begin
            # prompt = 'Interact with a household to solve a task. Note: "put in" is invalid, you should use "put in/on". Here are two examples.\n' + d[f'react_{v}_1'] + d[f'react_{v}_0'] + '\nHere is the task.\n'
            print(k, v)
            # r, llm_call_cnt = alfworld_run(prompt, ob=ob)
            r, llm_call_cnt = alfworld_run2(task_prefix+note+examples, experience, task_begin, ob=ob)
            success_info.append(r)
            llm_call_cnts.append(llm_call_cnt)
            rs[i] += r
            cnts[i] += 1
            break
    print(_+1, 'r', r, 'rs', rs, 'cnts', cnts, 'sum(rs)/sum(cnts)', sum(rs) / sum(cnts))
    print('------------\n')

print(success_info)
print(llm_call_cnts)