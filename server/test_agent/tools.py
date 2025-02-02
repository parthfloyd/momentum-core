import logging
from typing import List

from langchain.tools import tool
from server.utils.github_helper import GithubService
from server.parse import (
    get_flow,
    get_node_by_id,
    get_pydantic_class,
    get_pydantic_classes,
)
from server.utils.graph_db_helper import Neo4jGraph

neo4j_graph = Neo4jGraph()

class CodeTools:
    """
    A class that provides code tools for generating code for endpoint identifiers.
    """
   
    # Annotate the function with the tool decorator from LangChain
    @tool("Get accurate code context for given endpoint identifier")
    def get_code(identifier, project_id):
      """
      Get the code for the specified endpoint identifier.
      Parameters:
      - identifier: The identifier of the endpoint.
      - project_id: The exact project id of the project.
      Returns:
      - The code for the specified endpoint identifier.
      """
      code = ""
      nodes = get_flow(identifier, project_id)
      for node in nodes:
        node = get_node_by_id(node, project_id)
        code += (
            "\n"
            + node["id"]
            + "\n code: \n"
            + GithubService.fetch_method_from_repo(node)
        )
      return code


    @tool("Get pydantic class definition for a single class name")  
    def get_pydantic_definition( classname, project_id):
      """
        Get the pydantic class definition for given class name
      Parameters:
      - classname: The name of a class.
      - project_id: The id of the project.
      Returns:
      - The pydantic class definition for the specified class name.
      """
      return get_pydantic_class(classname, project_id)

    @tool("Get the pydantic class definition for list of class names")  
    def get_pydantic_definitions_tool( classnames: List[str], project_id):
      """
      Get the pydantic class definition for list of class names
      Parameters:
      - classnames: The list of the names of pydantic classes.
      - project_id: The id of the project.
      Returns:
      - The code definitions for the specified pydantic classes.
      """
      definitions = ""
      try:
        definitions = get_pydantic_classes(classnames, project_id)
      except Exception as e:
        logging.exception(f"project_id : {project_id} something went wrong during fetching definition for {classnames}", e)
      return definitions

    @tool("Query the code knowledge graph with specific directed questions using natural language and project id and return the query result")
    def ask_knowledge_graph(query: str, project_id) -> str:
      """
        Query the code knowledge graph using natural language questions.
        DO NOT USE THIS TOOL TO QUERY CODE DIRECTLY. USE GET CODE TOOL TO FETCH CODE
        The knowledge graph contains information from various database tables including:
        - inference: key-value pairs of inferred knowledge about APIs and their constituting functions
        - endpoints: API endpoint paths and identifiers
        - explanation: code explanations for function identifiers
        - pydantic: pydantic class definitions
        Parameters:
        - query: A natural language question to ask the knowledge graph.\
        - project_id: The project id metadata for the project bein evaluated 
        Returns:
        - The result of querying the knowledge graph with the provided question.
            """
      from server.knowledge_graph.knowledge_graph import KnowledgeGraph

      return KnowledgeGraph(project_id).query(query, project_id)