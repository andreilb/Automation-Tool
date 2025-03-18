from pathlib import Path

class Input_RDLT:
    """
    The Input_RDLT class reads RDLT input from a specified file and extracts various components such as arcs, vertices,
    center, IN, and OUT lists. It supports the evaluation of the extracted data and provides access to RDLT
    structures (R1, R2, etc.) for further processing.

    Attributes:
        filepath (Path): Path to the RDLT input file.
        contents (dict): Dictionary holding the contents of the RDLT file (arcs, centers, in, out).
        Cycle_List (list): List to hold cycle data (not used directly in this class).
        Centers_list (list): List of centers extracted from the RDLT file.
        In_list (list): List of IN components extracted from the RDLT file.
        Out_list (list): List of OUT components extracted from the RDLT file.
        Arcs_List (list): List of arcs (edges) extracted from the RDLT file.
        Vertices_List (list): List of unique vertices extracted from the arcs.
        C_attribute_list (list): List of c-attributes associated with the arcs.
        L_attribute_list (list): List of l-attributes associated with the arcs.
        user_input_to_evsa (list): Processed RDLT data structured for EVSA (Expanded Vertex Simplification Algorithm).
    """
    
    def __init__(self, filepath):
        """
        Initializes the Input_RDLT object and reads the RDLT data from the provided file.

        Parameters:
            - filepath (str): Path to the RDLT file. The default file path can be set in main.py.
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
        Evaluates the RDLT data by extracting and categorizing arcs, vertices, and attributes.
        This method also processes RDLT data into R1, R2, etc., and prepares it for use in further analysis.
        """
        
        def extract_R(line):
            """
            Extracts the arc, c-attribute, and l-attribute from a given line.

            Parameters:
                - line (str): A line containing arc data, separated by commas.

            Returns:
                dict or None: A dictionary containing the arc and its attributes, or None for invalid lines.
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

            Parameters:
                - arc_list (list): A list of arcs.

            Returns:
                list: A sorted list of unique vertices.
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

        # Print the extracted data for debugging
        # print('-' * 60)
        print(f"\nInput RDLT: ")
        print('-' * 20)
        print(f"Arcs List ({len(self.Arcs_List)}): ", self.Arcs_List)
        print(f"Vertices List ({len(self.Vertices_List)}): ", self.Vertices_List)
        print(f"C-attribute List ({len(self.C_attribute_list)}): ", self.C_attribute_list)
        print(f"L-attribute List ({len(self.L_attribute_list)}): ", self.L_attribute_list)
        if self.Centers_list:
            print('-' * 20)
            print(f"RBS components:")
            print('-' * 20)
            print(f"Centers ({len(self.Centers_list)}): ", self.Centers_list)
            print(f"In ({len(self.In_list)}): ", self.In_list)
            print(f"Out ({len(self.Out_list)}): ", self.Out_list)
        print('=' * 60)

        # Process the RDLT structure for R2, R3, etc., based on centers and arcs
        rdlts_raw = [{f"R{i + 2}-{self.Centers_list[i]}": []} for i in range(len(self.Centers_list))]

        def extract_rdlt(rdlt):
            """
            Extracts and processes RDLT data for each center, excluding in- and out-arcs.

            Parameters:
                - rdlt (dict): A dictionary representing the current RDLT.

            Returns:
                dict or None: Processed RDLT data for the specified center, or None for invalid data.
            """
            for key, value in rdlt.items():
                if '-' in key:  # Ensure key is in the expected format (e.g., "R2-center")
                    r, center_vertex = key.split('-')
                    rdlt[key] = [arc for arc in self.Arcs_List if center_vertex in arc]
                    final_rdlt = [arc for arc in rdlt[key] if arc not in self.In_list and arc not in self.Out_list]
                    final_vertices = extract_vertices(final_rdlt)
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
            Transforms RDLT data into a final format for analysis, adding arc information, attributes, and eRU values.

            Parameters:
                - rdlt (dict): A dictionary representing a processed RDLT.

            Returns:
                dict: Transformed RDLT data with additional attributes.
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

        # Print final results for debugging (dictionary)
        # print("Extracted RDLT Data (dict):")
        # print('-' * 30)
        # for rdlt in self.user_input_to_evsa:
        #     print(rdlt)

    def getRs(self):
        """
        Fetches all RDLT structures except for R1.

        Returns:
            list: List of RDLT structures (R2, R3, etc.).
        """
        return [R for R in self.user_input_to_evsa if "R1" not in R.keys()]

    def getR(self, R):
        """
        Fetches a specific RDLT structure (e.g., R1, R2, etc.) by its identifier.

        Parameters:
            - R (str): The identifier of the RDLT structure (e.g., 'R1').

        Returns:
            dict or str: The requested RDLT structure, or a warning message if not found.
        """
        for dictionary in self.user_input_to_evsa:
            if dictionary is not None and R in dictionary:  # Check if dictionary is not None
                return dictionary[R]
        return f"[WARNING] {R} has not been defined or is missing."

if __name__ == '__main__':
    # Example usage of the Input_RDLT class
    input_data = Input_RDLT('your_file_path_here.txt')  # Make sure to set the correct path to the RDLT file
    input_data.evaluate()  # Evaluates the RDLT input data
    print(input_data.getRs())  # This will print R2, R3, etc. without R1
    print(input_data.getR('R1'))  # This will print R1 structure



# from pathlib import Path

# class Input_RDLT:
#     """
#     The Input_RDLT class reads RDLT input from a specified file and extracts various components such as arcs, vertices,
#     center, IN, and OUT lists. It supports the evaluation of the extracted data and provides access to RDLT
#     structures (R1, R2, etc.) for further processing.
#     """
    
#     def __init__(self, filepath):
#         """
#         Initializes the Input_RDLT object and reads the RDLT data from the provided file.

#         Parameters:
#             filepath (str): Path to the RDLT file.
#         """
#         self.filepath = Path(filepath)  # Ensure the filepath is set correctly
#         self.contents = {'R': [], 'CENTER': [], 'IN': [], 'OUT': []}
#         self.Cycle_List = []  # Initialize cycle list

#         # Read the file and categorize the data into different sections
#         with open(self.filepath) as file:
#             current_obj = 'R'
#             for line in file:
#                 line = line.strip()
#                 if line.startswith('CENTER'):
#                     current_obj = 'CENTER'
#                 elif line.startswith('IN'):
#                     current_obj = 'IN'
#                 elif line.startswith('OUT'):
#                     current_obj = 'OUT'
#                 else:
#                     self.contents[current_obj].append(line)

#         # Process and add data to the lists: Centers, In, Out
#         self.Centers_list = [center.strip() for line in self.contents['CENTER'] for center in line.split(',') if center.strip()]
#         self.In_list = [line.strip() for line in self.contents['IN'] if line.strip()]
#         self.Out_list = [line.strip() for line in self.contents['OUT'] if line.strip()]
#         self.Arcs_List = []  # List of arcs
#         self.Vertices_List = []  # List of vertices
#         self.C_attribute_list = []  # List of c-attributes
#         self.L_attribute_list = []  # List of l-attributes
#         self.user_input_to_evsa = []  # List of processed RDLT data
#         self.r2_dict = {}  # Initialize dictionary for R2 data

#     def evaluate(self):
#         """
#         Evaluates the RDLT data by extracting and categorizing arcs, vertices, and attributes.
#         This method also processes RDLT data into R1, R2, etc., and prepares it for use in further analysis.
#         """
        
#         def extract_R(line):
#             """Extract arc, c-attribute, and l-attribute from a line."""
#             L = line.split(', ')
#             if len(L) < 4:
#                 return None
#             return {
#                 'arc': f"{L[0]}, {L[1]}",
#                 'c-attribute': f"{L[2]}",
#                 'l-attribute': f"{L[3]}"
#             }

#         def extract_vertices(arc_list):
#             """Extract unique vertices from a list of arcs."""
#             unique_xs = set()
#             for arc in arc_list:
#                 xs = arc.split(', ')
#                 unique_xs.update(xs)
#             return sorted(unique_xs)

#         # Extracting arcs and attributes from the 'R' section of the input data
#         R_list = [extract_R(x) for x in self.contents['R'] if extract_R(x) is not None]
        
#         # Extract the arcs, vertices, and attributes
#         self.Arcs_List = [i['arc'] for i in R_list]
#         self.Vertices_List = extract_vertices(self.Arcs_List)
#         self.C_attribute_list = [i['c-attribute'] for i in R_list]
#         self.L_attribute_list = [i['l-attribute'] for i in R_list]

#         # Process the RDLT structure for R2, R3, etc., based on centers and arcs
#         rdlts_raw = [{f"R{i + 2}-{self.Centers_list[i]}": []} for i in range(len(self.Centers_list))]

#         def extract_rdlt(rdlt):
#             """Extract and process RDLT data for each center, excluding in- and out-arcs."""
#             for key, value in rdlt.items():
#                 if '-' in key:
#                     r, center_vertex = key.split('-')
#                     rdlt[key] = [arc for arc in self.Arcs_List if center_vertex in arc]
#                     final_rdlt = [arc for arc in rdlt[key] if arc not in self.In_list and arc not in self.Out_list]
#                     final_vertices = extract_vertices(final_rdlt)
#                     final_rdlt = [arc for arc in self.Arcs_List if (arc.split(', ')[0] in final_vertices and arc.split(', ')[1] in final_vertices)]
#                     return {r: final_rdlt}
#                 else:
#                     print(f"[WARNING] Skipping invalid key format: {key}")
#                     return None

#         rdlts = []
#         for r in rdlts_raw:
#             rdlt_result = extract_rdlt(r)
#             if rdlt_result is not None:
#                 rdlts.append(rdlt_result)

#         # Extracting remaining arcs for R1
#         used_arcs = [arc for rdlt in rdlts for r_list in rdlt.values() for arc in r_list]
#         rdlts.append({"R1": [arc for arc in self.Arcs_List if arc not in used_arcs]})

#         def final_transform_R(rdlt):
#             """Transforms RDLT data into a final format for analysis."""
#             for key, value in rdlt.items():
#                 return {key: [{
#                     "r-id": f"{key}-{self.Arcs_List.index(x)}",
#                     "arc": self.Arcs_List[self.Arcs_List.index(x)],
#                     "l-attribute": self.L_attribute_list[self.Arcs_List.index(x)],
#                     "c-attribute": self.C_attribute_list[self.Arcs_List.index(x)],
#                     'eRU': 0
#                 } for x in value]}

#         self.user_input_to_evsa = [final_transform_R(rdlt) for rdlt in rdlts]

#         # Construct the r2_dict from the transformed RDLT data
#         self.r2_dict = {f"R{i + 2}": rdlt for i, rdlt in enumerate(self.user_input_to_evsa) if f"R{i + 2}" in rdlt}

#         # Print final results for debugging
#         print("Extracted RDLT Data (dict):")
#         print('-' * 30)
#         for rdlt in self.user_input_to_evsa:
#             print(rdlt)

#     def getRs(self):
#         """Fetches all RDLT structures except for R1."""
#         return [R for R in self.user_input_to_evsa if "R1" not in R.keys()]

#     def getR(self, R):
#         """Fetches a specific RDLT structure (e.g., R1, R2, etc.) by its identifier."""
#         for dictionary in self.user_input_to_evsa:
#             if dictionary is not None and R in dictionary:
#                 return dictionary[R]
#         return f"[WARNING] {R} has not been defined or is missing."
