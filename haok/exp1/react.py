import json
from typing import List

from haok.base_agent.react import bare_react, react_with_haok
from haok.config.config import Database
from haok.base_agent.action_to_module import action_to_module, action_id_to_module
from haok.exp1.task import get_task, filter_samples


def step1(task_prefix, samples):
    for sample in samples:
        output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = bare_react(task_prefix + sample['question'])
        print(f'output: {output}, total_tokens_k: {total_tokens_k}, prompt_tokens_k: {prompt_tokens_k}, completion_tokens_k: {completion_tokens_k}')

    # for sample in samples:
    #     print(sample)


def step2(action_id):
    # 把 action 历史转变为模块
    action_id_to_module(action_id)

def step3(task_prefix, samples):
    # 再运行一次
    for sample in samples:
        output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = react_with_haok(task_prefix + sample['question'])
        print(f'output: {output}, total_tokens_k: {total_tokens_k}, prompt_tokens_k: {prompt_tokens_k}, completion_tokens_k: {completion_tokens_k}')


# task = "word_sorting"
task = "navigate"
# task = "tracking_shuffled_five_objects"
action_to_module_index = 1000   # 哪个作为module的例子
sample_length = 2  # 样本数
example_index = 500 # 哪个作为example的例子

if __name__ == '__main__':
    Database.module_collection = "exp1_module"
    Database.action_history_collection = "exp1_action_history"
    Database.plan_collection = "exp1_plan"

    task_prefix, all_samples = get_task(task)
    print(task_prefix)

    # 先执行一次，获得对应的action
    sample_module = all_samples[action_to_module_index]
    print(sample_module)
    output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = bare_react(task_prefix + sample_module['question'], save_action=True)
    print(f'output: {output}, total_tokens_k: {total_tokens_k}, prompt_tokens_k: {prompt_tokens_k}, completion_tokens_k: {completion_tokens_k}')


    samples = filter_samples(all_samples, sample_length)
    print('==================step1===================')
    step1(task_prefix, samples)

    print('==================step2================')
    action_id = '65e0979b05e1bb485699df24'
    step2(action_id)

    print('================step3====================')
    step3(task_prefix, samples)

