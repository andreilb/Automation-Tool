"""
RDLT Input Processing Module

This module implements the Input_RDLT class for reading, parsing, and processing RDLT input files. 

The module provides functionality to:
1. Parse RDLT input files containing RDLT structure and components
2. Extract vertices, arcs, and their associated attributes 
3. Identify center elements and IN/OUT components
4. Process the extracted data into hierarchical RDLT structures (R1, R2, etc.)
5. Compute expanded Reusability (eRU) values for cycle analysis
6. Prepare the processed data for further analysis with the EVSA (Expanded Vertex Simplification Algorithm).
"""

from pathlib import Path
import utils
from cycle import Cycle

class Input_RDLT:
    """
    The Input_RDLT class reads and processes RDLT input files.
    
    This class parses RDLT files, extracting RDLT components such as arcs, vertices, centers, and 
    IN/OUT lists. It processes these components into structured data, computes cycle-based metrics,
    and prepares the data for further analysis with algorithms like EVSA (Expanded Vertex 
    Simplification Algorithm).
    
    RDLT files have a specific structure:
    - R section: Lists arcs with their c-attributes and l-attributes
    - CENTER section: Identifies center vertices for sub-structures
    - IN section: Lists incoming arcs to the structure
    - OUT section: Lists outgoing arcs from the structure
    
    The class handles the extraction of these sections and processes them into R1, R2, etc. structures,
    where:
    - R1: Contains arcs not associated with any center
    - R2, R3, etc.: Contain arcs associated with each center listed in the CENTER section

    Attributes:
        filepath (Path): Path to the RDLT input file.
        contents (dict): Dictionary holding the contents of the RDLT file (arcs, centers, in, out).
        Cycle_List (list): List to hold cycle data.
        Centers_list (list): List of centers extracted from the RDLT file.
        In_list (list): List of IN components extracted from the RDLT file.
        Out_list (list): List of OUT components extracted from the RDLT file.
        Arcs_List (list): List of arcs (edges) extracted from the RDLT file.
        Vertices_List (list): List of unique vertices extracted from the arcs.
        C_attribute_list (list): List of c-attributes associated with the arcs.
        L_attribute_list (list): List of l-attributes associated with the arcs.
        user_input_to_evsa (list): Processed RDLT data structured for EVSA.
    """
    
    def __init__(self, filepath):
        """
        Initializes the Input_RDLT object and reads the RDLT data from the provided file.

        This method opens the RDLT input file, reads its contents, and organizes the data into
        categories (R, CENTER, IN, OUT). It initializes all necessary attributes and data structures 
        that will be populated during evaluation.

        Parameters:
            filepath (str): Path to the RDLT file. Can be a relative or absolute path.
        """
        self.filepath = Path(filepath)  # Ensure the filepath is set correctly
        self.contents = {'R': [], 'CENTER': [], 'IN': [], 'OUT': []}
        self.Cycle_List = []  # Initialize cycle list

        # Read the file and categorize the data into different sections
        with open(self.filepath) as file:
            current_obj = 'R'
            for line in file:
                line = line.strip()
                if line.startswith('CENTER'):
                    current_obj = 'CENTER'
                elif line.startswith('IN'):
                    current_obj = 'IN'
                elif line.startswith('OUT'):
                    current_obj = 'OUT'
                else:
                    self.contents[current_obj].append(line)

        # Process and add data to the lists: Centers, In, Out
        self.Centers_list = [center.strip() for line in self.contents['CENTER'] for center in line.split(',') if center.strip()]
        self.In_list = [line.strip() for line in self.contents['IN'] if line.strip()]
        self.Out_list = [line.strip() for line in self.contents['OUT'] if line.strip()]
        self.Arcs_List = []
        self.Vertices_List = []
        self.C_attribute_list = []
        self.L_attribute_list = []
        self.user_input_to_evsa = []

    def evaluate(self):
        """
        Evaluates the RDLT data by extracting and processing various components.
        
        This method performs several key operations:
        1. Extracts arcs, vertices, and their associated c-attributes and l-attributes from the input data
        2. Organizes components into formatted structures and prints debug information
        3. Processes the RDLT structure into hierarchical components (R1, R2, etc.):
           - R2, R3, etc.: Components inside the RBS structures
           - R1: Components outside the RBS
        4. Transforms the processed data into a standardized format for further analysis
        5. Computes eRU values for cycle components in R1
        
        The processed data is stored in the user_input_to_evsa attribute for further analysis
        with the EVSA algorithm.
        
        Example format of processed data in user_input_to_evsa:
        [
            {"R2": [{
                "r-id": "R2-0",
                "arc": "vertex1, vertex2", 
                "l-attribute": "value",
                "c-attribute": "value",
                "eRU": 0
            }, ...]},
            {"R1": [...]}
        ]
        """
        
        def extract_R(line):
            """
            Extracts the arc, c-attribute, and l-attribute from a given line in the R section.

            This function parses a comma-separated line from the R section of the RDLT file and
            extracts the arc (vertex pair) along with its associated c-attribute and l-attribute.
            The expected format is: "vertex1, vertex2, c-attribute, l-attribute".

            Parameters:
                line (str): A line containing arc data, separated by commas.

            Returns:
                dict or None: 
                    - If valid: A dictionary containing 'arc', 'c-attribute', and 'l-attribute' keys.
                    - If invalid (less than 4 elements): None.
            """
            L = line.split(', ')
            if len(L) < 4:
                return None  # Return None for invalid lines
            return {
                'arc': f"{L[0]}, {L[1]}",
                'c-attribute': f"{L[2]}",
                'l-attribute': f"{L[3]}"
            }

        def extract_vertices(arc_list):
            """
            Extracts unique vertices from a list of arcs.

            This function takes a list of arcs in the format "vertex1, vertex2" and
            extracts all unique vertices, returning them as a sorted list.

            Parameters:
                arc_list (list): A list of arcs, where each arc is a string in the format "vertex1, vertex2".

            Returns:
                list: A sorted list of all unique vertices found in the arcs.
            """
            unique_xs = set()
            for arc in arc_list:
                xs = arc.split(', ')
                unique_xs.update(xs)
            return sorted(unique_xs)

        # Extracting arcs and attributes from the 'R' section of the input data
        R_list = [extract_R(x) for x in self.contents['R'] if extract_R(x) is not None]
        
        # Extract the arcs, vertices, and attributes
        self.Arcs_List = [i['arc'] for i in R_list]
        self.Vertices_List = extract_vertices(self.Arcs_List)
        self.C_attribute_list = [i['c-attribute'] for i in R_list]
        self.L_attribute_list = [i['l-attribute'] for i in R_list]

        def convert_arc_format(arc):
            """
            Converts an arc from the "vertex1, vertex2" format to the "(vertex1, vertex2)" format.

            This function is used for display and debugging purposes to format arcs
            in a more readable parenthetical notation.

            Parameters:
                arc (str): An arc in the format "vertex1, vertex2".

            Returns:
                str: The arc in the format "(vertex1, vertex2)".
            """
            return f"({arc.split(', ')[0]}, {arc.split(', ')[1]})"
        
        def convert_arc_list_format(arc_list):
            """
            Converts a list of arcs from "vertex1, vertex2" format to "(vertex1, vertex2)" format.

            This function is used for display and debugging purposes to format a list of arcs
            in a more readable parenthetical notation.

            Parameters:
                arc_list (list): A list of arcs, each in the format "vertex1, vertex2".

            Returns:
                list: A list of arcs, each in the format "(vertex1, vertex2)".
            """
            return [convert_arc_format(arc) for arc in arc_list]

        # Print the extracted data for debugging
        print(f"\nInput RDLT: ")
        print('-' * 20)
        print(f"Arcs List ({len(self.Arcs_List)}): ", convert_arc_list_format(self.Arcs_List))
        print(f"Vertices List ({len(self.Vertices_List)}): ", self.Vertices_List)
        print(f"C-attribute List ({len(self.C_attribute_list)}): ", self.C_attribute_list)
        print(f"L-attribute List ({len(self.L_attribute_list)}): ", self.L_attribute_list)
  
        if self.Centers_list:
            print('-' * 20)
            print(f"RBS components:")
            print('-' * 20)
            print(f"Centers ({len(self.Centers_list)}): ", self.Centers_list)
            print(f"In ({len(self.In_list)}): ", convert_arc_list_format(self.In_list))
            print(f"Out ({len(self.Out_list)}): ", convert_arc_list_format(self.Out_list))
        print('=' * 60)

        # Process the RDLT structure for R2, R3, etc., based on centers and arcs
        rdlts_raw = [{f"R{i + 2}-{self.Centers_list[i]}": []} for i in range(len(self.Centers_list))]

        def extract_rdlt(rdlt):
            """
            Extracts and processes RDLT data for each center, excluding in- and out-arcs.

            This function processes a raw RDLT dictionary by:
            1. Identifying the center vertex from the key (e.g., "R2-centerVertex")
            2. Finding all arcs that include the center vertex
            3. Excluding arcs that are in the IN or OUT lists
            4. Collecting all vertices involved in the remaining arcs
            5. Creating a final RDLT with all arcs that connect these vertices

            Parameters:
                rdlt (dict): A dictionary representing the raw RDLT in the format {"Rn-centerVertex": []}.

            Returns:
                dict or None: 
                    - If valid: A processed RDLT dictionary in the format {"Rn": [list of arc strings]}.
                    - If invalid key format: None.
            """
            for key, value in rdlt.items():
                if '-' in key:  # Ensure key is in the expected format (e.g., "R2-center")
                    r, center_vertex = key.split('-')
                    # Find all arcs that include the center vertex
                    rdlt[key] = [arc for arc in self.Arcs_List if center_vertex in arc]
                    # Exclude arcs that are in the IN or OUT lists
                    final_rdlt = [arc for arc in rdlt[key] if arc not in self.In_list and arc not in self.Out_list]
                    # Get all vertices involved in the remaining arcs
                    final_vertices = extract_vertices(final_rdlt)
                    # Create a final RDLT with all arcs that connect these vertices
                    final_rdlt = [arc for arc in self.Arcs_List if (arc.split(', ')[0] in final_vertices and arc.split(', ')[1] in final_vertices)]
                    return {r: final_rdlt}
                else:
                    print(f"[WARNING] Skipping invalid key format: {key}")
                    return None  # Return None for invalid entries

        rdlts = []
        for r in rdlts_raw:
            rdlt_result = extract_rdlt(r)
            if rdlt_result is not None:
                rdlts.append(rdlt_result)

        # Extracting remaining arcs for R1 (those that were not used in R2, R3, etc.)
        used_arcs = []
        for rdlt in rdlts:
            for r_list in rdlt.values():
                for r in r_list:
                    used_arcs.append(r)
        rdlts.append({"R1": [arc for arc in self.Arcs_List if arc not in used_arcs]})

        def final_transform_R(rdlt):
            """
            Transforms RDLT data into a final format for analysis, adding arc information and attributes.

            This function takes a processed RDLT dictionary and enhances it with additional arc
            information, including r-id, attributes, and an initial eRU value. This format is 
            required for the EVSA algorithm and cycle analysis.

            Parameters:
                rdlt (dict): A dictionary representing a processed RDLT in the format {"Rn": [list of arc strings]}.

            Returns:
                dict: A transformed RDLT dictionary in the format:
                     {"Rn": [
                         {
                             "r-id": "Rn-index",
                             "arc": "vertex1, vertex2",
                             "l-attribute": "value",
                             "c-attribute": "value",
                             "eRU": 0
                         },
                         ...
                     ]}
            """
            for key, value in rdlt.items():
                return {key: [{
                    "r-id": f"{key}-{self.Arcs_List.index(x)}",
                    "arc": self.Arcs_List[self.Arcs_List.index(x)],
                    "l-attribute": self.L_attribute_list[self.Arcs_List.index(x)],
                    "c-attribute": self.C_attribute_list[self.Arcs_List.index(x)],
                    'eRU': 0
                } for x in value]}

        self.user_input_to_evsa = [final_transform_R(rdlt) for rdlt in rdlts]

        # Compute eRU for R1
        R1 = self.getR('R1')
        if R1:
            self._compute_eRU(R1)

    def _compute_eRU(self, R1):
        """
        Computes the eRU (expanded Reusability) values for arcs in R1 based on cycle detection.
        
        This method:
        1. Uses the Cycle class to detect cycles within the R1 component
        2. For each detected cycle:
           a. Extracts the l-attributes of all arcs in the cycle
           b. Identifies the critical arc (ca) value as the minimum l-attribute in the cycle
           c. Updates the eRU value of each arc in the cycle to the critical arc value
        
        The eRU value represents the "expanded reusability" measure for each arc, which is
        determined by the cycles it participates in and the minimum l-attribute values in those cycles.
        
        Parameters:
            R1 (list): The R1 structure containing arcs and their attributes.
        """
        # Detect cycles in R1
        cycle_instance = Cycle(R1)
        cycle_R1 = cycle_instance.evaluate_cycle()

        if cycle_R1:
            # Iterate over each cycle
            for cycle_data in cycle_R1:
                cycle_arcs = cycle_data['cycle']
                cycle_l_attributes = []

                # Iterate over the arcs in the cycle
                for cycle_arc in cycle_arcs:
                    r_id, arc_name = cycle_arc.split(": ")
                    arc_name = arc_name.strip()

                    # Get the actual arc from R1 using r-id
                    actual_arc = utils.get_arc_from_rid(r_id, R1)

                    if actual_arc:
                        # Find the matching arc in R1
                        matching_arc = next((r for r in R1 if r['arc'] == actual_arc), None)
                        if matching_arc:
                            l_attribute = matching_arc.get('l-attribute', None)
                            if l_attribute is not None:
                                cycle_l_attributes.append(int(l_attribute))  # Convert to int
                            else:
                                print(f"Warning: 'l-attribute' not found for arc {actual_arc}")
                        else:
                            print(f"Warning: No matching arc found for {actual_arc} in R1")
                    else:
                        print(f"Warning: No arc found in R1 for r-id {r_id}")

                # Compute the critical arc value (minimum l-attribute in the cycle)
                ca = min(cycle_l_attributes) if cycle_l_attributes else None

                if ca is not None:
                    # Update eRU for arcs in the cycle
                    for cycle_arc in cycle_arcs:
                        r_id, arc_name = cycle_arc.split(": ")
                        arc_name = arc_name.strip()

                        # Get the actual arc from R1 using r-id
                        actual_arc = utils.get_arc_from_rid(r_id, R1)

                        if actual_arc:
                            # Find the matching arc in R1
                            matching_arc = next((r for r in R1 if r['arc'] == actual_arc), None)
                            if matching_arc:
                                # Update eRU to the critical arc's 'ca' value
                                matching_arc['eRU'] = ca
    
    # get only R1 components for EVSA processing
    def getRs(self):
        """
        Fetches all RDLT structures except for R1.
        
        This method returns a list of dictionaries containing the R2, R3, etc. structures,
        which represent components associated with the centers specified in the RDLT input file.
        These components are used for EVSA (Expanded Vertex Simplification Algorithm) processing.
        
        Returns:
            list: List of dictionaries, each containing an RDLT structure (R2, R3, etc.)
                 in the format {"Rn": [list of arc dictionaries]}.
                 
                 Example:
                 [
                     {"R2": [{
                         "r-id": "R2-0",
                         "arc": "vertex1, vertex2",
                         "l-attribute": "value",
                         "c-attribute": "value",
                         "eRU": 0
                     }, ...]},
                     {"R3": [...]}
                 ]
        """
        return [R for R in self.user_input_to_evsa if "R1" not in R.keys()]
    
    # get only R2 components for EVSA processing
    def getR(self, R): 
        """
        Fetches a specific RDLT structure (e.g., R1, R2, etc.) by its identifier.
        
        This method searches through the user_input_to_evsa list to find the requested
        RDLT structure based on its identifier (e.g., 'R1', 'R2', etc.).
        
        Parameters:
            R (str): The identifier of the RDLT structure (e.g., 'R1', 'R2', etc.).
        
        Returns:
            list or str: 
                - If found: A list of dictionaries, each representing an arc in the specified 
                  RDLT structure with its attributes (r-id, arc, l-attribute, c-attribute, eRU).
                - If not found: A warning message indicating that the requested structure 
                  is not defined or is missing.
                  
            Example of a returned list:
            [
                {
                    "r-id": "R1-0",
                    "arc": "vertex1, vertex2",
                    "l-attribute": "value",
                    "c-attribute": "value",
                    "eRU": 0
                },
                ...
            ]
        """
        for dictionary in self.user_input_to_evsa:
            if dictionary is not None and R in dictionary:  # Check if dictionary is not None
                return dictionary[R]
        return f"[WARNING] {R} has not been defined or is missing."