import streamlit as st
from langgraph_backend import workflow , config
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage


st.set_page_config(page_title='Chatbot', page_icon=':robot:')

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# loading convo history
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
       st.text(msg['content'])


user_input = st.chat_input('Type here')
if user_input:
    # first add the message to the message history
    st.session_state.chat_history.append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

   

    with st.chat_message('assistant'):
        with st.spinner('thinking...'):
           ai_message= st.write_stream(
              message_chunk.content for message_chunk, metadata in workflow.stream({
               'messages': [HumanMessage(content=user_input)]},
               config=config,
               stream_mode='messages'
    ) 
            
    )
    st.session_state.chat_history.append({'role':'assistant','content':ai_message})
   

