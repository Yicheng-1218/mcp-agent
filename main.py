from pydantic_ai import Agent,RunContext
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ToolCallPartDelta,
    TextPart
)
from src.utils.messages import convert_history
import gradio as gr
from gradio import ChatMessage
import asyncio
from dotenv import load_dotenv
import logfire
from loguru import logger
import sys
from src.mcp_server.server_registry import ServerRegistry
import os

try:
    logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
    logfire.instrument_pydantic_ai()
except Exception as e:
    pass

load_dotenv()
SYSTEM_PROMPT=open('prompt/system_prompt.txt','r',encoding='utf-8').read()
MODEL_NAME="openai:gpt-4o"

class MyAgent:
    def __init__(self,mcp_server=[]) -> None:
        if not isinstance(mcp_server,list):
            mcp_server = [mcp_server]
        self.agent = Agent(
            MODEL_NAME,
            mcp_servers=mcp_server,
            system_prompt=SYSTEM_PROMPT
        )
    
    async def chat(self,message,history):
        messages=[]
        # 啟動MCP伺服器
        async with self.agent.run_mcp_servers():
            
            # 使用事件管理的方式來執行
            async with self.agent.iter(
                user_prompt=message,
                message_history=convert_history(SYSTEM_PROMPT,history,model_name=MODEL_NAME)
                ) as run:
                
                # 將每個執行過程的事件列出
                async for node in run:
                    
                    # 如果當前節點是一般問題回應
                    if Agent.is_model_request_node(node):
                        messages.append('')
                        async with node.stream(run.ctx) as request_stream:
                            async for event in request_stream:
                                # LLM的fisrt message
                                if isinstance(event,PartStartEvent):
                                    if isinstance(event.part,TextPart):
                                        messages[-1]+=event.part.content
                                        
                                # LLM的更新message
                                elif isinstance(event,PartDeltaEvent):
                                    if isinstance(event.delta,TextPartDelta):
                                        messages[-1]+=event.delta.content_delta
                                yield messages
                    
                    # 如果當前節點是工具使用
                    elif Agent.is_call_tools_node(node):
                        messages.append('')
                        async with node.stream(run.ctx) as handle_stream:
                            async for event in handle_stream:
                                # 工具開始使用
                                if isinstance(event, FunctionToolCallEvent):
                                    messages[-1]=ChatMessage(content=f'參數:{event.part.args}',metadata={'title':f'🛠️ 使用工具: {event.part.tool_name}'})
                                yield messages
                    
                    # 如果當前節點是結束階段
                    elif Agent.is_end_node(node):
                        assert run.result.output == node.data.output
                        logger.info(f'AI回應:\n{run.result.output}')
                        

async def main():
    registry = ServerRegistry()
    await registry.initialize()
    mcp_server = registry.get_all_servers()
    my_agent = MyAgent(mcp_server=mcp_server)
    
    with gr.Blocks(
            title="AI Chatbot",
        ) as demo:
        gr.Markdown(
            """
            # AI Chatbot
            ### 這是一個基於Pydantic AI的聊天機器人範例，結合了MCP Server
            ### 使用Gradio建立一個簡單的聊天介面，使用串流的方式來顯示回覆，過程中會顯示使用的工具
            """
        )
        gr.ChatInterface(
            fn=my_agent.chat,
            theme="soft",
            type="messages",
            chatbot=gr.Chatbot(
                type="messages",
                avatar_images=(None,'./static/kitty.png')
            ),
            save_history=True,
        )
    demo.launch()
    
    
if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    asyncio.run(main())