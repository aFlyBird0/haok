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

def extract_all_logs_to_plan(all_logs):
    for log in all_logs:
        plans = plan_extract_agent(log)
        default_plan_store.add_batch(plans)

if __name__ == '__main__':
    logs_dir = "result/exp2/logs/react"
    all_logs = get_all_logs(logs_dir)
    extract_all_logs_to_plan(all_logs)
