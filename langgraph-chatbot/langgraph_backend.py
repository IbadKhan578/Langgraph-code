from langgraph.graph import StateGraph, START , END
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()


# setting up llm
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv('GROQ_API_KEY')
)


from langgraph.graph.message import add_messages # reducer instead of add operator for messages , work well with base messages
class messageState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] # adding base message instead of str so it can take ai,human,system messages



def chat_node(state:messageState):
    # take user query from the state
    messages = state['messages']



    # pass that query to llm
    response = llm.invoke(messages) 

    # store in state 
    return{
        'messages' : [response]
    }


conn = sqlite3.connect( database='chatbot.db' , check_same_thread=False)
#checkpointer
checkpointer = SqliteSaver(conn=conn)


graph = StateGraph(messageState)

# add node
graph.add_node('chat_node', chat_node)

# add edges 

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

workflow = graph.compile(checkpointer=checkpointer)


# # # streaming the response
# for message_chunk, metadata in workflow.stream({
#     'messages': [HumanMessage(content='tell me the recepie to make biryani?')]},
#       config=config,
#       stream_mode='messages'
#     ) :
#     if message_chunk.content:
#         print(message_chunk.content, end=' ', flush=True)
    
def get_all_threads():
    all_thread = set()
    for checkpoint in checkpointer.list(None): # return all the checkpoints from the sqllite db
        all_thread.add(checkpoint.config['configurable']['thread_id'])


    return list(all_thread)