import json

def transform_choice_to_answer(filename):
    # 读取JSON文件
    with open(filename, 'r') as file:
        data = json.load(file)

    # 调整examples的格式
    for example in data["examples"]:
        for key, value in example["target_scores"].items():
            if value == 1:
                example["target"] = key
                break

    # 将修改后的数据写回JSON文件
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# 把多选的值为1的结果挑出来，变成回答题
if __name__ == '__main__':
    # filename = 'tracking_shuffled_three_objects.json'
    # filename = 'navigate.json'
    filename = 'dyck_languages.json'
    transform_choice_to_answer(filename)
