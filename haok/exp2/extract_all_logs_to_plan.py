import os

from haok.exp2.plan_extract_agent import plan_extract_agent
from haok.exp2.plan_store import default_plan_store

def get_all_logs(logs_dir):
    all_logs = []

    # 获取目录下的所有文件
    for filename in os.listdir(logs_dir):
        # 检查文件是否是日志文件
        if filename.endswith('.log'):
            # 获取文件的完整路径
            file_path = os.path.join(logs_dir, filename)

            # 打开文件并读取内容
            with open(file_path, 'r') as file:
                content = file.read()

            # 将内容添加到列表中
            all_logs.append(content)

    return all_logs

def extract_all_logs_to_plan(all_logs, skip_index=0):
    for i, log in enumerate(all_logs, start=1):
        if i <= skip_index:
            continue
        print(f'开始处理第{i}个日志文件')
        plans = plan_extract_agent(log)
        default_plan_store.add_batch(plans)
        print(f'第{i}个日志文件处理完成')

if __name__ == '__main__':
    sample = 30
    logs_dir = f"result/exp2/logs_sample_{sample}/react"
    all_logs = get_all_logs(logs_dir)
    # 跳过前面的日志，用于断点续传
    # 如果前面输出第i个日志文件处理完成，那么skip_index=i
    skip_index = 0
    if skip_index > 0:
        print(f'跳过前{skip_index}个日志文件')
    extract_all_logs_to_plan(all_logs, skip_index=skip_index)
