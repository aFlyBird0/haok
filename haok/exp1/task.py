import json

from haok.base_agent.action_to_module import action_id_to_module


def transform_task_key(example):
    return {
        'question': example['input'],
        'answer': example['target'],
    }

def double_braces(input_str):
    return input_str.replace("{", "{{").replace("}", "}}")
def get_task(task: str):
    example_index = 500
    if "tracking_shuffled" in task:
        example_index = 50
    if task == "dyck_languages":
        example_index = 2
    samples = []
    with open(f"data/bigbench/{task}.json") as f:
        data = json.load(f)
        examples = data['examples']
        for index in range(len(examples)):
            example = examples[index]
            # 对于 navigate 任务，只用 turns 的
            if task == "navigate" and example["inst_type"] != "turns":
                continue
            samples.append(transform_task_key(example))
    example = samples[example_index]
    # 把 { 替换成 {{, 把 } 替换成 }}
    example['question'] = double_braces(example['question'])
    example['answer'] = double_braces(example['answer'])
    # 对打乱的这个做特殊处理
    if "tracking_shuffled" in task:
        samples = samples[:180]

    task_prefix = data.get('task_prefix', '')
    return task_prefix, example, samples

def filter_samples(samples, num):
    total = len(samples)
    step = total//num
    filtered_samples = []

    for index in range(total):
        if index % step == 0 and len(filtered_samples) < num:
            filtered_samples.append(samples[index])
    return filtered_samples

def task_prefix_with_example(task_prefix, sample):
    hint = f'{task_prefix}. Example: \n Input: {sample["question"]}, \n Output: {sample["answer"]}\n Input: '
    return hint