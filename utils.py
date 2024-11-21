def find_all_paths(graph, start, end, path=None):
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
    """Format the path as a list of arcs."""
    formatted_arcs = []
    for i in range(len(path) - 1):
        formatted_arcs.append(f"{path[i]}, {path[i + 1]}")
    return formatted_arcs

def list_to_graph(arc_list):
    """Convert a list of arcs into a graph (dictionary of adjacency lists)."""
    graph = {}
    for arc in arc_list:
        start, end = arc.split(', ')  # Split the arc into start and end vertices
        if start not in graph:
            graph[start] = []
        if end not in graph:
            graph[end] = []
        graph[start].append(end)  # Add the directed edge to the graph
    return graph

def dfs_with_cycle_detection(graph, start, visited=None, rec_stack=None):
    """Perform DFS to detect cycles in a directed graph."""
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
