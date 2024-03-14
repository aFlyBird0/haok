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

def llm_call_cnts_fig(sample=30):
    react_file = f"result/exp2/res_sample_{sample}/react.jsonl"
    react_with_haok_file = f"result/exp2/res_sample_{sample}/react_with_haok.jsonl"

    def get_one_llm_call_cnts(filename):
        all_results = read_jsonl_file(filename)
        total_token_cnts = [result['llm_call_cnts'] for result in all_results]
        return total_token_cnts

    react_llm_call_cnts = get_one_llm_call_cnts(react_file)
    react_with_haok_call_cnts = get_one_llm_call_cnts(react_with_haok_file)

    react_avg_llm_call_cnt = sum(react_llm_call_cnts) / len(react_llm_call_cnts)
    react_with_haok_avg_call_cnt = sum(react_with_haok_call_cnts) / len(react_with_haok_call_cnts)

    print(f'react_avg_llm_call_cnt: {react_avg_llm_call_cnt}, react_with_haok_call_cnt: {react_with_haok_avg_call_cnt}')

    # 绘制三条折线
    plt.plot(react_llm_call_cnts, label='ReAct')
    plt.plot(react_with_haok_call_cnts, label='ReAct-HAOK')

    # 添加图例
    plt.legend()

    # 添加x轴和y轴的标签
    plt.xlabel('任务编号', fontproperties=font, x=1)
    plt.ylabel('LLM调用次数', fontproperties=font, y=1)
    # plt.title('ReAct与ReAct-HAOK LLM调用次数对比', y=-0.18, fontproperties=font)
    plt.xticks(np.arange(0, len(react_llm_call_cnts), step=2))

    # 显示图形
    plt.show()


def success_rate_fig(sample=30):
    react_file = f"result/exp2/res_sample_{sample}/react.jsonl"
    react_with_haok_file = f"result/exp2/res_sample_{sample}/react_with_haok.jsonl"

    def get_success_num(filename):
        all_results = read_jsonl_file(filename)
        # success_info = [success['success'] for success in all_results]
        # return success_info

        success_num = 0
        for result in all_results:
            if result['success']:
                success_num += 1
        return success_num

    react_success_num = get_success_num(react_file)
    react_with_haok_success_num = get_success_num(react_with_haok_file)

    react_success_rate = react_success_num / sample * 100
    react_with_haok_success_rate = react_with_haok_success_num / sample * 100

    print(f'react_success_rate: {react_success_rate}, react_with_haok_success_rate: {react_with_haok_success_rate}')
def llm_call_cnts_fig_bar(sample=10):
    react_file = f"result/exp2/res_sample_{sample}/react.jsonl"
    react_with_haok_file = f"result/exp2/res_sample_{sample}/react_with_haok.jsonl"

    def get_one_llm_call_cnts(filename):
        all_results = read_jsonl_file(filename)
        total_token_cnts = [result['llm_call_cnts'] for result in all_results]
        return total_token_cnts

    react_llm_call_cnts = get_one_llm_call_cnts(react_file)
    react_with_haok_call_cnts = get_one_llm_call_cnts(react_with_haok_file)

    react_avg_llm_call_cnt = sum(react_llm_call_cnts) / len(react_llm_call_cnts)
    react_with_haok_avg_call_cnt = sum(react_with_haok_call_cnts) / len(react_with_haok_call_cnts)

    print(f'react_avg_llm_call_cnt: {react_avg_llm_call_cnt}, react_with_haok_call_cnt: {react_with_haok_avg_call_cnt}')

    # 创建一个新的图形
    fig, ax = plt.subplots()

    # 设置柱状图的宽度
    bar_width = 0.3

    # 创建一个索引数组，用于设定柱状图的位置
    index = np.arange(len(react_llm_call_cnts))

    # 绘制并列的柱状图
    ax.bar(index, react_llm_call_cnts, bar_width, label='ReAct')
    ax.bar(index + bar_width, react_with_haok_call_cnts, bar_width, label='ReAct-HAOK')

    # 添加图例
    ax.legend()

    # 添加x轴和y轴的标签
    ax.set_xlabel('任务编号', fontproperties=font)
    ax.set_ylabel('LLM调用次数', fontproperties=font)
    # ax.set_title('ReAct与ReAct-HAOK LLM调用次数对比', fontproperties=font)

    # 设置x轴的刻度
    if sample <= 10:
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(range(1, len(react_llm_call_cnts) + 1))
    elif sample >10 and sample <= 30:
        ax.set_xticks(index[1::2] + bar_width / 2)
        ax.set_xticklabels(range(2, len(react_llm_call_cnts) + 1)[::2])
    else:
        ax.set_xticks(index[4::5] + bar_width / 2)
        ax.set_xticklabels(range(5, len(react_llm_call_cnts) + 1)[::5])

    # 显示图形
    plt.show()


if __name__ == '__main__':
    sample = 60
    llm_call_cnts_fig_bar(sample)
    success_rate_fig(sample)