"""This module defines a graph for a travel chatbot using LangGraph and LangChain."""
from src.tools.tools import WeatherTool, RagTool
from src.utils.text_processing import format_retrieved_chunks

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.language_models import BaseLanguageModel

from src.agent.prompts import Prompts
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

class TravelGraphState(TypedDict):
    query: str
    intent: str
    context: str
    locations: list[str]
    weather_info: str
    final_answer: str
    chat_history: list[dict]


class TravelChatbotGraph(StateGraph):

    def __init__(self, llm: BaseLanguageModel, prompts):
        super().__init__(TravelGraphState)
        self.llm = llm
        self.prompts = prompts
        self.tools = self.set_up_tools()
        self.graph = self.build_graph()

    def set_up_tools(self):
        self.weather_tool = WeatherTool()
        self.rag_tool = RagTool()
        return 
    
    
    def build_graph(self):
        builder = StateGraph(TravelGraphState)
        # add nodes
        builder.add_node("oracle_node", self.oracle_node)
        builder.add_node("get_loc_from_query_node", self.get_loc_from_query)
        builder.add_node("get_loc_from_book_node", self.get_loc_from_book)
        builder.add_node("book_retriever_node", self.book_retriever_node)
        builder.add_node("get_weather_node", self.get_weather)
        builder.add_node("final_response_node", self.final_response)
        builder.add_node("fallback_node", self.fallback_node)
        builder.add_node("chitchat_node", self.chitchat_node)

        # add edges
        builder.set_entry_point("oracle_node")
        builder.add_conditional_edges("oracle_node",
                                      self.get_intent,
                                    {
                                        "weather": "get_loc_from_query_node",
                                        "book": "book_retriever_node",
                                        "combined": "get_loc_from_book_node",
                                        "chitchat": "chitchat_node",
                                        "irrelevant": "fallback_node",
                                    })
        builder.add_edge("get_loc_from_query_node", "get_weather_node")
        builder.add_edge("get_weather_node", "final_response_node")
        builder.add_edge("book_retriever_node", "final_response_node")
        builder.add_edge("get_loc_from_book_node", "get_weather_node")
        builder.add_edge("chitchat_node", END)
        builder.add_edge("fallback_node", END)
        builder.add_edge("final_response_node", END)

        return builder.compile()
    
    def get_intent(self, state: TravelGraphState):
        if "weather" in state['intent']:
            return "weather"
        elif "book" in state['intent'] or "travel" in state['intent']:
            return "book"
        elif "combined" in state['intent']:
            return "combined"
        elif "chitchat" in state['intent']:
            return "chitchat"
        else:
            return "irrelevant"
                                
    
    async def oracle_node(self, state: TravelGraphState):
        chain = self.prompts.create_oracle_prompt_template() | self.llm | JsonOutputParser()
        response = await chain.ainvoke({"query": state["query"]})
        intent = response.get("category", "irrelevant")
        return ({"intent": intent})

    async def get_loc_from_query(self,  state: TravelGraphState):
        chain = self.prompts.create_get_locations_from_query_prompt_template() | self.llm | JsonOutputParser()
        response = await chain.ainvoke({"query": state["query"]})

        return ({"locations": response.get("locations", [])})

    async def get_loc_from_book(self,  state: TravelGraphState):
        chain = self.prompts.create_get_locations_from_book_prompt_template() | self.llm | JsonOutputParser()
        formatted_context = self.rag_tool.run(state["query"])
        response = await chain.ainvoke({"context": formatted_context, "query": state["query"]})

        return ({"locations": response.get("locations", []), "context": formatted_context})

    async def book_retriever_node(self,  state: TravelGraphState):
        formatted_context = self.rag_tool.run({"query":state["query"]})

        return ({"context": formatted_context})

    async def get_weather(self,  state: TravelGraphState):
        weather_info = await self.weather_tool.ainvoke({"locations":state["locations"]})
        return ({"weather_info": weather_info})

    async def final_response(self,  state: TravelGraphState):
        chain = self.prompts.create_final_response_prompt_template() | self.llm | StrOutputParser()
        response = await chain.ainvoke({"query": state["query"], "context": state.get("context", ""), "weather_info": state.get("weather_info", "")})
        return ({"final_answer": response})

    async def fallback_node(self,  state: TravelGraphState):
        
        fallback_message = """I'm sorry, but I can only assist with travel-related or book-related inquiries. If you have any questions about travel destinations, weather, or related topics, feel free to ask!"""
        return ({"final_answer": fallback_message})

    async def chitchat_node(self,  state: TravelGraphState):
        
        chain  = self.prompts.create_chitchat_prompt_template() | self.llm | StrOutputParser()
        response = await chain.ainvoke({"query": state["query"], "chat_history": state.get("chat_history", [])})
        return ({"final_answer": response})
