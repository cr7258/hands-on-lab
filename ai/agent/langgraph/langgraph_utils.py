def draw_graph(graph, png_file):
    try:
        # 生成 graph的图
        image = graph.get_graph().draw_mermaid_png()
        with open(png_file, 'wb') as f:
            f.write(image)
    except Exception as e:
        print(e)


def loop_graph_invoke(graph, user_input: str):
    """循环调用这个流程图，让AI可以一直和用户对话"""
    # for chunk in graph.stream({'messages': [('user', user_input)]}):
    #     for value in chunk.values():
    #         print('AI机器人: ', value['messages'][-1].content)

    # stream_mode="values"：这意味着该方法将会直接返回事件中的值，而不是整个事件对象。
    # 这使得处理过程更加简洁，特别是当你只关心事件的具体内容而非其元数据时。
    events = graph.stream({"messages": [("user", user_input)]}, stream_mode="values")
    for event in events:
        event["messages"][-1].pretty_print()



def loop_graph_invoke(graph, user_input: str, config):
    """循环调用这个流程图，让AI可以一直和用户对话"""
    # stream_mode="values"：这意味着该方法将会直接返回事件中的值，而不是整个事件对象。
    # 这使得处理过程更加简洁，特别是当你只关心事件的具体内容而非其元数据时。
    events = graph.stream({"messages": [("user", user_input)]}, config, stream_mode="values")
    for event in events:
        event["messages"][-1].pretty_print()



def loop_graph_invoke_tools(graph, user_input: str, config):
    """循环调用这个流程图，让AI可以一直和用户对话"""
    # stream_mode="values"：这意味着该方法将会直接返回事件中的值，而不是整个事件对象。
    # 这使得处理过程更加简洁，特别是当你只关心事件的具体内容而非其元数据时。
    if user_input:
        events = graph.stream(
            {"messages": [("user", user_input)]}, config, stream_mode="values"
        )
        for event in events:
            if "messages" in event:
                event["messages"][-1].pretty_print()
    else:
        events = graph.stream(None, config, stream_mode="values")
        for event in events:
            if "messages" in event:
                event["messages"][-1].pretty_print()
