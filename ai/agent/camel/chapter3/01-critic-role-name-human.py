from camel.societies import RolePlaying
from camel.types import ModelPlatformType
from camel.models import ModelFactory

from os import getenv
from colorama import Fore

# model = ModelFactory.create(
#     model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
#     model_type="Qwen/Qwen2.5-72B-Instruct",
#     url='https://api-inference.modelscope.cn/v1/',
#     api_key=getenv("MODELSCOPE_API_KEY")
# )

model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type="qwen/qwen-turbo",
    url='https://openrouter.ai/api/v1/',
    api_key=getenv("OPENROUTER_API_KEY")
)

task_kwargs = {
    'task_prompt': '写一本关于AI社会的未来的书。',
    'with_task_specify': True,
    'task_specify_agent_kwargs': {'model': model}
}

user_role_kwargs = {
    'user_role_name': 'AI专家',
    'user_agent_kwargs': {'model': model}
}

assistant_role_kwargs = {
    'assistant_role_name': '对AI感兴趣的作家',
    'assistant_agent_kwargs': {'model': model}
}

society = RolePlaying(
    **task_kwargs,             # 任务参数
    **user_role_kwargs,        # 指令发送者的参数
    **assistant_role_kwargs,   # 指令接收者的参数
    critic_role_name='human',
    with_critic_in_the_loop=True,
    output_language="中文",
)

def is_terminated(response):
    """
    当会话应该终止时给出对应信息。
    """
    if response.terminated:
        role = response.msg.role_type.name
        reason = response.info['termination_reasons']
        print(f'AI {role} 因为 {reason} 而终止')

    return response.terminated

def run(society, round_limit: int=10):

    # 获取AI助手到AI用户的初始消息
    input_msg = society.init_chat()

    # 开始互动会话
    for _ in range(round_limit):

        # 获取这一轮的两个响应
        assistant_response, user_response = society.step(input_msg)

        # 检查终止条件
        if is_terminated(assistant_response) or is_terminated(user_response):
            break

        # 获取结果
        print(Fore.GREEN + f'[AI 用户] {user_response.msg.content}.\n')
        # 检查任务是否结束
        if 'CAMEL_TASK_DONE' in user_response.msg.content:
            break
        print(Fore.BLUE + f'[AI 助手] {assistant_response.msg.content}.\n')

        # 获取下一轮的输入消息
        input_msg = assistant_response.msg

    return None

run(society)

# > Proposals from AI专家 (RoleType.USER). Please choose an option:
# Option 1:
# Instruction: 首先，我们需要确定书的大纲。请列出你认为应该包含在书中的主要章节。
# Input: None
# Option 2:
# Input by Kill Switch Engineer.
# Option 3:
# Stop!!!
# Please enter your choice ([1-3]): 1
#
#
#
# > Proposals from 对AI感兴趣的作家 (RoleType.ASSISTANT). Please choose an option:
# Option 1:
# Solution: 为了确保这本书内容丰富且结构合理，我建议将大纲分为以下几个主要章节：
#
# 1. **引言**
#    - 2050年的愿景
#    - AI的发展历程
#    - 本书的目的和结构
#
# 2. **技术基础**
#    - 当前AI技术的现状
#    - 未来AI技术的发展趋势
#    - 关键技术突破（如量子计算、神经网络、自然语言处理）
#
# 3. **AI伦理与法律**
#    - AI伦理原则
#    - 数据隐私与安全
#    - 法律框架与监管
#    - 案例研究：AI伦理问题的实际案例
#
# 4. **人机共生**
#    - 人机交互的未来
#    - 增强现实与虚拟现实的应用
#    - 机器人在日常生活中的角色
#    - 情感计算与社交机器人
#
# 5. **经济影响**
#    - AI对就业市场的影响
#    - 新兴行业的崛起
#    - 经济增长与分配不均
#    - 案例研究：AI在不同行业中的应用
#
# 6. **教育变革**
#    - 个性化学习与自适应教学系统
#    - 在线教育与远程学习
#    - 教师角色的转变
#    - 未来学校的形态
#
# 7. **医疗健康**
#    - 精准医疗与基因编辑
#    - 远程医疗与智能诊断
#    - 健康管理与预防医学
#    - 案例研究：AI在医疗领域的实际应用
#
# 8. **社会治理**
#    - 智能城市与智慧交通
#    - 公共安全与应急响应
#    - 社会福利与公共服务
#    - 案例研究：AI在社会治理中的应用
#
# 9. **环境与可持续发展**
#    - AI在环境保护中的应用
#    - 能源管理与可再生能源
#    - 气候变化与灾害预测
#    - 案例研究：AI在环境保护中的实际案例
#
# 10. **文化与艺术**
#     - AI在创意产业中的应用
#     - 数字艺术与虚拟现实
#     - 媒体与娱乐产业的变革
#     - 案例研究：AI在文化和艺术中的创新
#
# 11. **结论**
#     - 2050年AI社会的展望
#     - 人类与AI的和谐共生
#     - 未来的挑战与机遇
#
# 每个章节都可以进一步细分为多个小节，以确保内容的全面性和深度。希望这个大纲能够为你提供一个清晰的框架，帮助我们顺利完成这本书。
#
# Next request.
# Option 2:
# Input by Kill Switch Engineer.
# Option 3:
# Stop!!!
# Please enter your choice ([1-3]): 1
#
#
# [AI 用户] Instruction: 首先，我们需要确定书的大纲。请列出你认为应该包含在书中的主要章节。
# Input: None.
#
# [AI 助手] Solution: 为了确保这本书内容丰富且结构合理，我建议将大纲分为以下几个主要章节：
#
# 1. **引言**
#    - 2050年的愿景
#    - AI的发展历程
#    - 本书的目的和结构
#
# 2. **技术基础**
#    - 当前AI技术的现状
#    - 未来AI技术的发展趋势
#    - 关键技术突破（如量子计算、神经网络、自然语言处理）
#
# 3. **AI伦理与法律**
#    - AI伦理原则
#    - 数据隐私与安全
#    - 法律框架与监管
#    - 案例研究：AI伦理问题的实际案例
#
# 4. **人机共生**
#    - 人机交互的未来
#    - 增强现实与虚拟现实的应用
#    - 机器人在日常生活中的角色
#    - 情感计算与社交机器人
#
# 5. **经济影响**
#    - AI对就业市场的影响
#    - 新兴行业的崛起
#    - 经济增长与分配不均
#    - 案例研究：AI在不同行业中的应用
#
# 6. **教育变革**
#    - 个性化学习与自适应教学系统
#    - 在线教育与远程学习
#    - 教师角色的转变
#    - 未来学校的形态
#
# 7. **医疗健康**
#    - 精准医疗与基因编辑
#    - 远程医疗与智能诊断
#    - 健康管理与预防医学
#    - 案例研究：AI在医疗领域的实际应用
#
# 8. **社会治理**
#    - 智能城市与智慧交通
#    - 公共安全与应急响应
#    - 社会福利与公共服务
#    - 案例研究：AI在社会治理中的应用
#
# 9. **环境与可持续发展**
#    - AI在环境保护中的应用
#    - 能源管理与可再生能源
#    - 气候变化与灾害预测
#    - 案例研究：AI在环境保护中的实际案例
#
# 10. **文化与艺术**
#     - AI在创意产业中的应用
#     - 数字艺术与虚拟现实
#     - 媒体与娱乐产业的变革
#     - 案例研究：AI在文化和艺术中的创新
#
# 11. **结论**
#     - 2050年AI社会的展望
#     - 人类与AI的和谐共生
#     - 未来的挑战与机遇
#
# 每个章节都可以进一步细分为多个小节，以确保内容的全面性和深度。希望这个大纲能够为你提供一个清晰的框架，帮助我们顺利完成这本书。
#
# Next request..
#
#
# > Proposals from AI专家 (RoleType.USER). Please choose an option:
# Option 1:
# Instruction: 根据你提供的大纲，接下来我们需要为每个章节编写详细的内容提纲。请从“引言”部分开始，列出具体的小节和主要内容。
# Input: None
# Option 2:
# Input by Kill Switch Engineer.
# Option 3:
# Stop!!!
# Please enter your choice ([1-3]): 1
#
#
#
# > Proposals from 对AI感兴趣的作家 (RoleType.ASSISTANT). Please choose an option:
# Option 1:
# Solution: 好的，我们将从“引言”部分开始，为每个章节编写详细的内容提纲。以下是“引言”部分的具体小节和主要内容：
#
# ### 引言
#
# #### 1.1 2050年的愿景
# - **2050年的世界**：描述2050年全球社会的基本面貌，包括人口、经济、科技等方面的预期变化。
# - **AI的普及与影响**：讨论AI在各个领域的广泛应用及其对社会的深远影响。
# - **未来生活的想象**：通过具体的场景和案例，展示2050年人类生活的可能状态。
#
# #### 1.2 AI的发展历程
# - **早期探索**：回顾AI的起源和发展，包括图灵测试、早期的机器学习算法等。
# - **现代进展**：介绍近年来AI技术的重大突破，如深度学习、自然语言处理、计算机视觉等。
# - **未来趋势**：预测AI技术在未来几十年内的发展方向，包括量子计算、通用人工智能等。
#
# #### 1.3 本书的目的和结构
# - **写作目的**：明确本书的目标读者和写作目的，强调对AI未来发展的探讨和反思。
# - **章节概览**：简要介绍本书的主要章节和内容安排，帮助读者了解全书的结构。
# - **阅读指南**：提供一些阅读建议和注意事项，帮助读者更好地理解和吸收书中的内容。
#
# ### 示例内容
#
# #### 1.1 2050年的愿景
# - **2050年的世界**：
#   - 人口老龄化与年轻化并存
#   - 城市化进程加速，智能城市成为主流
#   - 可持续能源和环保技术的广泛应用
# - **AI的普及与影响**：
#   - 自动驾驶汽车成为常态
#   - 智能家居普及，生活更加便捷
#   - 医疗健康领域的精准治疗和远程诊断
# - **未来生活的想象**：
#   - 早晨：智能家居系统自动调节温度、光线和音乐
#   - 上班：自动驾驶汽车接送，工作场所充满智能设备
#   - 休闲：虚拟现实技术带来全新的娱乐体验
#
# #### 1.2 AI的发展历程
# - **早期探索**：
#   - 图灵测试的提出及其意义
#   - 早期的机器学习算法和应用
# - **现代进展**：
#   - 深度学习的兴起及其在图像识别、语音识别等领域的应用
#   - 自然语言处理的突破，如机器翻译、情感分析
#   - 计算机视觉的进步，如人脸识别、物体检测
# - **未来趋势**：
#   - 量子计算的潜力及其对AI的推动作用
#   - 通用人工智能的可能性和挑战
#   - 人机共生的未来展望
#
# #### 1.3 本书的目的和结构
# - **写作目的**：
#   - 探讨2050年AI社会的未来图景
#   - 分析AI伦理、人机共生及智能革命对各领域的影响
#   - 提供对未来发展的思考和建议
# - **章节概览**：
#   - 技术基础
#   - AI伦理与法律
#   - 人机共生
#   - 经济影响
#   - 教育变革
#   - 医疗健康
#   - 社会治理
#   - 环境与可持续发展
#   - 文化与艺术
#   - 结论
# - **阅读指南**：
#   - 建议读者按顺序阅读，以便更好地理解内容
#   - 对于特定领域的读者，可以重点阅读相关章节
#   - 鼓励读者参与讨论，提出自己的观点和想法
#
# 希望这个详细的提纲能够帮助你更好地组织和编写“引言”部分的内容。如果有任何修改或补充意见，请随时告诉我。
#
# Next request.
# Option 2:
# Input by Kill Switch Engineer.
# Option 3:
# Stop!!!
# Please enter your choice ([1-3]): 3
#
# Killed by Kill Switch Engineer.
