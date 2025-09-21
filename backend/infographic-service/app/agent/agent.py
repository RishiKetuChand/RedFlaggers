import os
import asyncio
import uuid
from typing import Optional

from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from .prompts import return_instructions_root
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

def create_rag_retrieval_tool(rag_corpus: str) -> VertexAiRagRetrieval:
    return VertexAiRagRetrieval(
        name='retrieve_rag_documentation',
        description=(
            'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
        ),
        rag_resources=[
            rag.RagResource(
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )

def create_infographic_agents(rag_corpus: str, model_name: str = "gemini-2.5-flash"):
    ask_vertex_retrieval = create_rag_retrieval_tool(rag_corpus)

    root_agent = Agent(
        model=model_name,
        name='ask_rag_agent',
        description="The primary research assistant. It collaborates with internal documents and generates detailed json responses.",
        instruction=return_instructions_root(),
        tools=[
            ask_vertex_retrieval,
        ]
    )
    
    return root_agent


class AgentRunner:
    def __init__(self, app_name: str, user_id: str, session_id_prefix: str):
        self.app_name = app_name
        self.user_id = user_id
        self.session_id_prefix = session_id_prefix
        self.session_service = InMemorySessionService()

    async def setup_session_and_runner(self, root_agent: Agent):
        session_id = f"{self.session_id_prefix}_{uuid.uuid4().hex[:8]}"
        session = await self.session_service.create_session(
            app_name=self.app_name, 
            user_id=self.user_id, 
            session_id=session_id
        )
        runner = Runner(
            agent=root_agent, 
            app_name=self.app_name, 
            session_service=self.session_service
        )
        return session, runner, session_id

    async def call_agent_async(self, query: str, root_agent: Agent) -> str:
        content = types.Content(role='user', parts=[types.Part(text=query)])
        session, runner, session_id = await self.setup_session_and_runner(root_agent)
        
        events = runner.run_async(
            user_id=self.user_id, 
            session_id=session_id, 
            new_message=content
        )

        final_response = ""
        async for event in events:
            if event.is_final_response():
                final_response = event.content.parts[0].text
                break
        print(final_response)
        return final_response
