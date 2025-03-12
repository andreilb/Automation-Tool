import utils

class ContractionPath:
    def __init__(self, R):
        """
        Initializes the contraction path algorithm.

        Parameters:
            - R (list): The RDLT structure containing arcs.
        """
        self.R = R
        print(f"🔍 Input RDLT: {R}")
        self.graph = utils.build_graph(R)
        self.contracted_path = []  # Store the final contracted path
        self.successfully_contracted_arcs = []
        self.failed_contractions = []  # Track failed contractions
        self.unreached_arcs = set(arc['arc'] for arc in R)

    def can_contract(self, arc, superset):
        """
        Determines if an arc can be contracted by checking its incoming arcs.
        """
        try:
            start, end = arc.split(', ')
        except ValueError:
            print(f"Invalid arc format: {arc}. Expected format: 'start, end'.")
            return False

        arc_data = next((a for a in self.R if a['arc'] == arc), None)
        if not arc_data:
            print(f"Arc {arc} not found in RDLT.")
            return False

        # Get the c-attribute of the current arc (default to '0' if missing)
        current_c_attribute = arc_data.get('c-attribute', '0')
        print(f"Checking arc {arc} with c-attribute: {current_c_attribute}")

        # Get all incoming arcs to the end vertex
        incoming_arcs = [a for a in self.R if a['arc'].endswith(f", {end}")]

        # Collect conflicting c-attributes
        conflicting_c_attributes = set()
        for incoming_arc in incoming_arcs:
            incoming_c_attribute = incoming_arc.get('c-attribute', '0')
            if incoming_c_attribute != '0' and incoming_c_attribute not in superset:
                conflicting_c_attributes.add(incoming_c_attribute)

        if conflicting_c_attributes:
            print(f"Conflicting c-attributes found: {conflicting_c_attributes}. Cannot contract {arc}")
            return False

        return True
        
    def contract_segment(self, arc_list, source):
        """
        Contracts arcs in a **single, continuous** path while ensuring connectivity.
        """
        print(f"🔧 Contracting segment: {arc_list}")

        superset = {'0'}
        first_arc = next((a for a in self.R if a['arc'] == arc_list[0]), None)
        if first_arc:
            superset.add(first_arc['c-attribute'])

        dummy_vertex = source
        contracted_arcs = []
        previous_end = None

        for arc in arc_list:
            try:
                start, end = arc.split(', ')
            except ValueError:
                print(f"Invalid arc format: {arc}. Expected format: 'start, end'.")
                self.failed_contractions.append(arc)
                # Add any successfully contracted arcs before the failure
                if contracted_arcs:
                    print(f"Adding partial success: {contracted_arcs}")
                    self.successfully_contracted_arcs.update(contracted_arcs)  # Use update for sets
                return None, []  # Return a tuple to avoid unpacking errors

            if previous_end is not None and start != previous_end:
                print(f"Error: {start} is not connected to {previous_end}. Invalid contraction.")
                self.failed_contractions.append(arc)  # Track as failed
                # Add any successfully contracted arcs before the failure
                if contracted_arcs:
                    print(f"Adding partial success: {contracted_arcs}")
                    self.successfully_contracted_arcs.update(contracted_arcs)  # Use update for sets
                return None, []  # Return a tuple to avoid unpacking errors

            if not self.can_contract(arc, superset):
                print(f"Cannot contract {arc}, constraints not met.")
                self.failed_contractions.append(arc)  # Track as failed
                # Add any successfully contracted arcs before the failure
                if contracted_arcs:
                    print(f"Adding partial success: {contracted_arcs}")
                    self.successfully_contracted_arcs.update(contracted_arcs)  # Use update for sets
                return None, []  # Return a tuple to avoid unpacking errors

            # If the arc can be contracted, add it to the contracted_arcs list
            contracted_arcs.append(arc)
            dummy_vertex += end
            previous_end = end

            # Update the superset with the c-attributes of outgoing arcs
            for outgoing_arc in self.R:
                if outgoing_arc['arc'].startswith(f"{end}, "):
                    superset.add(outgoing_arc['c-attribute'])

            print(f"Dummy vertex updated: {dummy_vertex}")
            self.unreached_arcs.discard(arc)

        # If all arcs in the segment were successfully contracted
        if contracted_arcs:
            print(f"Created final dummy vertex: {dummy_vertex} by merging {contracted_arcs}")
            print(f"Superset after contracting {contracted_arcs}: {superset}")
            self.successfully_contracted_arcs.update(contracted_arcs)  # Use update for sets
            return dummy_vertex, contracted_arcs

        return None, []  # Return a tuple to avoid unpacking errors

    def contract_paths(self):
        """
        Contracts all arcs in the RDLT from source to sink as a **single connected path**.
        Uses self.graph to determine the path and contracts intermediate arcs.
        Tries all possible paths until a valid contraction is found.
        """
        source, sink = utils.get_source_and_target_vertices(self.R)
        print(f"🔗 Attempting contraction from {source} to {sink}")

        self.unreached_arcs = set(arc['arc'] for arc in self.R)
        self.contracted_path = []  # Store the final contracted path
        self.successfully_contracted_arcs = set()  # Use a set to avoid duplicates

        # Find all paths from source to sink using self.graph
        paths = utils.find_path_from_graph(self.graph, source, sink)
        if not paths:
            print(f"🚫 No path found from {source} to {sink}.")
            return [], self.failed_contractions

        # Try each path until a valid contraction is found
        for path in paths:
            arc_path = [f"{path[i]}, {path[i+1]}" for i in range(len(path) - 1)]
            print(f"Trying path: {arc_path}")

            # Attempt to contract the arcs in the path
            result = self.contract_segment(arc_path, source)
            if result[0] is not None:  # Check if contraction was successful
                contracted, successful_arcs = result
                print(f"✅ Successfully contracted path: {successful_arcs}")
                self.contracted_path.extend(successful_arcs)
                break  # Stop after the first successful contraction
            else:
                print(f"🚫 Failed to contract path: {arc_path}")

        # If no full path was contracted, check for partial contractions
        if not self.contracted_path and self.successfully_contracted_arcs:
            print(f"Partial contraction found: {list(self.successfully_contracted_arcs)}")
            self.contracted_path = list(self.successfully_contracted_arcs)

        # Check if the contracted path includes the source and sink
        if self.contracted_path:
            path_start = self.contracted_path[0].split(", ")[0]
            path_end = self.contracted_path[-1].split(", ")[1]

            if path_start == source and path_end == sink:
                print(f"Successfully contracted path from {source} to {sink}: {self.contracted_path}")
            else:
                print(f"Contracted path does not fully reach the sink ({sink}). Incomplete path: {self.contracted_path}")
        else:
            print("No valid contraction path found.")

        return self.contracted_path, self.failed_contractions