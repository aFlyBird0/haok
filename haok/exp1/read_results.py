import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.font_manager import FontProperties


def read_jsonl_file(filename):
    results = []
    with open(filename, 'r') as infile:
        for line in infile:
            results.append(json.loads(line))
    return results

font = FontProperties(fname=r'/System/Library/Fonts/PingFang.ttc', size=12)

def token_fig(task, token_type, ylabel, figure_name, model=''):
    few_shot_file = f"result/exp1/cot{model}/{task}.jsonl"
    few_shot_tool_file = f"result/exp1/cot_with_tool{model}/{task}.jsonl"
    few_shot_haok_file = f"result/exp1/cot_with_haok{model}/{task}.jsonl"

    def get_one_token_consume(filename):
        all_results = read_jsonl_file(filename)
        total_token_consumption = [result[token_type]*1000 for result in all_results]
        return total_token_consumption

    few_shot_tokens = get_one_token_consume(few_shot_file)
    few_shot_tool_tokens = get_one_token_consume(few_shot_tool_file)
    few_shot_haok_tokens = get_one_token_consume(few_shot_haok_file)

    # 创建一个新的figure
    # 创建一个新的figure，并设置其大小
    # 创建一个新的figure，并设置其大小
    # 创建一个新的figure，并设置其大小
    fig = plt.figure(figsize=(10, 5))

    # 使用GridSpec来创建一个4x1的网格
    gs = gridspec.GridSpec(6, 1, height_ratios=[1, 1, 1, 1, 1, 1])

    # 使用这个网格的上面四分之一来创建一个子图来显示每个数组的平均消耗
    ax1 = plt.subplot(gs[0])
    ax1.axis('off')
    # 计算每个数组的平均消耗
    avg_Few_Shot = np.mean(few_shot_tokens)
    avg_Few_Shot_Tool = np.mean(few_shot_tool_tokens)
    avg_Few_Shot_HAOK = np.mean(few_shot_haok_tokens)

    ax1.text(1, 1,
             'Few-Shot平均：{:.2f}\nFew-Shot-Tool平均：{:.2f}\nFew-Shot-HAOK平均：{:.2f}'.format(avg_Few_Shot,
                                                                                      avg_Few_Shot_Tool,
                                                                                      avg_Few_Shot_HAOK),
             fontproperties=font, verticalalignment='top', horizontalalignment='right', transform=plt.gca().transAxes,
             bbox=dict(facecolor='none', edgecolor='black'))





    # 使用这个网格的右边三分之一来创建另一个子图来显示每个数组的平均消耗
    ax2 = plt.subplot(gs[1:])
    # ax2.axis('off')
    # 绘制三条折线
    ax2.plot(few_shot_tokens, label='Few-Shot')
    ax2.plot(few_shot_tool_tokens, label='Few-Shot-Tool')
    ax2.plot(few_shot_haok_tokens, label='Few-Shot-HAOK')

    # 添加图例
    ax2.legend()

    # 添加x轴和y轴的标签
    ax2.set_xlabel('任务编号', fontproperties=font, x=1)
    ax2.set_ylabel('Token', fontproperties=font, y=1)
    ax2.set_title(figure_name, y=-0.18, fontproperties=font)


    # 显示图形
    plt.show()

def total_token_fig(task):
    return token_fig(task, "total_tokens_k", '总Token消耗', '(a) '+task+'——总Token消耗', '_gpt4')
def completion_token_fig(task):
    return token_fig(task, "completion_tokens_k", '输出（补全）Token消耗', '(b) '+task+'——输出（补全）Token消耗', '_gpt4')

if __name__ == '__main__':
    # task = "word_sorting"
    # tasks = ["word_sorting", "navigate"]
    tasks = ['dyck_languages', 'tracking_shuffled_five_objects']
    for task in tasks:
        total_token_fig(task)
        completion_token_fig(task)

    # tasks = ["word_sorting"]
    # for task in tasks:
    #     # 读取成功结果文件
    #     file_prefix = f"result/exp1/cot_with_tool/{task}"
    #     all_results = read_jsonl_file(f'{file_prefix}.jsonl')
    #     # 读取失败结果文件
    #     error_results = read_jsonl_file(f'{file_prefix}_error.jsonl')
    #
    #     import matplotlib.pyplot as plt
    #
    #     # 成功率计算
    #     total_samples = len(all_results)
    #     error_count = len(error_results)
    #     success_count = len(all_results) - error_count
    #     success_rate = success_count / total_samples
    #     print(f'total samples: {total_samples}, success rate: {success_rate}')
    #
    #     # 计算token消耗
    #     all_token_consumption = [result["total_tokens_k"] for result in all_results]
    #     prompt_token_consumption = [result["prompt_tokens_k"] for result in all_results]
    #     completion_token_consumption = [result["completion_tokens_k"] for result in all_results]
    #     print(all_token_consumption)
    #     print(prompt_token_consumption)
    #     print(completion_token_consumption)
    #     print()