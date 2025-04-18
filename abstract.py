"""
Abstract Arc Module

This module provides functionality for creating abstract arcs in an RDLT.
Abstract arcs represent RBS components (R2) within an RDLT, enabling the creation of more generalized 
RBS components for R1 to support EVSA creation.

The module contains the AbstractArc class, which handles:
1. Creation of abstract vertices from center vertices and bridge endpoints
2. Generation of abstract arcs through multiple algorithmic steps
3. Calculation of expanded reusability (eRU) attributes

"""

import utils
from cycle import Cycle
from functools import lru_cache

class AbstractArc:
    """
    A class for creating abstract arcs derived from RBS components.
    
    Attributes:
        R1 (list): List of arc dictionaries from R1 components.
        R2 (list): List of arc dictionaries from R2 (RBS) components.
        In_list (list): List of in-bridge arcs connecting to abstract vertices.
        Out_list (list): List of out-bridge arcs connecting from abstract vertices.
        Centers_list (list): List of center vertices that form abstract vertices.
        Arcs_List (list): List of arcs for processing.
        graph (dict): Adjacency list representation of the R1 graph.
        r2_graph (dict): Adjacency list representation of the R2 graph.
        path_cache (dict): Cache for storing computed paths.
        abstract_vertices (list): List of identified abstract vertices.
    """
    def __init__(self, R1, R2, In_list, Out_list, Centers_list, Arcs_List):
        """
        Initialize the AbstractArc.
        
        Parameters:
            R1 (list): R1 components as a list of arc dictionaries.
            R2 (list): R2 components as a list of arc dictionaries.
            In_list (list): List of in-bridge arcs
            Out_list (list): List of out-bridge arcs
            Centers_list (list): List of center vertices.
            Arcs_List (list): List of arcs with its attributes.
        """
        self.R1 = R1
        self.R2 = R2
        self.In_list = In_list
        self.Out_list = Out_list
        self.Centers_list = Centers_list
        self.Arcs_List = Arcs_List
        
        # Precompute graph structures
        self.graph = utils.build_graph(self.R1)
        self.r2_graph = utils.build_graph(self.R2)
        
        # Cache for paths
        self.path_cache = {}
        
        # Precompute abstract vertices
        self.abstract_vertices = self.find_abstract_vertices()

    def unique(self, Arcs_List):
        """
        Extract all unique vertices from a list of arcs.
        
        Parameters:
            Arcs_List (list): List of arcs as strings, e.g., "x1, x2".

        Returns:
            list: Sorted list of unique vertices.
        """
        unique_vertices = set()
        for arc in Arcs_List:
            # Split each arc string into its vertices and add to the set.
            vertices = arc.split(', ')
            unique_vertices.update(vertices)
        return sorted(unique_vertices)

    def find_abstract_vertices(self):
        """
        Identify all abstract vertices used for creating abstract arcs.
        
        Combines center vertices, in-bridge end vertices, and out-bridge start 
        vertices using set operations for efficient duplicate removal.

        Returns:
            list: List of unique abstract vertices.
        """
        abstract_v_in = {arc.split(', ')[1] for arc in self.In_list}
        abstract_v_out = {arc.split(', ')[0] for arc in self.Out_list}
        return list(set(self.Centers_list) | abstract_v_in | abstract_v_out)

    @lru_cache(maxsize=None)
    def find_paths(self, start, end, max_depth=5):
        """
        Find all paths between two vertices in R2.
        
        Uses memoization through lru_cache to avoid redundant computations.
        
        Parameters:
            start (str): Starting vertex.
            end (str): Ending vertex.
            max_depth (int, optional): Maximum path length to consider. Defaults to 5.
            
        Returns:
            list: List of paths, where each path is a list of vertices.
        """
        if start == end:
            return [[start]]
            
        paths = []
        stack = [(start, [start])]
        
        while stack:
            vertex, path = stack.pop()
            for neighbor in self.r2_graph.get(vertex, []):
                if neighbor not in path:
                    if len(path) < max_depth:
                        new_path = path + [neighbor]
                        if neighbor == end:
                            paths.append(new_path)
                        else:
                            stack.append((neighbor, new_path))
        return paths

    def make_abstract_arcs_stepA(self, abstract_vertices):
        """
        Step A: Create abstract arcs from cycles and paths between abstract vertices.
        
        This first step creates abstract arcs based on:
        1. Self-loops for abstract vertices participating in cycles
        2. Direct paths between abstract vertices
        
        Parameters:
            abstract_vertices (list): List of abstract vertices.
            
        Returns:
            list: List of abstract arc dictionaries with initial attributes.
        """
        abstract_arcs = []
        seen_self_loops = set()
        seen_paths = set()

        # Precompute in-bridge targets
        in_vertices = {arc.split(', ')[1] for arc in self.In_list}
        abstract_set = set(abstract_vertices)

        # Process cycles first
        cycle_instance = Cycle(self.R2)
        cycles = cycle_instance.find_cycles(self.r2_graph)

        for cycle_arcs in filter(None, cycles):
            cycle_vertices = {v for arc in cycle_arcs for v in (arc[0], arc[1])}
            for vertex in cycle_vertices & abstract_set & in_vertices:
                arc = f"{vertex}, {vertex}"
                if arc not in seen_self_loops:
                    seen_self_loops.add(arc)
                    abstract_arcs.append({
                        'r-id': f"A-{len(abstract_arcs)}",
                        'arc': arc,
                        'c-attribute': '0',
                        'l-attribute': '0',
                        'eRU': '0'
                    })

        # Process paths between abstract vertices
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]
            if in_vertex not in abstract_set:
                continue

            for out_vertex in abstract_set - {in_vertex}:
                paths = self.find_paths(in_vertex, out_vertex)
                for path in paths:
                    if len(path) >= 2:
                        path_tuple = tuple(path)
                        if path_tuple not in seen_paths:
                            seen_paths.add(path_tuple)
                            abstract_arcs.append({
                                'r-id': f"A-{len(abstract_arcs)}",
                                'arc': f"{path[0]}, {path[-1]}",
                                'c-attribute': '0',
                                'l-attribute': '0',
                                'eRU': '0'
                            })

        return abstract_arcs

    def make_abstract_arcs_stepB(self, abstract_arcs):
        """
        Step B: Add self-loops for abstract vertices with cyclic paths.
        
        This step identifies in-bridge vertices that have paths returning to themselves
        and adds self-loop abstract arcs for these vertices if they don't already exist.
        
        Parameters:
            abstract_arcs (list): List of abstract arcs from Step A.
            
        Returns:
            list: Updated list of abstract arcs with additional self-loops.
        """
        processed_in_vertices = set()
        
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]
            if in_vertex in processed_in_vertices:
                continue
            processed_in_vertices.add(in_vertex)

            # Use precomputed paths
            paths = self.find_paths(in_vertex, in_vertex)
            if paths:
                for path in paths:
                    if len(path) > 1:
                        filtered_arc = f'{in_vertex}, {in_vertex}'
                        if not any(a['arc'] == filtered_arc for a in abstract_arcs):
                            abstract_arcs.append({
                                'r-id': f"A-{len(abstract_arcs)}",
                                'arc': filtered_arc,
                                'c-attribute': '0',
                                'l-attribute': '0',
                                'eRU': '0'
                            })
        return abstract_arcs

    def make_abstract_arcs_stepC(self, abstract_arcs):
        """
        Step C: Finalize abstract arcs by assigning attributes.
        
        Adds derived attributes (e.g., `c-attribute`, `l-attribute`, `eRU`) to each 
        abstract arc based on the calculated expanded reusability.

        Parameters:
            abstract_arcs (list): List of abstract arcs from Step B.

        Returns:
            list: Finalized list of abstract arcs with computed attributes.
        """
        finalized_arcs = []

        for arc in abstract_arcs:
            # Split arc into start and end vertices.
            eRU = self.calculate_eRU(arc['arc'].split(', ')[0], arc['arc'].split(', ')[1])
            
            # Assign attributes to the abstract arc. 
            finalized_arcs.append({
                'r-id': arc['r-id'],
                'arc': arc['arc'],
                'c-attribute': '0',
                'l-attribute': str(int(eRU) + 1),
                'eRU': str(eRU)
            })

        return finalized_arcs

    def calculate_eRU(self, start, end):
        """
        Compute the Expanded Reusability (eRU) for an abstract arc.
        
        The eRU value represents the potential reusability of an abstract arc,
        considering paths from `start` to `end` in R2 and the L-attributes 
        of the in-bridges in R1.

        Parameters:
            start (str): Start vertex of the abstract arc.
            end (str): End vertex of the abstract arc.

        Returns:
            int: Expanded Reusability (eRU) value for the abstract arc.
        """
        total_eRU = 0  # Initialize total eRU

        # Identify the correct eRU from R2
        path_eRU = 0  # Default value
        for r2_arc in self.R2:
            if r2_arc['arc'] == f"{start}, {end}":
                path_eRU = int(r2_arc.get('eRU', 0))
                break  # Take the first found eRU

        # Special handling for cycles (self-loops)
        if start == end:
            loop_eRU_values = []  # Store eRU values of all valid loops
            for r2_arc in self.R2:
                arc_start, arc_end = r2_arc['arc'].split(', ')
                if arc_start == start or arc_end == end:  # Check arcs forming a loop
                    loop_eRU_values.append(int(r2_arc.get('eRU', 0)))

            if loop_eRU_values:
                path_eRU = max(loop_eRU_values)  # Use the highest loop eRU

        # Sum contributions from in-bridges in R1
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]  # Extract the in-bridge target vertex
            
            if start == in_vertex:
                # Find the corresponding L-attribute in R1
                for arc in self.R1:
                    if arc['arc'] == in_bridge:
                        l_value = int(arc['l-attribute'])  # Get L-value
                        reuse_value = path_eRU + 1  # Add 1 to eRU
                        contribution = l_value * reuse_value
                        total_eRU += contribution  # Accumulate eRU

        return total_eRU