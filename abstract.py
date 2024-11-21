import utils

class AbstractArc:
    def __init__(self, R1, R2, In_list, Out_list, Centers_list, Arcs_List):
        # Initialize the variables
        self.R1 = R1
        self.R2 = R2
        self.In_list = In_list
        self.Out_list = Out_list
        self.Centers_list = Centers_list
        self.Arcs_List = Arcs_List
        self.abstract_arcs = []  # Store the abstract arcs

    def unique(self, Arcs_List):
        # Extract all unique vertices from the list of arcs
        unique_vertices = set()
        for arc in Arcs_List:
            vertices = arc.split(', ')  # Split the arc string into vertices
            unique_vertices.update(vertices)  # Add vertices to the set
        return sorted(unique_vertices)  # Return the sorted list of unique vertices
    
    # def find_abstract_vertices(self):
    #     # Find abstract vertices which include Centers or vertices containing in-bridges
    #     abstract_v_in_list = [arc.split(', ')[1] for arc in self.In_list]
    #     abstract_v_out_list = [arc.split(', ')[0] for arc in self.Out_list]
    #     abstract_vertices = self.Centers_list + abstract_v_in_list + abstract_v_out_list
    #     return self.unique(abstract_vertices)

    def find_abstract_vertices(self):
        abstract_v_in_list = [arc.split(', ')[1] for arc in self.In_list]
        abstract_v_out_list = [arc.split(', ')[0] for arc in self.Out_list]
        abstract_vertices = self.Centers_list + abstract_v_in_list + abstract_v_out_list
        abstract_vertices = list(set(abstract_vertices))  # Remove duplicates
        return abstract_vertices

    def make_abstract_arcs_stepA(self, abstract_vertices):
        abstract_arcs = []  # List to hold the final abstract arcs
        seen_pairs = set()  # Track processed vertex pairs to avoid redundant path calculations
        all_paths = []  # List to hold all the raw paths found as arcs

        # Convert R2 to a graph for easy pathfinding
        arc_list = [arc['arc'] for arc in self.R2]
        graph = utils.list_to_graph(arc_list)

        print(f"Abstract vertices: {abstract_vertices}")

        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]  # Get the end vertex of the in-bridge
            if in_vertex not in abstract_vertices:
                print(f"Skipping in-bridge {in_vertex} as it's not in abstract vertices")
                continue

            for out_vertex in abstract_vertices:
                if in_vertex != out_vertex:
                    # Only compute paths once for a pair of vertices
                    vertex_pair = (in_vertex, out_vertex)
                    if vertex_pair in seen_pairs:
                        continue  # Skip if we've already processed this pair
                    seen_pairs.add(vertex_pair)

                    # Find all paths between in_vertex and out_vertex
                    paths = utils.find_all_paths(graph, in_vertex, out_vertex)
                    print(f"Paths from {in_vertex} to {out_vertex}: {paths}")

                    if paths:
                        for path in paths:
                            # Now treat the path directly as arcs (pairs of vertices)
                            arcs = []
                            for i in range(len(path) - 1):
                                arc = f"{path[i]}, {path[i+1]}"  # Arc as a string of the form 'start_vertex, end_vertex'
                                arcs.append(arc)  # Add the arc to the list
                            all_paths.append(arcs)  # Add the entire set of arcs for this path to all_paths

                            # Debugging: print arcs and abstract_vertices
                            print(f"Arcs: {arcs}")
                            print(f"Abstract vertices: {abstract_vertices}")

                            # Filter the arcs based on abstract vertices
                            # For multi-arc paths, get the start vertex of the first arc and the end vertex of the last arc
                            if len(path) > 1:
                                start_vertex = path[0]
                                end_vertex = path[-1]
                                # Check if both start and end vertices are in the abstract_vertices
                                if start_vertex in abstract_vertices and end_vertex in abstract_vertices:
                                    filtered_arc = f"{start_vertex}, {end_vertex}"
                                    abstract_arcs.append(filtered_arc)  # Add the filtered arc to the abstract arcs list
                                    print(f"Filtered arc (start-end): {filtered_arc}")
                            else:
                                # For single arcs, just add them directly
                                for arc in arcs:
                                    # Filter out any arcs that don't have both start and end in the abstract vertices
                                    if arc.split(', ')[0] in abstract_vertices and arc.split(', ')[1] in abstract_vertices:
                                        abstract_arcs.append(arc)  # Add the valid arc to the list
                                        print(f"Filtered arc: {arc}")

        # Print out the final abstract arcs and all raw paths as arcs
        print(f"Abstract arcs after Step A: {abstract_arcs}")
        print(f"All paths found as arcs: {all_paths}")  # Print all raw paths (as arcs) for reference

        return abstract_arcs


    # def make_abstract_arcs_stepB(self, abstract_arcs):
    # # Ensure abstract_arcs is a list
    #     if isinstance(abstract_arcs, tuple):
    #         abstract_arcs = list(abstract_arcs)
        
    #     # Set to keep track of in-vertex pairs that we've already processed for self-loops
    #     processed_in_vertices = set()

    #     # Iterate through all in-bridges to check for self-loops
    #     for in_bridge in self.In_list:
    #         # Extract the in-vertex (second part of the in-bridge)
    #         in_vertex = in_bridge.split(', ')[1]

    #         # Skip if this in_vertex has already been processed for a self-loop
    #         if in_vertex in processed_in_vertices:
    #             continue

    #         # Mark this vertex as processed for self-loop
    #         processed_in_vertices.add(in_vertex)

    #         # Find self-loop paths (in_vertex to itself)
    #         paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
    #         print(f"Self-loop paths from {in_vertex} to itself: {paths}")

    #         # If self-loops are found, add them to the abstract arcs
    #         if paths:
    #             # Append the self-loop path to the abstract arcs
    #             formatted_arc = f"{in_vertex}, {in_vertex}"
    #             if formatted_arc not in abstract_arcs:
    #                 abstract_arcs.append(formatted_arc)  # Add self-loop arc to abstract arcs
    #                 print("Formatted abstract arc (self-loop):", formatted_arc)

    #     # Debug: Print the abstract arcs after processing
    #     print(f"Abstract arcs after Step B: {abstract_arcs}")

    #     return abstract_arcs

    def make_abstract_arcs_stepB(self, abstract_arcs):
    # Ensure abstract_arcs is a list
        if isinstance(abstract_arcs, tuple):
            abstract_arcs = list(abstract_arcs)

        # Set to keep track of in-vertex pairs that we've already processed for self-loops
        processed_in_vertices = set()

        # Iterate through all in-bridges to check for self-loops
        for in_bridge in self.In_list:
            # Extract the in-vertex (second part of the in-bridge)
            in_vertex = in_bridge.split(', ')[1]

            # Skip if this in_vertex has already been processed for a self-loop
            if in_vertex in processed_in_vertices:
                continue

            # Mark this vertex as processed for self-loop
            processed_in_vertices.add(in_vertex)

            # Find paths from the in_vertex that eventually form a self-loop (in_vertex to in_vertex)
            paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
            # print(f"Paths from {in_vertex} to itself: {paths}")

            if paths:
                for path in paths:
                    # For multi-arc paths, get the start vertex of the first arc and the end vertex of the last arc
                    if len(path) > 1:
                        start_vertex = path[0]
                        end_vertex = path[-1]
                        # Check if both start and end vertices are the same as in_vertex
                        if start_vertex == in_vertex and end_vertex == in_vertex:
                            # This forms a self-loop, so we add it
                            filtered_arc = f"{start_vertex}, {end_vertex}"
                            if filtered_arc not in abstract_arcs:
                                abstract_arcs.append(filtered_arc)
                                # print(f"Filtered arc (self-loop): {filtered_arc}")

            # If self-loops are found directly, add them as well
            formatted_arc = f"{in_vertex}, {in_vertex}"
            if formatted_arc not in abstract_arcs:
                abstract_arcs.append(formatted_arc)  # Add self-loop arc to abstract arcs
                # print(f"Formatted abstract arc (self-loop): {formatted_arc}")

        # Debug: Print the abstract arcs after processing
        # print(f"Abstract arcs after Step B: {abstract_arcs}")

        return abstract_arcs


    def make_abstract_arcs_stepC(self, abstract_arcs):
        # Finalize the abstract arcs by setting attributes
        finalized_arcs = []

        for arc in abstract_arcs:
            # If arc is a string, split it into start and end vertices
            if isinstance(arc, str):
                start, end = arc.split(', ')
            else:
                # Assuming it's already a tuple or list (start, end)
                start, end = arc

            # Set c-attribute to 0 (unconstrained)
            c_attribute = 0

            # Calculate eRU as derived l-attribute + 1
            eRU = self.calculate_eRU(start, end)

            # Calculate the derived l-attribute based on calculated eRU
            l_attribute = eRU + 1

            # Create the abstract arc with its attributes
            finalized_arcs.append({
                'arc': f"{start}, {end}",
                'c-attribute': c_attribute,
                'l-attribute': l_attribute,
                'eRU': eRU
            })

        # print(f"Finalized abstract arcs after Step C: {finalized_arcs}")
        return finalized_arcs


    def calculate_eRU(self, start, end):
        # Calculate the eRU for the abstract arc to get derived l-attribute
        eRU = 0

        # Iterate over the in-bridges to compute the eRU
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]  # Get the out-vertex of the in-bridge

            # Only consider in-bridges that correspond to the start vertex
            if start == in_vertex:
                # Find the corresponding l-attribute for the in-bridge in R1
                for arc in self.R1:
                    if arc['arc'] == in_bridge:
                        base_eRU = arc['l-attribute']
                        try:
                            base_eRU = int(base_eRU)
                        except ValueError:
                            base_eRU = 0  # Default if parsing fails

                        # Calculate reusability based on R2 paths
                        reusability = self.get_path_reusability(in_vertex, start, end)

                        # Update the l-attribute based on reusability and the base l-attribute
                        eRU += base_eRU * (reusability + 1)

        return eRU


    def get_path_reusability(self, in_vertex, start, end):
        """
        Calculate the eRU for paths between start and end vertices, including the case for self-loops.
        eRU is the reusability + 1.

        Args:
            in_vertex (str): The in-vertex used as an entry point for path calculation.
            start (str): The start vertex of the path.
            end (str): The end vertex of the path.

        Returns:
            int: The eRU for the path (reusability + 1).

        Remarks: this still manually computes for eRU instead of referencing to the initially calculated eRU from R2
        """
        eRU = 0

        # Check for self-loop at in_vertex (in_vertex to itself)
        if start == end and start == in_vertex:
            # Calculate eRU for self-loop (direct path from in_vertex to itself)
            paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
            # print(f"Calculating eRU for self-loop at {in_vertex}: {paths}")

            if paths:
                for path in paths:
                    # eRU for self-loop can be based on how many times in_vertex is traversed
                    eRU += path.count(in_vertex)

            # Finalize eRU for self-loop
            eRU += 1
            # print(f"eRU for self-loop at {in_vertex}: {eRU}")
            return eRU  # Return eRU for self-loop immediately

        # Find all paths between start and end vertices in R2
        paths = utils.find_all_paths(self.R2, start, end)
        # print(f"Calculating eRU for path from {start} to {end} through {in_vertex}")

        if paths:
            for path in paths:
                # If the in_vertex is part of the path, count its occurrences for reusability (same as eRU)
                if in_vertex in path:
                    eRU += path.count(in_vertex)

        # print(f"eRU for path {start} to {end} through {in_vertex}: {eRU}")
        return eRU

    # def print_abstract_arcs(self):
    #     # Print the abstract arcs with their attributes
    #     for arc in self.abstract_arcs:
    #         print(f"Abstract Arc: {arc['arc']} | c-attribute: {arc['c-attribute']} | l-attribute: {arc['l-attribute']} | eRU: {arc['eRU']}")

if __name__ == '__main__':
    # Define the input data
    R1 = [
        {'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0},
        {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
        {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}
    ]
    Arcs_List = ['x1, x2', 'x2, x3', 'x3, x2', 'x2, x4', 'x3, x4', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7']
    L_attribute_list = ['1', '2', '3', '4', '1', '6', '7', '7', '5', '1']
    C_attribute_list = ['a', '0', '0', '0', '0', '0', 'b', 'a', 'a', '0']
    Centers_list = ['x2']
    In_list = ['x1, x2', 'x6, x2']
    Out_list = ['x4, x5', 'x4, x6']
    R2 = [
        {'r-id': 'R2-1', 'arc': 'x2, x3', 'l-attribute': '2', 'c-attribute': '0', 'eRU': 2},
        {'r-id': 'R2-2', 'arc': 'x3, x2', 'l-attribute': '3', 'c-attribute': '0', 'eRU': 2},
        {'r-id': 'R2-3', 'arc': 'x2, x4', 'l-attribute': '4', 'c-attribute': '0', 'eRU': 0},
        {'r-id': 'R2-4', 'arc': 'x3, x4', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}
    ]

    # Initialize the AbstractArc class
    AA = AbstractArc(R1=R1, R2=R2, In_list=In_list, Out_list=Out_list, Centers_list=Centers_list, Arcs_List=Arcs_List)

    # Step 1: Find abstract vertices
    abstract_vertices = AA.find_abstract_vertices()
    # Step 2: Create abstract arcs (Step A)
    prepreFinal_abstractList = AA.make_abstract_arcs_stepA(abstract_vertices)
    # Step 3: Add self-loops (Step B)
    preFinal_abstractList = AA.make_abstract_arcs_stepB(prepreFinal_abstractList)
    # Step 4: Finalize abstract arcs (Step C)
    final_abstractList = AA.make_abstract_arcs_stepC(preFinal_abstractList)
    # Step 5: Add abstract arcs to R1
    updated_R1 = R1 + final_abstractList  # Simplified merging for demonstration
    # print(f"Updated R1 with Abstract Arcs: {updated_R1}")
