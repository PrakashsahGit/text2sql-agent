from agent.graph import build_graph

graph = build_graph()

# ✅ Use Graphviz instead of pygraphviz
graph.get_graph().draw_png("agent_graph.png", prog="dot")

print("✅ Graph saved as agent_graph.png")