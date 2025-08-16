## SpreadsheetEvaluator
Class `SpreadsheetEval` evaluates a single comma-delimited spreadsheet and writes output to a specified output file.
Handles basic arithmetic operations (according to post-order notation), references to other cells, and errors.

Usage is as follows:

    python3 SpreadsheetEvaluator.py <inputfile> <outputfile>


Input file is a plaintext representation of a single spreadsheet with no more than 500,000 cells (empty or non-empty)

Output file is a similar plaintext file with the evaluated results for each cell
