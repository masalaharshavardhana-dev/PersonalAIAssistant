from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage
import os
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from tools.weather import get_weather
from tools.stock import get_stock_price
from tools.news import get_latest_news
from tools.search import tavily_search
from tools.irctc_tool import irctc_tool
from tools.youtube_search_tool import search_youtube_videos

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

api_key = os.getenv("GROQ_API_KEY")
model = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

def model_call(state: AgentState) -> AgentState:
    system_prompt = (
        "You are a helpful personal chatbot assistant. Use the provided tools to answer questions. "
        "Use tools only when necessary. Do not use tools for simple questions."
        "If a tool provides information, you MUST use that information to construct your answer.\n"
        "IMPORTANT: When you decide to call a tool, you MUST NOT output any text or answer alongside it. ONLY output the tool call.\n"
        "When you have the final answer, your response MUST consist of two parts:\n"
        "only give suggestion when neccessary according to the question"
        "1. First, provide the direct answer to the user's question using the information from the tools (e.g., the current temperature, weather conditions, etc.).\n"
        "2. Then, provide exactly 3 personal, actionable pieces of advice or suggestions based on the context of the user's query and the information provided (e.g., if the temperature is very high, advise the user to stay hydrated and avoid direct sunlight). Do not generate generic follow-up questions about what else the user wants to know.\n"
        "Format the suggestions as a bulleted list under the heading '### Suggestions'."
    )
    
    messages = state['messages']
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages = [SystemMessage(content=system_prompt)] + messages
    
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_router(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

tools = [
    get_weather,
    get_stock_price,
    get_latest_news,
    tavily_search,
    irctc_tool,
    search_youtube_videos
]

model_with_tools = model.bind_tools(tools)

tools_node = ToolNode(tools)
graph = StateGraph(AgentState)
graph.add_node("model", model_call)
graph.add_node("tools", tools_node)
graph.add_edge("tools", "model")
graph.add_edge(START, "model")
graph.add_conditional_edges(
    "model",
    tool_router,
    {
        "tools": "tools",
        "end": END
    }
)

memory = InMemorySaver()
agent = graph.compile(checkpointer=memory)