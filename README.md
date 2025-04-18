# RDLT Processor

This repository contains a Python implementation for processing RDLT input files and verfying L-safeness and dertermine Classical Soundness of an RDLT.

## Overview

The RDLT Processor parses text formatted input files representing an RDLT (with RBS) with attributes, and processes them through expanded vertex simplification and convert to matrix form for further analysis. This system supports cycle detection, abstract arc generation, L-safeness analysis, and activity profile generation.

Key Components:

- **Input_RDLT**: Reads and processes RDLT files into structured components (R1, R2, etc.)
- **Cycle**: Detects and analyzes cycles in RDLTs
- **AbstractArc**: Creates abstract arcs from existing RBS structures
- **TestJoins**: Analyzes JOIN patterns in RDLT
- **ModifiedActivityExtraction**: Extracts activity profiles from the RDLT
- **Matrix**: Provides matrix operations for L-safeness of RDLT analysis
- **Utils**: Offers helper functions for graph operations and data manipulation

## Architecture

The RDLT automation tool follows a modular architecture that processes graph data through several stages:

1. **Input Processing**: Parses RDLT files and extracts components (arcs, vertices, attributes)
2. **Structure Analysis**: 
   - R1 Processing: Handles arcs not associated with center vertices
   - R2 Processing: Processes arcs associated with center vertices (Reset-Bound Subsystem)
3. **Cycle Detection**: Identifies cycles and calculates expanded reusability (eRU) values
4. **Abstract Arc Generation**: Creates higher-level abstract arcs from R1 and R2 components
5. **Join Analysis**: Identifies and analyzes JOIN patterns in the RDLT
6. **Activity Profile Extraction**: Generates activity profiles for further analysis

## RDLT File Format

RDLT files follow a specific structure with these sections:

### R Section
Contains the arcs (edges) of the RDLT with their attributes:
```
vertex1, vertex2, c-attribute, l-attribute
```

Where:
- `vertex1` and `vertex2` define the arc (directed edge)
- `c-attribute` represents the "complexity attribute" of the arc
- `l-attribute` represents the "length attribute" of the arc

### CENTER Section
Lists center vertices that serve as focal points for identifying R2, R3, etc. structures:
```
CENTER
center1, center2, center3
```

### IN Section
Lists incoming arcs to the overall structure:
```
IN
vertex1, vertex2
vertex3, vertex4
```

### OUT Section
Lists outgoing arcs from the overall structure:
```
OUT
vertex5, vertex6
vertex7, vertex8
```

## Core Modules

### Input_RDLT Module
The primary module that reads RDLT files and processes them into structured components:
```python
from input_rdlt import Input_RDLT

# Initialize with an input file
rdlt_processor = Input_RDLT('path/to/rdlt_file.txt')

# Process the input data
rdlt_processor.evaluate()

# Retrieve RDLT structures
r1_components = rdlt_processor.getR('R1')  # Get R1 components
r_components = rdlt_processor.getRs()      # Get all components except R1
```

### Cycle Module
Detects cycles in the RDLT and computes eRU values:
```python
from cycle import Cycle

# Initialize with RDLT components
cycle_detector = Cycle(r1_components)

# Find cycles in the RDLT
cycles = cycle_detector.evaluate_cycle()

# Get cycle list
cycle_list = cycle_detector.get_cycle_list()
```

### AbstractArc Module
Creates abstract arcs from existing RBS structures:
```python
from abstract import AbstractArc

# Initialize with R1, R2, and bridge components
abstract_generator = AbstractArc(R1, R2, In_list, Out_list, Centers_list, Arcs_List)

# Generate abstract vertices
abstract_vertices = abstract_generator.find_abstract_vertices()

# Create abstract arcs through multiple steps
abstract_arcs = abstract_generator.make_abstract_arcs_stepA(abstract_vertices)
abstract_arcs = abstract_generator.make_abstract_arcs_stepB(abstract_arcs)
abstract_arcs = abstract_generator.make_abstract_arcs_stepC(abstract_arcs)
```

### TestJoins Module
Analyzes JOIN patterns in RDLT:
```python
from joins import TestJoins

# Group arcs by target vertex
join_groups = TestJoins.group_arcs_by_target_vertex(R2)

# Check for similar target vertices and update data
updated_data = TestJoins.checkSimilarTargetVertexAndUpdate(R1, R2)
```

## RDLT Data Structures

After processing, the RDLT data is organized into hierarchical structures:

- **R1**: Contains arcs not associated with any center vertex
- **R2, R3, etc.**: Contain arcs associated with each center listed in the CENTER section
- **Abstract Arcs**: Higher-level arcs derived from R1 and R2 components

Each RDLT structure is represented as a list of dictionaries, where each dictionary contains:
- `r-id`: A unique identifier for the arc
- `arc`: The arc in the format "vertex1, vertex2"
- `l-attribute`: The length attribute of the arc
- `c-attribute`: The complexity attribute of the arc
- `eRU`: The expanded reusability unit value (computed for cycles)

## Cycle Analysis

The system detects cycles in RDLT and computes eRU values for arcs involved in cycles. The eRU value represents a measure of reusability based on:

1. Identifying all cycles in the RDLT
2. For each cycle, finding the critical arc (with the minimum l-attribute)
3. Assigning the critical arc's l-attribute value as the eRU for all arcs in the cycle

## JOIN Analysis

The JOIN analysis identifies and processes arcs that share the same target vertex, which represent JOIN patterns in the RDLT. The system distinguishes between:

- **OR-JOINs**: All arcs in a group have the same c-attribute
- **Mixed JOINs**: Arcs in a group have different c-attributes

## Abstract Arc Generation

Abstract arcs are created through a three-step process:

1. **Step A**: Create initial abstract arcs from cycles and paths between abstract vertices
2. **Step B**: Add self-loops for abstract vertices with cyclic paths
3. **Step C**: Finalize abstract arcs by assigning attributes based on calculated eRU values

## Dependencies

- Python 3.6+
- pathlib
- collections
- functools

## Example Input File

```
x1, x2, 0, 5
x2, x3, a, 4
x3, x6, 0, 3
x4, x3, 0, 2
x4, x5, b, 7
x5, x6, a, 2
CENTER
x3
IN
x4, x3
OUT
x5, x6
```

This input file defines an RDLT with six vertices and six  arcs, with x3 as a center. 