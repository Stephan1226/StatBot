import argparse
import json
import re
from typing import List, Tuple

import mcp.server.fastmcp as fastmcp
from langchain.tools import tool
from services.rag_pipeline import search


_METRIC_PATTERNS: List[Tuple[str, List[str]]] = [
    ("OPS", [r"ops(?![a-z0-9])", r"on[- ]?base plus slugging", r"\bobp[+ ]+slg\b"]),
    ("ERA", [r"era(?![a-z0-9])", r"earned run average"]),
    ("FIP", [r"fip(?![a-z0-9])", r"fielding independent pitching"]),
    ("wRC+", [r"wrc\+(?![a-z0-9])", r"weighted runs created plus", r"wrc(?![a-z0-9])"]),
    ("WAR", [r"war(?![a-z0-9])", r"wins above replacement"]),
]


def _extract_metric_keyword(text: str) -> str:
    """Heuristically extract the sabermetric keyword from text."""
    normalized = text.lower()
    for keyword, patterns in _METRIC_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, normalized):
                return keyword
    return "unknown"


def _run_rag(query: str) -> dict:
    """Core RAG search shared by LangChain tool and MCP server."""
    try:
        results = search(query, k=3)

        chunks = []
        for doc in results:
            chunks.append({
                "content": doc.page_content,
                "page": doc.metadata.get("page", "unknown"),
                "source": doc.metadata.get("source", "unknown")
            })

        # Try to infer the metric name from the query first, then from retrieved content.
        combined_text = query + "\n" + "\n".join(doc.page_content for doc in results)
        keyword = _extract_metric_keyword(combined_text)

        response = {
            "keyword": keyword,
            "chunks": chunks
        }

        return response
    except Exception as e:
        return {"error": str(e)}


@tool
def sabermetrics_rag_tool(query: str) -> str:
    """
    Search for baseball sabermetrics definitions and explanations in the knowledge base.
    Use this tool when asked about OPS, ERA, FIP, wRC+, WAR, or other baseball metrics.

    Args:
        query: The search query (e.g., "OPS definition", "wRC+ meaning").

    Returns:
        A JSON string containing the keyword (derived from query/content) and relevant text chunks from the PDF.
    """
    return json.dumps(_run_rag(query), ensure_ascii=False)


def create_mcp_server(host: str = "127.0.0.1", port: int = 8000) -> fastmcp.FastMCP:
    """Instantiate FastMCP server with sabermetrics RAG tool registered."""
    server = fastmcp.FastMCP(
        name="sabermetrics-rag-mcp",
        instructions="RAG over sabermetrics.pdf; use sabermetrics_rag to fetch chunks for OPS/ERA/FIP/wRC+/WAR queries.",
        host=host,
        port=port,
    )

    @server.tool(
        name="sabermetrics_rag",
        description="Search sabermetrics.pdf for OPS, ERA, FIP, wRC+, WAR definitions and explanations. Returns keyword+chunks.",
    )
    async def sabermetrics_rag(query: str) -> dict:
        return _run_rag(query)

    return server


def _cli():
    parser = argparse.ArgumentParser(description="Run sabermetrics RAG MCP server or quick test.")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio",
                        help="Transport protocol for MCP server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for SSE/HTTP transports.")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE/HTTP transports.")
    parser.add_argument("--mount-path", default="/", dest="mount_path", help="Mount path for SSE transport.")
    parser.add_argument("--test-query", help="Run a single RAG query and print JSON, then exit.")
    args = parser.parse_args()

    if args.test_query:
        print(json.dumps(_run_rag(args.test_query), ensure_ascii=False))
        return

    server = create_mcp_server(host=args.host, port=args.port)
    server.run(transport=args.transport, mount_path=args.mount_path if args.transport == "sse" else None)


if __name__ == "__main__":
    _cli()
