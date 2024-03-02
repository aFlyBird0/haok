import json
from typing import List

from langchain_community.callbacks import get_openai_callback

from haok.base_agent.react import bare_react, react_with_haok
from haok.config.config import Database
from haok.base_agent.action_to_module import action_to_module, action_id_to_module
from haok.exp1.task import get_task, filter_samples
from haok.base_agent.cot_with_tool import CoT_with_tool

# task = "word_sorting" 完成
# task = "navigate" 完成
task = "tracking_shuffled_five_objects"
# task = "tracking_shuffled_three_objects"
# task = "dyck_languages" 完成
action_to_module_index = 1000   # 哪个作为module的例子
sample_length = 30  # 样本数
example_index = 500 # 哪个作为example的例子

def count_non_empty_lines(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            non_empty_lines = sum(1 for line in file if line.strip())
        return non_empty_lines
    except FileNotFoundError:
        return 0

if __name__ == '__main__':
    Database.module_collection = "exp1_module"
    Database.action_history_collection = "exp1_action_history"
    Database.plan_collection = "exp1_plan"

    task_prefix, example, all_samples = get_task(task)
    samples = filter_samples(all_samples, sample_length)

    res_file_prefix = f"result/exp1/cot_with_tool/{task}"
    all_file = f"{res_file_prefix}.jsonl"
    error_file = f"{res_file_prefix}_error.jsonl"

    # 计算已经完成的数量
    finished_nums = count_non_empty_lines(all_file)
    print(f'检测到已经完成{finished_nums}项，即将跳过')

    for sample in samples:
        # 跳过已经完成的案例
        if finished_nums > 0:
            finished_nums -= 1
            continue
        question, answer = sample["question"], sample["answer"]
        with get_openai_callback() as cb:
            output = CoT_with_tool(question, task_prefix, example)
        total_tokens_k = round(cb.total_tokens / 1000, 3)
        prompt_tokens_k = round(cb.prompt_tokens / 1000, 3)
        completion_tokens_k = round(cb.completion_tokens / 1000, 3)
        success = answer == output
        if task == "dyck_languages":
            success = str.replace(answer, ' ', '') == str.replace(output, ' ', '')
        if "tracking_shuffled" in task:
            success = output == answer or output + " ball." == answer or output + " present." == answer
        print(f'Success: {success}, Question: {question}', f'Output: {output}', f'Answer: {answer}')
        print(f'total_tokens_k: {total_tokens_k}k, prompt_tokens_k: {prompt_tokens_k}k, completion_tokens_k: {completion_tokens_k}k')
        # 构建结果字典
        result = {
            "question": question,
            "answer": answer,
            "output": output,
            "success": success,
            "total_tokens_k": total_tokens_k,
            "prompt_tokens_k": prompt_tokens_k,
            "completion_tokens_k": completion_tokens_k
        }

        # 保存结果，失败了就额外再存一下
        with open(all_file, 'a') as outfile:
            json.dump(result, outfile)
            outfile.write('\n')  # 写入换行符以便每个结果占一行
        if not success:
            with open(error_file, 'a') as outfile:
                json.dump(result, outfile)
                outfile.write('\n')  # 写入换行符以便每个结果占一行

    # 先执行一次，获得对应的action
    # sample_module = all_samples[action_to_module_index]
    # print(sample_module)
    # output, conversation, total_tokens_k, prompt_tokens_k, completion_tokens_k = bare_react(task_prefix + sample_module['question'], save_action=True)
    # print(f'output: {output}, total_tokens_k: {total_tokens_k}, prompt_tokens_k: {prompt_tokens_k}, completion_tokens_k: {completion_tokens_k}')
    #
    #
    # samples = filter_samples(all_samples, sample_length)
    # print('==================step1===================')
    # step1(task_prefix, samples)
    #
    # print('==================step2================')
    # action_id = '65e0979b05e1bb485699df24'
    # step2(action_id)
    #
    # print('================step3====================')
    # step3(task_prefix, samples)

