"""
RDLT Utilities Module

This module provides a collection of utility functions for the RDLT.
It includes functions for graph operations, path finding, vertex and arc manipulations, and other
common operations used throughout the RDLT framework.

Key functionalities:
- Graph construction and traversal operations
- Path finding and analysis algorithms
- Cycle detection in directed graphs
- Data format conversions and manipulations
- Arc and vertex extraction utilities
"""

def find_all_paths(graph, start, end, path=None):
    """
    Finds all paths from the start vertex to the end vertex in an RDLT.

    This function recursively explores all possible paths between the start and end vertices, ensuring no cycles
    by checking if a vertex is revisited within the same path.

    Parameters:
        - graph (dict): A dictionary representing the graph where keys are vertices and values are lists of neighboring vertices.
        - start (str): The starting vertex for the path search.
        - end (str): The target vertex for the path search.
        - path (list, optional): A list that keeps track of the current path being explored. Defaults to None.

    Returns:
        list: A list of lists, where each inner list represents a path from start to end.
    """
    # Initialize the path list if it is not passed as an argument
    if path is None:
        path = []
    # Add the current node to the path
    path.append(start)
    # If the start node is the same as the end node, we've found a path
    if start == end:
        return [path]
    # If no paths are found, return an empty list
    if start not in graph:
        return []
    # List to store all paths
    paths = []
    # Recur for all the neighbors of the current node
    for neighbor in graph[start]:
        # Ensure no cycles by checking if the neighbor is not already in the path
        if neighbor not in path:
            # Find paths from the neighbor to the end
            new_paths = find_all_paths(graph, neighbor, end, path.copy())  # use path.copy() to avoid modifying the same path
            paths.extend(new_paths)  # Add all found paths to the paths list
    return paths

def format_path(path):
    """
    Formats a list of vertices into a list of arcs.

    Converts a path of vertices into a readable format of arcs (pairs of start and end vertices).

    Parameters:
        - path (list): A list of vertices representing a path.

    Returns:
        list: A list of formatted arcs as strings in the form "start, end".
    """
    formatted_arcs = []
    for i in range(len(path) - 1):
        formatted_arcs.append(f"{path[i]}, {path[i + 1]}")
    return formatted_arcs

def list_to_graph(arc_list):
    """
    Converts a list of arcs into a graph represented as a dictionary of adjacency lists.

    Parameters:
        - arc_list (list): A list of strings where each string represents an arc (e.g., "x, y").

    Returns:
        dict: A dictionary where keys are vertices and values are lists of neighboring vertices.
    """
    graph = {}
    for arc in arc_list:
        start, end = arc.split(', ')  # Split the arc into start and end vertices
        if start not in graph:
            graph[start] = []
        if end not in graph:
            graph[end] = []
        graph[start].append(end)  # Add the directed edge to the graph
    return graph

def extract_vertices(arc_list):
    """
    Extracts all unique vertices from a list of arcs.

    Parameters:
        - arc_list (list): A list of strings representing arcs in the form "x, y".

    Returns:
        list: A sorted list of unique vertices (both start and end vertices from the arcs).
    """
    # Extract all unique 'x's from the list
    unique_xs = set()
    for arc in arc_list:
        xs = arc.split(', ')
        unique_xs.update(xs)
    unique_xs_list = sorted(unique_xs)
    return unique_xs_list

def dfs_with_cycle_detection(graph, start, visited=None, rec_stack=None):
    """
    Performs Depth First Search (DFS) to detect cycles in a directed graph.

    The function tracks visited vertices and ensures that no cycles are encountered during the traversal.

    Parameters:
        - graph (dict): A dictionary representing the graph.
        - start (str): The starting vertex for the DFS.
        - visited (set, optional): A set of visited vertices. Defaults to None.
        - rec_stack (set, optional): A set of vertices currently in the recursion stack. Defaults to None.

    Returns:
        bool: True if a cycle is detected, False otherwise.
    """
    if visited is None:
        visited = set()
    if rec_stack is None:
        rec_stack = set()

    visited.add(start)
    rec_stack.add(start)

    for neighbor in graph.get(start, []):
        if neighbor not in visited:  # If the neighbor has not been visited
            if dfs_with_cycle_detection(graph, neighbor, visited, rec_stack):
                return True
        elif neighbor in rec_stack:  # Cycle detected
            return True

    rec_stack.remove(start)  # Remove the vertex from recursion stack
    return False

def find_paths(R, source, target, visited=None):
    """
    Finds all paths from a source vertex to a target vertex in the given RDLT, without revisiting nodes.

    Parameters:
        - R (list): A list of dictionaries, each representing an arc with an 'arc' field containing the edge.
        - source (str): The starting vertex for the path search.
        - target (str): The target vertex for the path search.
        - visited (set, optional): A set of visited vertices to prevent revisiting. Defaults to None.

    Returns:
        list: A list of paths, each represented as a list of vertices from source to target.
    """
    if visited is None:
        visited = set()
    visited.add(source)
    
    # If source equals target, return path
    if source == target:
        return [[source]]
    
    paths = []
    # Explore all arcs (outgoing edges)
    for arc in R:
        arc_source, arc_target = arc['arc'].split(', ')
        if arc_source == source and arc_target not in visited:
            # Recursively find paths from the arc target
            for path in find_paths(R, arc_target, target, visited.copy()):
                paths.append([source] + path)
    return paths

def find_path_from_graph(graph, start, end, path=[]):
    """
    Finds all paths from start to end in the given graph.

    Parameters:
        - graph (dict): A dictionary representing the graph, where keys are vertices and values are lists of adjacent vertices.
        - start (str): The starting vertex for the path search.
        - end (str): The target vertex for the path search.
        - path (list, optional): The current path being explored. Defaults to [].

    Returns:
        list: A list of paths, each represented as a list of vertices from start to end.
    """
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            # Recursively call find_path_from_graph (not find_paths)
            new_paths = find_path_from_graph(graph, node, end, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths

def get_source_and_target_vertices(R):
    """
    Identifies the source and target vertices that result in the longest path or involve the most vertices.

    Parameters:
        - R (list): List of dictionaries representing arcs in the RDLT.

    Returns:
        tuple: A tuple containing the source and target vertices of the longest path.
    """
    from collections import defaultdict

    # Build graph as adjacency list
    graph = defaultdict(list)
    for r in R:
        x, y = r['arc'].split(', ')
        graph[x].append(y)

    # Function to perform DFS and track longest path
    def dfs(vertex, visited, path):
        visited.add(vertex)
        path.append(vertex)
        longest_path = list(path)  # Copy current path as the longest
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                current_path = dfs(neighbor, visited, path)
                if len(current_path) > len(longest_path):  # Compare path lengths
                    longest_path = current_path
        path.pop()  # Backtrack
        visited.remove(vertex)
        return longest_path

    # Identify potential source and target vertices
    all_x = {r['arc'].split(', ')[0] for r in R}
    all_y = {r['arc'].split(', ')[1] for r in R}
    source_candidates = list(all_x - all_y)
    target_candidates = list(all_y - all_x)

    # Evaluate longest path for each source vertex
    longest_path = []
    source_vertex = None
    for source in source_candidates:
        visited = set()
        path = dfs(source, visited, [])
        if len(path) > len(longest_path):
            longest_path = path
            source_vertex = source

    # Identify the endpoint of the longest path
    target_vertex = longest_path[-1] if longest_path else None

    # print(f"Source Vertex: {source_vertex}")
    # print(f"Target Vertex: {target_vertex}")

    return source_vertex, target_vertex

def get_r_id(arc, R):
    """
    Retrieves the r-id associated with a given arc.

    Parameters:
        - arc (str): The arc for which to retrieve the r-id.
        - R (list): The list of arcs, where each arc is a dictionary containing 'arc' and 'r-id'.

    Returns:
        str or None: The r-id corresponding to the given arc, or None if not found.
    """
    # Search through R to find the r-id associated with the given arc
    for arc in R:
        if arc['arc'] == arc:
            return arc['r-id']
    return None  # Return None if the arc is not found

def get_arc_from_rid(rid, R1):
    """
    Retrieve the arc corresponding to the given r-id from R1.
    
    Parameters:
        - rid (str): The unique identifier of the arc.
        - R1 (list of dict): The list of arcs with their attributes in R1.

    Returns:
        str: The arc corresponding to the r-id, or None if not found.
    """
    for r in R1:
        if r['r-id'] == rid:
            return r['arc']
    return None

def build_graph(R):
        """
        Builds a directed graph from the list of arcs.
        """
        graph = {}
        for arc in R:
            start, end = arc['arc'].split(', ')
            if start not in graph:
                graph[start] = []
            graph[start].append(end)
        return graph
        