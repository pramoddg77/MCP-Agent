from typing import ParamSpecArgs
from mcp.server.fastmcp import FastMCP
import arxiv
import os
from tavily import TavilyClient

from pydantic import BaseModel

from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP("Academic & Research Tool Server",
            transport_security = TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
            ))

class AcademicPaper(BaseModel):
    title: str
    authors: list
    published: str
    arxiv_id: str
    url: str
    primary_category: str
    abstract: str

@mcp.tool()
def search_arxiv(query: str,max_results: int = 5):
    """
    This tool searched the arxiv database for academic literature, pre-prints and papers. 
    
    Spanning computer Science, physics and mathematics-quantitatives.

    This tool is to be used when the user needs highly-formal proofs, 
    deep mathematics or academic context.

    This tool takes multiple parameters:

    1. Query : The topic is user is intrested in searching/learning for.
    2. max_results : An integer value, determining how many papers to find.
    """

    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []

    for result in client.results(search):
        papers.append(AcademicPaper(
            title = result.title,
            authors = [author.name for author in result.authors],
            published=result.published.strftime("%Y-%m-%d"),
            arxiv_id = result.get_short_id(),
            url=result.pdf_url,
            primary_category = result.primary_category,
            abstract = result.summary.replace("\n", " ")         
            ) 
        )

    return papers
        
@mcp.tool()
def fetch_arxiv_by_id(arxiv_id:str):
    """
    This toll fetches the precise metadata and abstract of a specific academic 
    papaer using its arxiv ID.
    """

    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])

    result = next(client.results(search))
    return AcademicPaper(
            title = result.title,
            authors = [author.name for author in result.authors],
            published=result.published.strftime("%Y-%m-%d"),
            arxiv_id = result.get_short_id(),
            url=result.pdf_url,
            primary_category = result.primary_category,
            abstract = result.summary.replace("\n", " ")
    )

#-----------------------------
# Write TAVILY CODE HERE
#----------------------------

# @mcp.tool()
# def search_web(query: str, max_results: int = 5):
#     """
#     Search from the web for recent information, news, articles, blogs, documentation and 
#     general internet content using Tavily. Useful when the user needs upto date information that my not be available in academic papaers.
#     Use this tool for current events, or when you need web-page
#     """
    
#     client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
#     response = client.search(
#         query = query,
#         max_results=max_results,
#         search_depth = "advanced"    
#     )

#     return [
#         {
#             "title": result.get("title"),
#             "url": result.get("url"),
#             "content": result.get("content"),
#             "score": result.get("score")
#         }
#         for result in response.get("results", [])
#     ]

@mcp.tool()
def search_live_web(query: str, search_depth: str = "basic", max_results: int = 1) -> dict:
    """
    Searches the live internet using Tavily to retrieve clean context, real-time facts, 
    and up-to-date documentation. 
    Use 'advanced' depth if you are looking for highly complex multi-source technical cross-referencing.
    """
    # Acceptable depths for Tavily API: 'basic' or 'advanced'
    depth = "advanced" if search_depth == "advanced" else "basic"

    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    response = tavily_client.search(
        query=query,
        search_depth=depth,
        max_results=max_results,
        include_answer=True
    )
    return response


@mcp.tool()
def extract_webpage_content(url: str) -> dict:
    """
    Extracts high-fidelity, raw text/markdown context directly from one or more specified URLs.
    Bypasses cookie banners, paywalls, and heavy JS scripts to give the LLM pure reading content.
    """
    # Tavily extract API expects strings or a list of strings up to 20 links
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = tavily_client.extract(url)
    return response

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))

    mcp.run()