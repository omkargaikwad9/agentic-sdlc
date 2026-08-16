from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from langchain_core.messages import SystemMessage

from states.state import AgentState
from llm.groq_llm_client import get_llm

from utils.travers import (
    scan_repository as scan_repository_impl,
    read_file as read_file_impl,
    search_code as search_code_impl,
    get_project_metadata as get_project_metadata_impl,
    _write_file as write_file_impl,
    _git_diff as git_diff_impl
)

from langchain_core.tools import tool

def create_repository_tools(
    repository_root: str,
):

    @tool
    def scan_repository() -> list[dict]:
        """
        Scan the target repository.

        Returns metadata about Python files,
        imports, classes, functions and calls.
        """

        return scan_repository_impl(
            repository_root
        )

    @tool
    def get_project_metadata() -> dict:
        """
        Get project information such as
        language, framework, dependencies
        and test framework.
        """

        return get_project_metadata_impl(
            repository_root
        )

    @tool
    def read_file(
        file_path: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        """
        Read a file from the target repository.

        file_path must be relative to the
        repository root.
        """

        return read_file_impl(
            repository_root,
            file_path,
            start_line,
            end_line,
        )

    @tool
    def search_code(
        query: str,
    ) -> list[dict]:
        """
        Search for text inside the target repository.
        """

        return search_code_impl(
            repository_root,
            query,
        )

    @tool
    def write_file(
        file_path: str,
        content: str,
    ) -> dict:
        """
        Write or update a text file inside the target repository.

        Use this only after understanding the existing code
        and determining the required implementation changes.
        """

        return write_file_impl(
            repository_root,
            file_path,
            content,
        )

    @tool
    def git_diff() -> dict:
        """
        Show the current uncommitted changes made
        to the target repository.

        Use this after modifying files to inspect
        exactly what changed.
        """

        return git_diff_impl(repository_root)

    return [
        scan_repository,
        get_project_metadata,
        read_file,
        search_code,
        write_file,
        git_diff
    ]

    

# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph(repository_root: str):

    # --------------------------------------------
    # Create tools for THIS repository
    # --------------------------------------------

    tools = create_repository_tools(
        repository_root
    )

    # --------------------------------------------
    # Create LLM
    # --------------------------------------------

    llm = get_llm()

    # --------------------------------------------
    # Bind tools to LLM
    # --------------------------------------------

    llm_with_tools = llm.bind_tools(
        tools
    )

    # --------------------------------------------
    # Model node
    # --------------------------------------------

    def call_model(state):

        response = llm_with_tools.invoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    # --------------------------------------------
    # Tool node
    # --------------------------------------------

    tool_node = ToolNode(tools)

    # --------------------------------------------
    # Build graph
    # --------------------------------------------

    graph_builder = StateGraph(
        AgentState
    )

    graph_builder.add_node(
        "model",
        call_model
    )

    graph_builder.add_node(
        "tools",
        tool_node
    )

    # START → model

    graph_builder.add_edge(
        START,
        "model"
    )

    # model → tools OR END
    graph_builder.add_conditional_edges(
        "model",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        }
    )

    # tools → model

    graph_builder.add_edge(
        "tools",
        "model"
    )

    return graph_builder.compile()