import json


def read_jsonl_file(filename):
    results = []
    with open(filename, 'r') as infile:
        for line in infile:
            results.append(json.loads(line))
    return results

if __name__ == '__main__':
    tasks = ["word_sorting"]
    for task in tasks:
        # 读取成功结果文件
        file_prefix = f"result/exp1/cot_with_tool/{task}"
        all_results = read_jsonl_file(f'{file_prefix}.jsonl')
        # 读取失败结果文件
        error_results = read_jsonl_file(f'{file_prefix}_error.jsonl')

        import matplotlib.pyplot as plt

        # 成功率计算
        total_samples = len(all_results)
        error_count = len(error_results)
        success_count = len(all_results) - error_count
        success_rate = success_count / total_samples
        print(f'total samples: {total_samples}, success rate: {success_rate}')

        # 计算token消耗
        all_token_consumption = [result["total_tokens_k"] for result in all_results]
        prompt_token_consumption = [result["prompt_tokens_k"] for result in all_results]
        completion_token_consumption = [result["completion_tokens_k"] for result in all_results]
        print(all_token_consumption)
        print(prompt_token_consumption)
        print(completion_token_consumption)
        print()

        # # 绘制图表
        # fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        #
        # # 成功率柱状图
        # ax[0].bar(['Success', 'Error'], [success_count, error_count], color=['green', 'red'])
        # ax[0].set_title('Success Rate')
        # ax[0].set_ylabel('Number of Samples')
        #
        # # Token消耗箱线图
        # ax[1].boxplot([token_consumption], labels=['Success', 'Error'])
        # ax[1].set_title('Token Consumption')
        # ax[1].set_ylabel('Total Tokens (k)')
        #
        # plt.show()