import streamlit as st
from agent import agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        config = {"configurable": {"thread_id": "streamlit_user"}}
        input_data = {"messages": [HumanMessage(content=prompt)]}
        
        status_placeholder = st.empty()
        status_placeholder.write("🤖 Thinking...")
        
        for event in agent.stream(input_data, config=config, stream_mode="values"):
            if "messages" in event:
                last_message = event["messages"][-1]
                
                if isinstance(last_message, AIMessage):
                    if last_message.tool_calls:
                        status_placeholder.write("🛠️ Calling tool...")
                    else:
                        full_response = last_message.content
                        if isinstance(full_response, list):
                            full_response = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in full_response])
                        
                        if full_response:
                            status_placeholder.empty()
                            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})