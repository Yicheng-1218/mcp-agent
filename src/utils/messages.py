from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
)
from datetime import datetime
from loguru import logger

def convert_history(system_prompt,history,*,model_name=""):
        logger.trace(f'history: {history}')
        pydantic_messages = []
        pydantic_messages.append(
            ModelRequest(
            parts=[
                    SystemPromptPart(
                        content=system_prompt,
                        timestamp=datetime.now(),
                        dynamic_ref=None,
                        part_kind="system-prompt",
                    ),
                ],
                instructions=None,
                kind="request",
            ),
        )
        for msg in history:
            if msg["role"] == "user":
                pydantic_messages.append(
                    ModelRequest(
                        parts=[
                            UserPromptPart(
                                content=msg["content"],
                                timestamp=datetime.now(),
                                part_kind="user-prompt"
                            )
                        ],
                        instructions=None,
                        kind="request"
                    )
                )
            elif msg["role"] == "assistant":
                pydantic_messages.append(
                    ModelResponse(
                        parts=[
                            TextPart(
                                content=msg["content"],
                                part_kind="text"
                            )
                        ],
                        timestamp=datetime.now(),
                        kind="response"
                    )
                )
        return pydantic_messages