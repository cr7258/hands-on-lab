from os import getenv
from langchain.agents import initialize_agent, AgentType
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base="https://openrouter.ai/api/v1",
  model_name="openai/gpt-4o",
)

# 内置的工具
tools = load_tools(['llm-math', 'arxiv'], llm)

agent = initialize_agent(  # 初始化智能体
    tools,
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,  # 如果解析报错，继续
    verbose=True,
)

# resp = agent.invoke('What is the 25% of 300?')
# print(resp)

resp = agent.invoke('介绍一下2006.13145这篇论文的创新点？')
print(resp)

# > Entering new AgentExecutor chain...
# Question: 介绍一下2006.13145这篇论文的创新点？
# Thought: I need to look up the paper with the identifier 2006.13145 on arXiv to understand its contributions.
# Action:
# ```
# {
#   "action": "arxiv",
#   "action_input": "2006.13145"
# }
# ```

# Observation: Published: 2020-07-15
# Title: An $ε$-regularity criterion and estimates of the regular set for Navier-Stokes flows in terms of initial data
# Authors: Kyungkeun Kang, Hideyuki Miura, Tai-Peng Tsai
# Summary: We prove an $\epsilon$-regularity criterion for the 3D Navier-Stokes
# equations in terms of initial data. It shows that if a scaled local $L^2$ norm
# of initial data is sufficiently small around the origin, a suitable weak
# solution is regular in a set enclosed by a paraboloid started from the origin.
# The result is applied to the estimate of the regular set for local energy
# solutions with initial data in weighted $L^2$ spaces. We also apply this result
# to studying energy concentration near a possible blow-up time and regularity of
# forward discretely self-similar solutions.
# Thought:The paper "An $ε$-regularity criterion and estimates of the regular set for Navier-Stokes flows in terms of initial data" introduces several innovative contributions:

# 1. **$ε$-Regularity Criterion**: The authors have developed an $\epsilon$-regularity criterion for the 3D Navier-Stokes equations based explicitly on the initial data. This provides a condition under which the solutions remain regular, offering insights into the behavior of the system under certain initial conditions.

# 2. **Scaled Local $L^2$ Norm Condition**: They show that if a scaled local $L^2$ norm of the initial data is sufficiently small around the origin, then a suitable weak solution is regular. This approach links the regularity of solutions to the properties of initial data, which is a significant step forward in understanding fluid dynamics modeled by the Navier-Stokes equations.

# 3. **Regular Set Estimation**: The criterion is applied to estimate the regular set for local energy solutions with initial data in weighted $L^2$ spaces. This provides a method to analyze the regions in space-time where the solutions are expected to remain smooth.

# 4. **Energy Concentration and Blow-Up Analysis**: The results are applied to study energy concentration near a possible blow-up time, which is crucial for understanding singularity formation in fluid flows.

# 5. **Regularity of Forward Discretely Self-Similar Solutions**: The paper also explores the regularity properties of forward discretely self-similar solutions, contributing to the broader understanding of solution behavior under self-similarity transformations.

# These contributions advance the understanding of the Navier-Stokes equations, particularly in terms of solution regularity and the influence of initial conditions, which are central themes in the theory of partial differential equations and fluid dynamics. 

# Final Answer: The paper introduces an $\epsilon$-regularity criterion for the 3D Navier-Stokes equations relating to initial data, offers methods to estimate regular sets, analyzes energy concentration, and studies the regularity of self-similar solutions, contributing to the understanding of flow behaviors and singularities.

# > Finished chain.
# {'input': '介绍一下2006.13145这篇论文的创新点？', 'output': 'The paper introduces an $\\epsilon$-regularity criterion for the 3D Navier-Stokes equations relating to initial data, offers methods to estimate regular sets, analyzes energy concentration, and studies the regularity of self-similar solutions, contributing to the understanding of flow behaviors and singularities.'}