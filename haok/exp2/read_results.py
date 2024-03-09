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

def llm_call_cnts_fig(sample=10):
    react_file = f"result/exp2/res_sample_{sample}/react.jsonl"
    react_with_haok_file = f"result/exp2/res_sample_{sample}/react_with_haok.jsonl"

    def get_one_llm_call_cnts(filename):
        all_results = read_jsonl_file(filename)
        total_token_cnts = [result['llm_call_cnts'] for result in all_results]
        return total_token_cnts

    react_llm_call_cnts = get_one_llm_call_cnts(react_file)
    react_with_haok_call_cnts = get_one_llm_call_cnts(react_with_haok_file)

    # 绘制三条折线
    plt.plot(react_llm_call_cnts, label='ReAct')
    plt.plot(react_with_haok_call_cnts, label='ReAct-HAOK')

    # 添加图例
    plt.legend()

    # 添加x轴和y轴的标签
    plt.xlabel('任务编号', fontproperties=font, x=1)
    plt.ylabel('LLM调用次数', fontproperties=font, y=1)
    # plt.title('ReAct与ReAct-HAOK LLM调用次数对比', y=-0.18, fontproperties=font)


    # 显示图形
    plt.show()

def llm_call_cnts_fig_bar(sample=10):
    react_file = f"result/exp2/res_sample_{sample}/react.jsonl"
    react_with_haok_file = f"result/exp2/res_sample_{sample}/react_with_haok.jsonl"

    def get_one_llm_call_cnts(filename):
        all_results = read_jsonl_file(filename)
        total_token_cnts = [result['llm_call_cnts'] for result in all_results]
        return total_token_cnts

    react_llm_call_cnts = get_one_llm_call_cnts(react_file)
    react_with_haok_call_cnts = get_one_llm_call_cnts(react_with_haok_file)

    # 创建一个新的图形
    fig, ax = plt.subplots()

    # 设置柱状图的宽度
    bar_width = 0.35

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
    ax.set_title('ReAct与ReAct-HAOK LLM调用次数对比', fontproperties=font)

    # 设置x轴的刻度
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(range(1, len(react_llm_call_cnts) + 1))

    # 显示图形
    plt.show()


if __name__ == '__main__':
    llm_call_cnts_fig_bar(10)