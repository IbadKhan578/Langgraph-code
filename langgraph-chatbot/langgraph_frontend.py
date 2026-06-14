import streamlit as st
from langgraph_backend import workflow , get_all_threads
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage
import uuid

#*****************utility function**************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    # generate new thread id
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])

    st.session_state['chat_history'] = []


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):
    state = workflow.get_state(
        config={'configurable': {'thread_id': thread_id}}
    )
    return state.values.get('messages', [])


#***********#app config **********************
st.set_page_config(page_title='Chatbot', page_icon=':robot:')




#**************** session setup ***************************
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_all_threads()

add_thread(st.session_state['thread_id'])







#***************************    sidebar ui *************************************

st.sidebar.title('Langgraph Chatbot')


if st.sidebar.button('New chat'):
    reset_chat()


st.sidebar.header('My conversation')

for id in st.session_state['chat_threads'][::-1]:
   if st.sidebar.button(str(id)):
     st.session_state['thread_id'] = id
     messages= load_conversation(id)


     temp_messages = []

     for message in messages:
         if isinstance(message, HumanMessage):
             role ='user'
         else:
             role ='assistant'   
         temp_messages.append({'role':role, 'content':message.content}) 


     st.session_state['chat_history'] = temp_messages         
         

#********************* loading convo history *****************************
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
       st.text(msg['content'])


# taking user input 
user_input = st.chat_input('Type here')
if user_input:
    # first add the message to the message history
    st.session_state.chat_history.append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    config = {'configurable':{'thread_id': st.session_state['thread_id']}}
   

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
   

