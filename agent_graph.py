from langgraph.graph import StateGraph, END
from nodes.fetch_transcript import fetch_transcript
from nodes.chunk_text import chunk_text
from nodes.summarize import summarize_chunks, summarize_timeline
from nodes.qa_agent import answer_question
from nodes.controller import controller

from typing import TypedDict, Literal

class AgentState(TypedDict):
    video_id: str
    transcript: str
    chunks: list[str]
    mode: Literal["summary", "timeline", "qa"]
    summary: str
    timeline: str
    qa_answer: str

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("fetch", lambda x: {"transcript": fetch_transcript(x["video_id"])})
    builder.add_node("chunk", lambda x: {"chunks": chunk_text(x["transcript"])})
    builder.add_node("controller", controller)
    builder.add_node("summarize_chunks_node", summarize_chunks)
    builder.add_node("timeline_node", summarize_timeline)
    builder.add_node("qa", answer_question)

    builder.set_entry_point("fetch")
    builder.add_edge("fetch", "chunk")
    builder.add_edge("chunk", "controller")
    builder.add_conditional_edges(
    "controller",
    lambda x: x["mode"],
    {
        "summary": "summarize_chunks_node",
        "timeline": "timeline_node",
        "qa": "qa"
    }
)

    builder.add_edge("summarize_chunks_node", END)
    builder.add_edge("timeline_node", END)
    builder.add_edge("qa", END)
    return builder.compile()
