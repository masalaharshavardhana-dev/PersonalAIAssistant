import streamlit as st
from agent import agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import streamlit.components.v1 as components
from streamlit_mic_recorder import mic_recorder
import os
import hashlib
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Agent", layout="wide")
st.title("🤖 AI Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

audio_bytes = mic_recorder(
    start_prompt="Record",
    stop_prompt="🛑",
    just_once=True,
    use_container_width=False,
    format="wav",
    key="mic_recorder"
)

prompt = st.chat_input("Ask anything")

components.html(
    """
    <script>
    const setupUI = setInterval(() => {
        try {
            const chatInput = window.parent.document.querySelector('[data-testid="stChatInput"] textarea');
            const chatInputContainer = window.parent.document.querySelector('[data-testid="stChatInput"]');
            
            // Find our iframe
            const iframes = window.parent.document.querySelectorAll('iframe');
            let micIframe = null;
            for (let i = 0; i < iframes.length; i++) {
                if (iframes[i].title && iframes[i].title.includes('streamlit_mic_recorder')) {
                    micIframe = iframes[i];
                    break;
                }
            }

            if (chatInputContainer && chatInput && micIframe) {
                // Add padding to the chat input to make room for our button(s)
                chatInput.style.paddingRight = '60px';
                
                // Re-position the block container of the iframe so it doesn't take space where it originally was
                const elementBlock = micIframe.closest('[data-testid="stElementBlock"]') || micIframe;
                
                // Fix the position to overlay the chat input
                elementBlock.style.position = 'fixed';
                elementBlock.style.zIndex = '99999';
                elementBlock.style.width = '32px';
                elementBlock.style.height = '32px';
                elementBlock.style.borderRadius = '50%';
                
                const rect = chatInput.getBoundingClientRect();
                elementBlock.style.left = (rect.right - 42) + 'px';
                elementBlock.style.top = (rect.top + (rect.height - 32)/2) + 'px'; 
                
                micIframe.style.width = '32px';
                micIframe.style.height = '32px';
                micIframe.style.borderRadius = '50%';
                
                const iframeDoc = micIframe.contentDocument || micIframe.contentWindow.document;
                if (iframeDoc) {
                    const btn = iframeDoc.querySelector('button');
                    if (btn) {
                        btn.style.backgroundColor = 'white';
                        btn.style.color = 'black';
                        btn.style.cursor = 'pointer';
                        btn.style.borderRadius = '50%';
                        btn.style.border = 'none';
                        btn.style.width = '32px';
                        btn.style.height = '32px';
                        btn.style.display = 'flex';
                        btn.style.alignItems = 'center';
                        btn.style.justifyContent = 'center';
                        btn.style.margin = '0';
                        btn.style.padding = '0';
                        btn.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
                        
                        const text = btn.innerText.trim();
                        if (text === 'Record' || text === '🎙️') {
                            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="black" viewBox="0 0 16 16"><path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0z"/><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/></svg>';
                        } else if (text === '🛑') {
                            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="black" viewBox="0 0 16 16"><rect width="10" height="10" x="3" y="3" rx="2"/></svg>';
                        }
                    }
                }
            }
        } catch (e) {}
    }, 50);
    </script>
    """,
    height=0,
    width=0
)

if audio_bytes and "bytes" in audio_bytes:
    audio_data = audio_bytes["bytes"]
    audio_hash = hashlib.md5(audio_data).hexdigest()
    if audio_hash != st.session_state.get("last_audio_hash"):
        st.session_state["last_audio_hash"] = audio_hash
        with st.spinner("🎙️ Transcribing voice..."):
            temp_file = "temp_audio.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            with open(temp_file, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(temp_file, f.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            if transcription and transcription.strip():
                prompt = transcription.strip()

if prompt:
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