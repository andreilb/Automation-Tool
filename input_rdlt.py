from pathlib import Path

class Input_RDLT:
    """
    Input_RDLT class reads RDLT input from a specified file and extracts various components such as arcs, vertices,
    center, IN, and OUT lists. It also supports evaluation of the extracted data and provides access to RDLT
    structures (R1, R2, etc.).
    """
    
    def __init__(self, filepath):
        """
        Initializes the Input_RDLT object and reads the RDLT data from the provided file.

        Parameters:
            filepath (str): Path to the RDLT file. Default is 'rdlt_text/sample_rdlt.txt', refer to main.py to change file path.
        """
        self.filepath = Path(filepath)  # Ensure the filepath is set correctly
        self.contents = {'R': [], 'CENTER': [], 'IN': [], 'OUT': []}
        self.Cycle_List = []  # Initialize cycle list

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
        self.Centers_list = self.Centers_list = [center.strip() for line in self.contents['CENTER'] for center in line.split(',') if center.strip()]
        self.In_list = [line.strip() for line in self.contents['IN'] if line.strip()]
        self.Out_list = [line.strip() for line in self.contents['OUT'] if line.strip()]
        self.Arcs_List = []
        self.Vertices_List = []
        self.C_attribute_list = []
        self.L_attribute_list = []
        self.user_input_to_evsa = []

    def evaluate(self):
        def extract_R(line):
            L = line.split(', ')
            if len(L) < 4:
                # print(f"[WARNING] Skipping invalid line: {line}")
                return None  # Return None for invalid lines
            return {
                'arc': f"{L[0]}, {L[1]}",
                'c-attribute': f"{L[2]}",
                'l-attribute': f"{L[3]}"
            }

        def extract_vertices(arc_list):
            unique_xs = set()
            for arc in arc_list:
                xs = arc.split(', ')
                unique_xs.update(xs)
            return sorted(unique_xs)

        # Extracting arcs and attributes from 'R' section
        # Filter out any None values that result from invalid lines
        R_list = [extract_R(x) for x in self.contents['R'] if extract_R(x) is not None]
        
        # Extract the arcs, vertices, and attributes
        self.Arcs_List = [i['arc'] for i in R_list]
        self.Vertices_List = extract_vertices(self.Arcs_List)
        self.C_attribute_list = [i['c-attribute'] for i in R_list]
        self.L_attribute_list = [i['l-attribute'] for i in R_list]

        # Print the extracted data
        print('-' * 60)
        print(f"Input RDLT: ")
        print('-' * 20)
        print(f"Arcs List ({len(self.Arcs_List)}): ", self.Arcs_List)
        print(f"Vertices List ({len(self.Vertices_List)}): ", self.Vertices_List)
        print(f"C-attribute List ({len(self.C_attribute_list)}): ", self.C_attribute_list)
        print(f"L-attribute List ({len(self.L_attribute_list)}): ", self.L_attribute_list)
        print('-' * 20)
        print(f"RBS components:")
        print('-' * 20)
        print(f"Centers ({len(self.Centers_list)}): ", self.Centers_list)
        print("In: ", self.In_list)
        print("Out: ", self.Out_list)
        print('-' * 60)

        # Process the RDLT structure for R2, R3, etc.
        rdlts_raw = [{f"R{i + 2}-{self.Centers_list[i]}": []} for i in range(len(self.Centers_list))]

        def extract_rdlt(rdlt):
            for key, value in rdlt.items():
                # Check if the key contains the expected format (R1-center)
                if '-' in key:
                    # Split the key safely
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

        # Extraction Process for R1
        used_arcs = []
        for rdlt in rdlts:
            for r_list in rdlt.values():
                for r in r_list:
                    used_arcs.append(r)
        rdlts.append({"R1": [arc for arc in self.Arcs_List if arc not in used_arcs]})

        def final_transform_R(rdlt):
            for key, value in rdlt.items():
                return {key: [{
                    "r-id": f"{key}-{self.Arcs_List.index(x)}",
                    "arc": self.Arcs_List[self.Arcs_List.index(x)],
                    "l-attribute": self.L_attribute_list[self.Arcs_List.index(x)],
                    "c-attribute": self.C_attribute_list[self.Arcs_List.index(x)],
                    'eRU': 0
                } for x in value]}

        self.user_input_to_evsa = [final_transform_R(rdlt) for rdlt in rdlts]

        # Printing results of the evaluation
        print("RDLT Evaluation Completed:")
        for rdlt in self.user_input_to_evsa:
            print(rdlt)


    def getRs(self):
        """
        Fetches all RDLT structures except for R1.
        """
        return [R for R in self.user_input_to_evsa if "R1" not in R.keys()]

    def getR(self, R):
        """
        Fetches a specific RDLT (R1, R2, etc.) by its identifier.
        """
        for dictionary in self.user_input_to_evsa:
            if dictionary is not None and R in dictionary:  # Check if dictionary is not None
                return dictionary[R]
        return f"[WARNING] {R} has not been defined or is missing."

if __name__ == '__main__':
    input_data = Input_RDLT('your_file_path_here.txt')  # Make sure to set the correct path to the RDLT file
    input_data.evaluate()
    print(input_data.getRs())  # This will print R2, R3, etc. without R1
    print(input_data.getR('R1'))  # This will print R1 structure
