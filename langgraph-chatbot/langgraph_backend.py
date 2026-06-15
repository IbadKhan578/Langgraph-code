from langgraph.graph import StateGraph, START , END
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import BaseMessage , HumanMessage , AIMessage
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode , tools_condition 
from langchain_core.tools import tool

import requests
load_dotenv()


# setting up llm
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv('GROQ_API_KEY')
)

#************ tools*********************
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()


tools = [search_tool, calculator,get_stock_price]
llm_with_tools = llm.bind_tools(tools=tools)



from langgraph.graph.message import add_messages # reducer instead of add operator for messages , work well with base messages
class messageState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages] # adding base message instead of str so it can take ai,human,system messages



def chat_node(state:messageState):

    """ llm that may answer or call the tool node 
    """
    # take user query from the state
    messages = state['messages']

    # pass that query to llm
    response = llm_with_tools.invoke(messages) 

    # store in state 
    return{
        'messages' : [response]
    }

tool_node = ToolNode(tools)


conn = sqlite3.connect( database='chatbot.db' , check_same_thread=False)
#checkpointer
checkpointer = SqliteSaver(conn=conn)


graph = StateGraph(messageState)

# add node
graph.add_node('chat_node', chat_node)
graph.add_node('tools',tool_node)

# add edges 

graph.add_edge(START,'chat_node')
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools','chat_node')

workflow = graph.compile(checkpointer=checkpointer)
config = {'configurable':{'thread_id':'6'}}

out = workflow.invoke({'messages': [HumanMessage(content='what is the current stock prce of apple?')]},config=config)

print(out['messages'][-1].content)



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