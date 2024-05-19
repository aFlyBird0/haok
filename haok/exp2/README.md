## 历史案例驱动的任务规划方法

1. 先跑 alfword_exp.py，生成 ReAct 的结果 
    * 记得改 sample 变量（任务数量）
    * 记得改get_settings()里的模型设置
    * 记得改 log_dir
    * agent_type = "react"
2. 再跑 extract_all_logs_to_plan.py，生成任务规划经验
   * 记得改 haok/config/config.py 里的数据库设置，plan_collection 每个模型和批次数量，用不同的collection
   * plan_extract_agent.py 里的 llm 也记得改
3. 重跑一遍 alfword_exp.py，生成 ReAct-Haok 的结果
    * 记得改 sample 变量（任务数量）
    * 记得改get_settings()里的模型设置
    * 记得改 log_dir
    * agent_type = "react_with_haok"
* 最后跑 read_results_exp2.py，读取数据画实验图
  * 记得改 sample 变量（任务数量）