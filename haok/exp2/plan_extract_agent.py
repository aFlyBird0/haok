import json

from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from haok.llm.openai import OpenAIConfig


def plan_extract_agent(log):
    prompt = ChatPromptTemplate.from_template(
    """
    从下面的运行日志中提取出几个成功的子任务（你应该尽可能地将任务拆分为多个子任务），并且每个成功的子任务提取出对应的有效执行步骤。
    注意，并不是每个任务的所有操作都是有效的，例如Nothing happens，又比如去了好几个地方找某样东西，只有一个地方找到了，就只保留找到了东西的哪个操作。
    你的输出应该是一个json数组，形如[{{"task": "find and take a tomato", "steps": ["go to countertop 1", "take tomato 1 from countertop 1"]}}, ...]
    其中，步骤请输出Act后面的内容，例如"Act 3: open fridge 1"，请输出 "open fridge 1"
    用英文回答我。
    
    下面是运行日志：
    {input}
    """
)
    output_parser = JsonOutputParser()
    llm = OpenAIConfig.openai4()
    llm.bind(response_format={"type": "json_object"})
    chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | llm
            | output_parser
    )

    return chain.invoke(log)

def convert_json_to_string(json_data):
    result = ""
    for item in json_data:
        result += f'If you want to "{item["task"]}", maybe you can:\n'
        for step in item["steps"]:
            result += f'> {step}\n'
        result += '\n'
    return result

if __name__ == '__main__':
    log = """
    You are in the middle of a room. Looking quickly around you, you see a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
Your task is to: put a cool tomato in microwave.
Act 1: think: To solve the task, I need to find and take a tomato, then cool it with the fridge, and finally put it in the microwave.
Obs 1: OK.
Act 2: think: First, I need to find a tomato. A tomato is more likely to appear in countertop (1-3), fridge (1), shelf (1-3), cabinet (1-6), drawer (1-3). I can check one by one, starting with countertop 1.
Obs 2: OK.
Act 3: go to countertop 1
Obs 3: On the countertop 1, you see a peppershaker 2, and a tomato 1.
Act 4: take tomato 1 from countertop 1
Obs 4: You pick up the tomato 1 from the countertop 1.
Act 5: think: Now I have a tomato (1). Next, I need to cool it with the fridge (1).
Obs 5: OK.
Act 6: go to fridge 1
Obs 6: The fridge 1 is closed.
Act 7: cool tomato 1 with fridge 1
Obs 7: You cool the tomato 1 using the fridge 1.
Act 8: think: Now I have a cool tomato (1). Next, I need to put it in the microwave.
Obs 8: OK.
Act 9: go to microwave 1
Obs 9: The microwave 1 is closed.
Act 10: put tomato 1 in/on microwave 1
Obs 10: Nothing happens.
Act 11: open microwave 1
Obs 11: You open the microwave 1. The microwave 1 is open. In it, you see nothing.
Act 12: put tomato 1 in/on microwave 1
Obs 12: You put the tomato 1 in/on the microwave 1.
"""
    log2 = """You are in the middle of a room. Looking quickly around you, you see a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a shelf 3, a shelf 2, a shelf 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.
Your task is to: put a clean spatula in drawer.
Act 1: think: To solve the task, I need to find and take a spatula, then clean it with sinkbasin, then put it in a drawer.
Obs 1: OK.
Act 2: think: First I need to find a spatula. A spatula is more likely to appear in a drawer (1-3), sinkbasin (1), countertop (1-3), cabinet (1-6), shelf (1-3). I can check one by one, starting with a drawer.
Obs 2: OK.
Act 3: go to drawer 3
Obs 3: The drawer 3 is closed.
Act 4: open drawer 3
Obs 4: You open the drawer 3. The drawer 3 is open. In it, you see a cellphone 1.
Act 5: go to drawer 2
Obs 5: The drawer 2 is closed.
Act 6: open drawer 2
Obs 6: You open the drawer 2. The drawer 2 is open. In it, you see a peppershaker 1, and a saltshaker 1.
Act 7: go to drawer 1
Obs 7: The drawer 1 is closed.
Act 8: open drawer 1
Obs 8: You open the drawer 1. The drawer 1 is open. In it, you see a fork 1.
Act 9: think: I didn't find a spatula in the drawers. I should check the sinkbasin, countertop, cabinet, and shelf next.
Obs 9: OK.
Act 10: go to sinkbasin 1
Obs 10: On the sinkbasin 1, you see a apple 1, a butterknife 2, a potato 3, and a tomato 2.
Act 11: take spatula 1 from sinkbasin 1
Obs 11: Nothing happens.
Act 12: think: I didn't find a spatula in the sinkbasin. I should check the countertop, cabinet, and shelf next.
Obs 12: OK.
Act 13: go to countertop 1
Obs 13: On the countertop 1, you see a cellphone 2, a mug 1, and a soapbottle 1.
Act 14: take spatula 1 from countertop 1
Obs 14: Nothing happens.
Act 15: think: I didn't find a spatula on the countertop. I should check the cabinet and shelf next.
Obs 15: OK.
Act 16: go to cabinet 1
Obs 16: On the cabinet 1, you see a glassbottle 2.
Act 17: take spatula 1 from cabinet 1
Obs 17: Nothing happens.
Act 18: think: I didn't find a spatula in the cabinet. I should check the shelf next.
Obs 18: OK.
Act 19: go to shelf 1
Obs 19: On the shelf 1, you see a peppershaker 2, and a vase 2.
Act 20: take spatula 1 from shelf 1
Obs 20: Nothing happens.
Act 21: think: I didn't find a spatula on the shelf either. Let me try checking the other countertop, cabinet, and shelf.
Obs 21: OK.
Act 22: go to countertop 2
Obs 22: On the countertop 2, you see a butterknife 1, a glassbottle 3, a knife 1, a papertowelroll 1, a potato 1, and a statue 1.
Act 23: take spatula 1 from countertop 2
Obs 23: Nothing happens.
Act 24: think: I didn't find a spatula on this countertop either. Let me try checking the other countertop, cabinet, and shelf.
Obs 24: OK.
Act 25: go to countertop 3
Obs 25: On the countertop 3, you see a bread 1, a creditcard 1, a houseplant 1, a knife 2, a spatula 1, a spoon 1, and a statue 2.
Act 26: take spatula 1 from countertop 3
Obs 26: You pick up the spatula 1 from the countertop 3.
Act 27: think: Now I have found a spatula (1). Next, I need to go to the sinkbasin (1) and clean it.
Obs 27: OK.
Act 28: go to sinkbasin 1
Obs 28: On the sinkbasin 1, you see a apple 1, a butterknife 2, a potato 3, and a tomato 2.
Act 29: clean spatula 1 with sinkbasin 1
Obs 29: You clean the spatula 1 using the sinkbasin 1.
Act 30: think: Now I have cleaned the spatula (1). Next, I need to put it in a drawer.
Obs 30: OK.
"""
    log3 = """
    You are in the middle of a room. Looking quickly around you, you see a bed 1, a desk 2, a desk 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a laundryhamper 1, a safe 1, a shelf 6, a shelf 5, a shelf 4, a shelf 3, a shelf 2, and a shelf 1.
Your task is to: look at bowl under the desklamp.
Act 1: think: To solve the task, I need to find and take a bowl, then find and use a desklamp. First I need to find a bowl. A bowl is more likely to appear in drawer (1-6), desk (1-2), shelf (1-6), garbagecan (1), laundryhamper (1). I can check one by one, starting with drawer 1.
Obs 1: OK.
Act 2: go to drawer 1
Obs 2: The drawer 1 is closed.
Act 3: open drawer 1
Obs 3: You open the drawer 1. The drawer 1 is open. In it, you see a cellphone 2.
Act 4: go to drawer 2
Obs 4: On the drawer 2, you see a keychain 1.
Act 5: go to drawer 3
Obs 5: Nothing happens.
Act 6: go to drawer 4
Obs 6: The drawer 4 is closed.
Act 7: open drawer 4
Obs 7: You open the drawer 4. The drawer 4 is open. In it, you see nothing.
Act 8: go to drawer 5
Obs 8: On the drawer 5, you see nothing.
Act 9: go to drawer 6
Obs 9: The drawer 6 is closed.
Act 10: open drawer 6
Obs 10: You open the drawer 6. The drawer 6 is open. In it, you see a book 2, and a pen 2.
Act 11: think: Now I find a bowl. Next, I need to take it.
Obs 11: OK.
Act 12: take bowl from drawer 6
Obs 12: Nothing happens.
Act 13: think: I can't seem to find a bowl in the drawers. I should check the desks next. A bowl is more likely to be found in desk (1-2). I will start with desk 1.
Obs 13: OK.
Act 14: go to desk 1
Obs 14: On the desk 1, you see a alarmclock 1, a desklamp 1, a mug 1, and a pencil 1.
Act 15: think: Now I find a bowl. Next, I need to take it. A bowl is more likely to be found in desk (1-2). I will check desk 2 next.
Obs 15: OK.
Act 16: go to desk 2
Obs 16: On the desk 2, you see a bowl 2, a bowl 1, a cd 2, a cd 1, and a creditcard 3.
Act 17: think: Now I find a bowl (2). Next, I need to take it.
Obs 17: OK.
Act 18: take bowl 2 from desk 2
Obs 18: You pick up the bowl 2 from the desk 2.
Act 19: think: Now I take a bowl (2). Next, I need to find a desklamp. A desklamp is more likely to be found in desk (1-2), shelf (1-6), bed (1), garbagecan (1), laundryhamper (1). I will check the desks first, starting with desk 1.
Obs 19: OK.
Act 20: go to desk 1
Obs 20: On the desk 1, you see a alarmclock 1, a desklamp 1, a mug 1, and a pencil 1.
Act 21: go to desk 2
Obs 21: On the desk 2, you see a bowl 1, a cd 2, a cd 1, and a creditcard 3.
Act 22: think: Now I find a desklamp (1). Next, I need to use it.
Obs 22: OK.
Act 23: use desklamp 1
Obs 23: Nothing happens.
Act 24: think: It seems like the desklamp is not working. I should try to find another one. A desklamp is more likely to be found in shelf (1-6), bed (1), garbagecan (1), laundryhamper (1). I will check the shelves next, starting with shelf 1.
Obs 24: OK.
Act 25: go to shelf 1
Obs 25: On the shelf 1, you see a pencil 2.
Act 26: go to shelf 2
Obs 26: On the shelf 2, you see a pen 1.
Act 27: go to shelf 3
Obs 27: On the shelf 3, you see a desklamp 1, and a pencil 1.
Act 28: think: Now I find a desklamp (1). Next, I need to use it.
Obs 28: OK.
Act 29: use desklamp 1
Obs 29: You turn on the desklamp 1.
Result: Task Success!
"""
    experience = plan_extract_agent(log3)
    print(json.dumps(experience, indent=2))

# example_experience = [
#   {
#     "task": "find and take a tomato",
#     "steps": [
#       "go to countertop 1",
#       "take tomato 1 from countertop 1"
#     ]
#   },
#   {
#     "task": "cool the tomato with the fridge",
#     "steps": [
#       "go to fridge 1",
#       "cool tomato 1 with fridge 1"
#     ]
#   },
#   {
#     "task": "put the tomato in the microwave",
#     "steps": [
#       "go to microwave 1",
#       "open microwave 1",
#       "put tomato 1 in/on microwave 1"
#     ]
#   }
# ]

# example_experience2 = [
#   {
#     "task": "find and take a spatula",
#     "steps": [
#       "go to countertop 3",
#       "take spatula 1 from countertop 3"
#     ]
#   },
#   {
#     "task": "clean the spatula",
#     "steps": [
#       "go to sinkbasin 1",
#       "clean spatula 1 with sinkbasin 1"
#     ]
#   },
#     {
#         "task": "put a spatula in drawer",
#         "steps": [
#             "go to drawer 1"
#             "put spatula 1 in/on drawer 1"
#         ]
#     }
# ]
