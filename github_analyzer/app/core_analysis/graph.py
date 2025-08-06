from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.core_analysis.state import AgentState
from app.core_analysis.agents import (
    triage, profiler, evaluator, deconstructor, security, evolution, synthesizer, writer
)

memory = SqliteSaver.from_conn_string(":memory:")

def create_graph():
    graph = StateGraph(AgentState)

    graph.add_node("triage", triage.run)
    graph.add_node("profiler", profiler.run)
    graph.add_node("evaluator", evaluator.run)
    graph.add_node("deconstructor", deconstructor.run)
    graph.add_node("security", security.run)
    graph.add_node("evolution", evolution.run)
    graph.add_node("synthesizer", synthesizer.run)
    graph.add_node("writer", writer.run)

    graph.set_entry_point("triage")

    graph.add_edge("triage", "profiler")
    graph.add_edge("profiler", "evaluator")
    graph.add_edge("evaluator", "deconstructor")
    graph.add_edge("deconstructor", "security")
    graph.add_edge("security", "evolution")
    graph.add_edge("evolution", "synthesizer")
    graph.add_edge("synthesizer", "writer")
    graph.add_edge("writer", END)

    return graph.compile(checkpointer=memory)

app = create_graph()
