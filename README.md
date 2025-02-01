# Automation-Tool
This automation tool (python application) is an Automated Verification for Classical Soundness of RDLTs.

## Author
- Andrei Luz B. Asoy
- Email: abasoy@up.edu.ph
- BS in Computer Science

## File Contents
- main.py : The main program of the automation tool. This utilizes all the other python files below.
- input_rdlt.py : Contains the input process on generating RDLTs from input text file to input RDLT and generation of EVSA from input RDLT. 
- create_r1: Part of EVSA Extraction. Contains the algorithm on creating the R1 (components outside the RBS).
- create_r2: Part of EVSA Extraction. Contains the algorithm on creating the R2 (components inside the RBS).
- cycle.py : Part of EVSA Extraction. Contains the algorithm on detecting cycles. Also contains algorithm to update R2 (RBS).
- abstract_arc.py : Part of EVSA Extraction. Contains the algorithm on creating abstract arcs for R1.
- utils.py : Contains utility functions designed for manipulating graph structures, detecting cycles, and formatting path outputs.
- matrix.py : Contains the algorithm on converting input RDLT (in EVSA form) to Matrix Representation. Also contains algorithm to determine L-safeness.

### Misc File Contents
- __init__.py
- __pycache__/
- sample_rdlt.txt

***
## Documentation
The following are documentations for each python file specified above in the file contents. These explains the processes involved within the code.

## Main.py `main.py`
This processes input RDLT (Robustness Diagram with Loop and Time Controls) data, detects cycles in the graph, and processes the resulting data using multiple functions from different modules (`Input_RDLT`, `Cycle`, `ProcessR2`, `ProcessR1`). It serves as the entry point for the overall RDLT processing, ensuring that data is read, categorized, and analyzed. 

This also integrates various components of the RDLT analysis system, checks for the existence of certain attributes (such as RBS centers and bridges), and processes both R1 and R2 data.

### Main Workflow:
1. **Input File Processing**
   - The script begins by initializing an `Input_RDLT` instance with a path to the input file (hardcoded or provided).
   - The `evaluate()` method of `Input_RDLT` is invoked to read and categorize the file contents, which includes separating the data into `R1`, `R2`, centers, in-bridges, and out-bridges.

2. **R2 Processing (Reset-Bound Subsystem)**
   - The script checks if `R2` and the necessary RBS components (`Centers_list`, `In_list`, and `Out_list`) exist.
   - If valid, it uses `ProcessR2` to process and print details of the `R2` data, focusing on the flow and structure of arcs.
   - It then uses the `Cycle` class to detect and evaluate cycles in the `R2` graph, printing out the cycle details if found.

3. **R1 Processing (Main Structure)**
   - If cycles are detected in `R2`, the script retrieves `R1` data from the `Input_RDLT` instance.
   - It checks and prints the retrieved `R1` data, then passes relevant lists (arcs, L-attributes, C-attributes, centers, in-bridges, and out-bridges) to the `ProcessR1` function.
   - `ProcessR1` handles abstract arcs and updates the `R1` data accordingly.

  4. **Cyclce Detection and Evaluation**
     - The `Cycle` class is used to evaluate cycles in both R1 and R2. If cycles are found, they are printed with details about their structure.
  5. **JOIN Evaluation**
     - The `TestJoins` class evaluates whether the components of the RBS form an **OR-JOIN**.
     - If the RBS contains ONLY OR-JOINs, only R1 is processed further; otherwise, if there are any presence of any types of JOIN, both R1 and R2 are processed in parallel.
  6. **L-Safeness Verification**
     - Using the matrix class, the script performs matrix operations on R1 and R2 (if necessary) to verify the **L-Safeness** of the RDLT.
     - The **L-Safeness** of the structure is evaluated based on the matrix values. If the system is **L-safe**, the script confirms that the RDLT is **Classical Sound**. Otherwise, it flags the need for further verification.
  7. **Activity Profile Generation**
      - In case of violations detected during matrix evaluation, the script generates an **activity profile** through modified activity extraction that identifies which components violate the L-safeness criteria.

## `Input_RDLT` 'input_rdlt.py'

#### **Overview:**
The `Input_RDLT` class is designed to process and evaluate Robustness Diagram with Loop and Time Controls (RDLT) data from a specified input file. It extracts various components of the RDLT, such as arcs, vertices, and the RBS (Reset-Bound Subsystem) components (center, in-bridge, and out-bridge). Additionally, it supports the evaluation of these components, building and accessing RDLT structures like R1, R2, etc., for further analysis.

#### **Constructor (`__init__`):**
- **Parameters:**
  - `filepath`: The path to the RDLT file (default: `'rdlt_text/sample_rdlt.txt'`). The file should contain RDLT data structured in a specific format (e.g., Arcs, Vertices, Centers, In-bridges, Out-bridges).
  - Input RDLT Text Format
    ```
    <vertex1>, <vertex2>, <c-attribute>, <l-attribute>
    CENTER 
    <vertex>
    IN 
    <vextex1> , <vertex2>
    OUT 
    <vertex1>, <vertex2>
    ```

  - Sample RDLT in the specified format
    ```
    x1, x2, a, 1
    x2, x3, 0, 2
    x3, x2, 0, 3
    x2, x4, 0, 4
    x3, x4, 0, 1
    x4, x5, 0, 6
    x4, x6, b, 7
    x5, x6, a, 7
    x6, x2, a, 5
    x6, x7, 0, 1
    CENTER 
    x2
    IN 
    x1, x2
    x6, x2
    OUT 
    x4, x5
    x4, x6
    ```
- **Attributes Initialized:**
  - `filepath`: Stores the file path as a `Path` object.
  - `contents`: A dictionary with keys `'R'`, `'CENTER'`, `'IN'`, and `'OUT'` to store the respective components of the RDLT data.
  - `Cycle_List`: Initializes an empty list to store cycle data.
  - `Centers_list`, `In_list`, `Out_list`: Lists to hold centers, in-bridges, and out-bridges extracted from the RDLT.
  - `Arcs_List`, `Vertices_List`, `C_attribute_list`, `L_attribute_list`: Empty lists to store arcs, vertices, and their respective attributes.
  - `user_input_to_evsa`: List to store the final transformed RDLT structures.

- **Process:**
  - Reads the input file line by line, categorizing lines into respective sections (`R`, `CENTER`, `IN`, `OUT`).
  - Processes the centers, in-bridges, and out-bridges to create respective lists.

#### **Method: `evaluate`**
- **Functionality:**
  - **Extracts data** from the `'R'` section by parsing each line and separating the arc, c-attribute, and l-attribute values.
  - **Extracts unique vertices** from the arcs.
  - **Creates and categorizes arcs**, vertices, and attributes into respective lists.
  - **Evaluates the RDLT structure** by processing the Reset-Bound Subsystem (RBS) components:
    - Centers (`CENTER`), In-bridges (`IN`), Out-bridges (`OUT`) are processed.
  - **Builds RDLT structures** (R1, R2, etc.) using the extracted data. The function identifies arcs involved in each RDLT and stores the information accordingly.

- **Key Functions within `evaluate`:**
  - `extract_R`: Processes and extracts information from the `'R'` section.
  - `extract_vertices`: Collects unique vertices from the arcs.
  - `extract_rdlt`: Processes each RDLT structure (R1, R2, etc.) by filtering arcs and vertices.
  - `final_transform_R`: Finalizes the transformation of each RDLT structure by adding an `r-id` for each arc and calculating relevant attributes (e.g., `l-attribute`, `c-attribute`, `eRU`).

- **Printed Results:**
  - Displays the processed RDLT data: Arcs List, Vertices List, C-attribute List, L-attribute List, Centers, In, Out, and the results of the evaluation.

#### **Method: `getRs`**
- **Functionality:**
  - Returns a list of RDLT structures, excluding `R1`.

---

#### **Method: `getR`**
- **Functionality:**
  - Fetches a specific RDLT (e.g., `R1`, `R2`, etc.) by its identifier and returns the corresponding structure.
  - If the requested RDLT is not found, returns a warning message indicating that the structure is missing.

---

#### **Example Usage:**
```python
if __name__ == '__main__':
    input_data = Input_RDLT('your_file_path_here.txt')  # Make sure to set the correct path to the RDLT file
    input_data.evaluate()
    print(input_data.getRs())  # This will print R2, R3, etc. without R1
    print(input_data.getR('R1'))  # This will print R1 structure
```

- **Flow of Execution:**
  - An instance of the `Input_RDLT` class is created by passing the path to the RDLT file.
  - The `evaluate` method is called to process and evaluate the data in the file.
  - The results of the evaluation, including RDLT structures (R1, R2, etc.), are printed.
  - The `getRs` method can be used to retrieve R2, R3, etc., while `getR` fetches a specific RDLT structure (e.g., `R1`).

---

#### **Output Example:**

```
------------------------------------------------------------
Input RDLT: 
--------------------
Arcs List (5):  ['x1, x2', 'x2, x3', 'x3, x4', 'x4, x5', 'x5, x6']
Vertices List (6):  ['x1', 'x2', 'x3', 'x4', 'x5', 'x6']
C-attribute List (5):  ['a', 'b', 'a', 'b', 'c']
L-attribute List (5):  ['1', '2', '3', '4', '5']
--------------------
RBS components:
--------------------
Centers (2):  ['x2', 'x4']
In:  ['x1', 'x5']
Out:  ['x6', 'x3']
------------------------------------------------------------
RDLT Evaluation Completed:
{'R2-x2': [{'r-id': 'R2-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0}]}
{'R3-x4': [{'r-id': 'R3-3', 'arc': 'x4, x5', 'l-attribute': '4', 'c-attribute': 'b', 'eRU': 0}]}
```

- **Explanation of Output:**
  - The printed output includes the details of the RDLT evaluation, with the arcs, vertices, attributes, and centers.
  - The final RDLT evaluation output provides the structures of `R2`, `R3`, and any other RDLT components based on the input data.

## `Process R1` 'create_r1.py'

### Overview
The `ProcessR1` function processes the components of R1, extracting arcs, vertices, and attributes, while calculating the **Expanded Reusability (eRU)** and generating abstract arcs based on the R2 system. It automatically prints the results for each step and returns the updated R1 data.

### Import Dependencies
```python
from abstract import AbstractArc  # Ensure the AbstractArc class is imported 
from cycle import Cycle  # Ensure the Cycle class is imported
```

### Function Definition
```python
def ProcessR1(arcs_list, l_attribute_list, c_attribute_list, R1, Centers_list, In_list, Out_list, R2):
```

#### Parameters:
- `arcs_list` (list of strings): List of arcs in the RDLT system, where each arc is represented as a string of vertices (e.g., `'x1, x2'`).
- `l_attribute_list` (list of strings): Corresponding list of **l-attributes** for each arc in `arcs_list`.
- `c_attribute_list` (list of strings): Corresponding list of **c-attributes** for each arc in `arcs_list`.
- `R1` (list of dictionaries): List of existing arcs in R1, where each arc is represented as a dictionary containing attributes such as `'r-id'`, `'arc'`, `'l-attribute'`, `'c-attribute'`, and `'eRU'`.
- `Centers_list` (list of strings): List of center vertices in the RBS, used for abstract arc generation.
- `In_list` (list of strings): List of in-bridges in the RBS.
- `Out_list` (list of strings): List of out-bridges in the RBS.
- `R2` (list of dictionaries): List of arcs in R2, where each arc is represented as a dictionary containing similar attributes as R1 (`'r-id'`, `'arc'`, `'l-attribute'`, `'c-attribute'`, and `'eRU'`).

#### Returns:
- `R1` (list of dictionaries): Updated list of R1, now including both original and newly added abstract arcs. Each arc in R1 is a dictionary with updated attributes.

### Function Process Breakdown:

1. **Extract R1 Components**: 
    - Extracts the arcs, vertices, and corresponding attributes (`c-attribute` and `l-attribute`) from the input list `R1`.
    - Vertices are extracted by splitting the arcs and ensuring they are unique.

2. **Initialize AbstractArc Class**:
    - An instance of the `AbstractArc` class is created with the provided data: `R1`, `R2`, `In_list`, `Out_list`, `Centers_list`, and `arcs_list`.

3. **Find Abstract Vertices**:
    - The `find_abstract_vertices()` method is called on the `AbstractArc` instance to find vertices that will participate in abstract arc creation. The result is printed.

4. **Create Abstract Arcs (Step A)**:
    - The `make_abstract_arcs_stepA()` method generates abstract arcs based on the identified abstract vertices.
    - If this step encounters an error, it is caught and an error message is printed.

5. **Add Self-Loops (Step B)**:
    - The `make_abstract_arcs_stepB()` method is called to add self-loops to the abstract arcs.
    - If an error occurs, it is caught and an error message is printed.

6. **Finalize Abstract Arcs (Step C)**:
    - The `make_abstract_arcs_stepC()` method is invoked to finalize the abstract arcs.
    - Errors are caught and printed as well.

7. **Add an `r-id` for the Abstract Arcs**:
    - The function calculates the next available `r-id` by finding the highest `r-id` already existing in `R1` and adding 1.

8. **Create and Add Abstract Arcs to R1**:
    - For each finalized abstract arc, a new dictionary is created, assigning a unique `r-id`, along with its corresponding `arc`, `l-attribute`, `c-attribute`, and `eRU`.
    - These new abstract arcs are appended to the `R1` list.

9. **Return Updated R1**:
    - The function returns the updated `R1` list, which now includes both the original arcs and the newly added abstract arcs.
  
### Detailed Output Example:
The output printed by the function includes the following details:
```
R1:
--------------------
Arcs List (8): ['x1, x2', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7', 'x2, x2', 'x2, x4']
Vertices List (7): ['x1', 'x2', 'x4', 'x5', 'x6', 'x7']
C-attribute List (8): ['a', '0', 'b', 'a', 'a', '0', 'a', 'a']
L-attribute List (8): ['1', '6', '7', '7', '5', '1', '18', '6']
eRU List (8): [0, 2, 3, 5, 1, 0, 3, 0]
------------------------------------------------------------
Abstract Arcs (2): 
{'r-id': 'R1-10', 'arc': 'x2, x2', 'l-attribute': '18', 'c-attribute': 'a', 'eRU': 3}
{'r-id': 'R1-11', 'arc': 'x2, x4', 'l-attribute': '6', 'c-attribute': 'a', 'eRU': 0}
------------------------------------------------------------
Updated R1 after adding abstract arcs: 
[{'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
 {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0},
 {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
 {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0},
 {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0},
 {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0},
 {'r-id': 'R1-10', 'arc': 'x2, x2', 'l-attribute': '18', 'c-attribute': 'a', 'eRU': 3}
 {'r-id': 'R1-11', 'arc': 'x2, x4', 'l-attribute': '6', 'c-attribute': 'a', 'eRU': 0}]
```

### Error Handling
- Errors during any of the abstract arc generation steps (Step A, Step B, or Step C) will be caught, and an appropriate error message will be printed (written as comments for debugging purposes).

## `ProcessR2` 'create_r2.py'

### Overview
The `ProcessR2` function processes the components of R2 (components of every RBS), extracting arcs, vertices, and attributes, and calculating the **Expanded Reusability (eRU)** for each arc. It identifies cycles in R2 and computes the eRU based on the minimum l-attribute of arcs in each cycle. The function automatically prints the results of the process for verification.

### Import Dependencies
```python
from cycle import Cycle  # Ensure the Cycle class is imported
```

### Function Definition
```python
def ProcessR2(R2):
```

#### Parameters:
- `R2` (list of dictionaries): List of arcs in R2, where each arc is represented as a dictionary containing the following keys:
  - `'arc'`: A string representing the arc (e.g., `'x2, x3'`).
  - `'c-attribute'`: The **c-attribute** for the arc (e.g., `'a'` or `'0'`).
  - `'l-attribute'`: The **l-attribute** for the arc (e.g., `'1'` or `'2'`).

#### Returns:
- **None**: The function prints the results directly to the console.

### Function Process Breakdown:

1. **Extract R2 Components**:
    - Extracts the list of arcs, vertices, and the corresponding **c-attribute** and **l-attribute** from the input list `R2`.
    - Vertices are extracted by splitting the arcs and ensuring they are unique, i.e., no duplicates.

2. **Initialize the Cycle Object**:
    - A `Cycle` object is created using the `R2` data, which is responsible for detecting cycles within the R2 graph.

3. **Evaluate Cycles in R2**:
    - The `evaluate_cycle()` method is called on the `Cycle` object to identify any cycles present in the system. This method returns a list of cycles if any are detected, or an empty list if no cycles are found.

4. **Calculate eRU for Arcs**:
    - The `calculate_eRU_for_arcs()` method is called on the `Cycle` object to calculate the **Effective Reusability (eRU)** for each arc in `R2`. This is based on the **l-attributes** of the arcs.

5. **Initialize eRU List**:
    - The function initializes a list `eRU_list_R2` with the same length as the number of arcs in R2. By default, each value in `eRU_list_R2` is set to `0`.

6. **Process Cycles**:
    - If cycles are detected, the function checks whether each arc in `R2` is part of a cycle. If an arc is part of a cycle, its eRU value is updated to the minimum **l-attribute** of all arcs in that cycle.
    - If an arc is not part of a cycle, its eRU remains `0` (as initialized).

7. **Print the Results**:
    - The function prints detailed information about the R2 components, including:
      - Arcs list: All arcs in R2.
      - Vertices list: All unique vertices in R2.
      - C-attributes list: The **c-attributes** for each arc.
      - L-attributes list: The **l-attributes** for each arc.
      - eRU list: The calculated **eRU** values for each arc.

### Detailed Output Example:
The output printed by the function includes the following details:

```
R2:
--------------------
Arcs List (4): ['x2, x3', 'x3, x2', 'x2, x4', 'x3, x4']
Vertices List (4): ['x2', 'x3', 'x4']
C-attribute List (4): ['0', '0', '0', '0']
L-attribute List (4): ['2', '3', '4', '1']
eRU List (4): [0, 0, 0, 0]
------------------------------------------------------------
```

If cycles are detected, the **eRU List** will reflect the calculated **eRU** values for arcs that are part of the cycle.

### Error Handling
- If no cycles are detected in R2, the function will print `"No cycles detected in R2."` to indicate that no further cycle-based calculations are performed.
- The `calculate_eRU_for_arcs` method assumes that each arc has a corresponding **l-attribute**; if any arc is missing this attribute, an error may be raised in the cycle detection and eRU calculation processes.

## `Cycle` 'cycle.py'

The `Cycle` class is used to detect cycles in a directed graph represented by a list of arcs (edges). It supports processing arcs and vertices, detecting cycles through depth-first search (DFS), evaluating the presence of cycles, and calculating Expanded Reusability (eRU) for the arcs involved in cycles. The class is initialized with a list of arcs, which are processed to create a graph structure. It then provides methods for cycle detection and cycle-related calculations.

### Key Features:
1. **Cycle Detection:**  
   The class detects cycles in a graph using DFS and stores them in a list of cycles.

2. **Graph Representation:**  
   Converts the list of arcs into an adjacency list representation for efficient cycle detection.

3. **eRU Calculation:**  
   Computes the Effective Reset Units (eRU) for each arc based on cycle participation.

4. **Cycle Evaluation:**  
   Evaluates the presence of cycles in the graph and outputs relevant cycle details.

### Methods:
- **`__init__(self, R)`**  
  Initializes the `Cycle` object by processing the provided list of arcs.

- **`process_arcs(self)`**  
  Processes the arcs from the list and extracts the vertices and edges.

- **`list_to_graph(self, edge_list)`**  
  Converts an edge list into an adjacency list representation of the graph.

- **`find_cycles(self, adj_list)`**  
  Detects cycles in the graph using DFS.

- **`store_to_cycle_list(self)`**  
  Stores the detected cycles in the `Cycle_List` attribute.

- **`evaluate_cycle(self)`**  
  Evaluates and formats the detected cycles for output.

- **`calculate_eRU_for_arcs(self, L_Attributes)`**  
  Calculates eRU for each arc in the graph based on its participation in cycles.


