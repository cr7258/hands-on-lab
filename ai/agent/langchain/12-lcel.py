from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.tracers import Run
import time

def test1(x: int):
    return x + 10


# 节点： 标准：Runnable
r1 = RunnableLambda(test1)  # 把行数封装成一个组件

res = r1.invoke(4)
print("单次调用:", res)
# 14

# 2、批量调用
res = r1.batch([4, 5])
print("批量调用:", res)
# [14, 15]

# 3、流式调用
def test2(prompt: str):
    for item in prompt.split(' '):
        yield item

r1 = RunnableLambda(test2)  # 把行数封装成一个组件
res = r1.stream('This is a Dog.')  # 返回的是一个生成器
for chunk in res:
    print(chunk)
# This
# is
# a
# Dog.

#  4、组合链
r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x: x * 2)

chain1 = r1 | r2  # 串行
print(chain1.invoke(2))
# 24

#  5、 并行运行
chain2 = RunnableParallel(k1=r1, k2=r2)
# max_concurrency: 最大并发数
print(chain2.invoke(2, config={'max_concurrency': 3}))
# {'k1': 12, 'k2': 4}

new_chain = chain1 | chain2
new_chain.get_graph().print_ascii() # 打印链的图像描述
#       +-------------+         
#       | test1_input |         
#       +-------------+         
#               *               
#               *               
#               *               
#          +-------+            
#          | test1 |            
#          +-------+            
#               *               
#               *               
#               *               
#          +--------+           
#          | Lambda |           
#          +--------+           
#               *               
#               *               
#               *               
#   +----------------------+    
#   | Parallel<k1,k2>Input |    
#   +----------------------+    
#          *        *           
#        **          **         
#       *              *        
# +-------+         +--------+  
# | test1 |         | Lambda |  
# +-------+         +--------+  
#          *        *           
#           **    **            
#             *  *              
#  +-----------------------+    
#  | Parallel<k1,k2>Output |    
#  +-----------------------+    
print(new_chain.invoke(2))

# 首先执行 chain1：
# 输入2传给r1：2 + 10 = 12
# 12传给r2：12 * 2 = 24
# chain1的输出是24

# 然后24作为输入传给 chain2：
# 并行执行r1(24)：24 + 10 = 34
# 并行执行r2(24)：24 * 2 = 48
# chain2的输出是 {'k1': 34, 'k2': 48}
# {'k1': 34, 'k2': 48}

# 6、合并输入，并处理中间数据
# RunnablePassthrough： 允许传递输入数据，可以保持不变或添加额外的键。 必须传入一个字典数据， 还可以过滤
r1 = RunnableLambda(lambda x: {'key1': x})
r2 = RunnableLambda(lambda x: x['key1'] + 10)

chain = r1 | RunnablePassthrough.assign(new_key=r2)  # new_key, 随意定制的，代表输出的key
print(chain.invoke(2))
# {'key1': 2, 'new_key': 12}

chain = r1 | RunnableParallel(foo=RunnablePassthrough(), new_key=RunnablePassthrough.assign(key2=r2))
print(chain.invoke(2))
# {'foo': {'key1': 2}, 'new_key': {'key1': 2, 'key2': 12}}

r3 = RunnableLambda(lambda x: x['new_key']['key2'])
# pick 只选择 new_key
chain = r1 | RunnableParallel(foo=RunnablePassthrough(), new_key=RunnablePassthrough.assign(key2=r2)) | RunnablePassthrough().pick(['new_key']) | r3
print(chain.invoke(2))
# 12

# 7、后备选项 ：后备选项是一种可以在紧急情况下使用的替代方案。
r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x: int(x) + 20)
# 在加法计算中的后备选项
chain = r1.with_fallbacks([r2])  # r2是r1的后备方案，r1 报错的情况下
print(chain.invoke('2')) # 故意传入字符串，产生错误，使用后备方案
# 22

# 8、如有报错，重复多次执行某个节点（比如爬取数据，可能因为网络问题会失败，可以进行重试）
# counter = 0  # 计数用的
# def test3(x):
#     global counter
#     counter += 1
#     print(f'执行了 {counter} 次')
#     return x / 0 # 每次都报错

# # 报错了才会重试
# r1 = RunnableLambda(test3).with_retry(stop_after_attempt=4)
# print(r1.invoke(2))
# 执行了 1 次
# 执行了 2 次
# 执行了 3 次
# 执行了 4 次
# 后面会报错

# 根据条件，动态的构建链
r1 = RunnableLambda(test1)
r2 = RunnableLambda(lambda x: [x] * 2)

# 根据r1的输出结果，判断，是否要执行r2，（判断本身也是一个节点）
chain = r1 | RunnableLambda(lambda x: r2 if x > 12 else RunnableLambda(lambda x: x))
print(chain.invoke(3))
# [13, 13]，触发了 r2


# 生命周期管理
def test4(n: int):
    time.sleep(n)
    return n * 2

r1 = RunnableLambda(test4)

def on_start(run_obj: Run):
    """ 当r1节点启动的时候，自动调用"""
    print('r1启动的时间：', run_obj.start_time)

def on_end(run_obj: Run):
    """ 当r1节已经运行结束的时候，自动调用"""
    print('r1结束的时间：', run_obj.end_time)

chain = r1.with_listeners(on_start=on_start, on_end=on_end)
print(chain.invoke(2))
# r1启动的时间：2025-03-09 14:53:25.996365+00:00
# r1结束的时间：2025-03-09 14:53:28.001429+00:00
# 4
     