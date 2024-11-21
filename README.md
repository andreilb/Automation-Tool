# Automation-Tool
This automation tool (python application) is an Automated Verification for Classical Soundness of RDLTs.

## Author
- Andrei Luz B. Asoy
- Email: abasoy@up.edu.pg
- Student Number: 2019-08852
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
