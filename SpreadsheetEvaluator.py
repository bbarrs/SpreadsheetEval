from collections import deque
import re
import sys

'''
Class [SpreadsheetEval] evaluates a single comma-delimited spreadsheet and writes output to a specified output file.
Handles basic arithmetic operations (according to post-order notation), references to other cells, and errors.

Usage is as follows:
    python3 SpreadsheetEvaluator.py <inputfile> <outputfile>

Input file is a plaintext representation of a single spreadsheet with no more than 500,000 cells (empty or non-empty)
Output file is a similar plaintext file with the evaluated results for each cell
'''
class SpreadsheetEval:
    def __init__(self, inputFile, outputFile):
        # Hard cap on max tokens per expression to ensure run-time efficiency that reduces to O(N), where N is number of cells
        self.maxTokensPerCell = 100

        # Cap on number of cells in input file; given in problem statement
        self.maxCells = 500000

        # Plaintext input file given as cmd param
        self.inputFile = inputFile

        # Output file given as cmd param
        self.outputFile = outputFile

        # A 2D list used to map (row, col) to cell name. Used for ease of outputting.
        self.grid = []

        # Maps cell name (key) to raw expression (value)
        self.exprMap = {}

        # Maps cell name (key) to its evaluated result (value)
        self.valMap = {}

    '''
    Parses the input file, assuming the aforementioned pre-conditions are met (see SpreadsheetEval header comment)
    
    Populates expression map and map of spreadsheet grid
    '''
    def parseInput(self):
        cellCount = 0
        with open(self.inputFile, 'r') as rows:
            for rowIndex, row in enumerate(rows):
                cells = row.strip().split(',')
                cellCount += len(cells)
                rowCells = []
                
                # Ensure spreadsheet has at most [maxCells] cells
                if cellCount > self.maxCells:
                    raise Exception(f"Input file contains more than maximum number of allowed cells ({self.maxCells})")

                for colIndex, expression in enumerate(cells):
                    cell = self.getCellName(colIndex, rowIndex)
                    rowCells.append(cell)

                    expression = expression.strip()
                    if not expression: # For empty cells
                        self.valMap[cell] = ""
                        continue

                    self.exprMap[cell] = expression.split()
                
                self.grid.append(rowCells)
    '''
    Converts 0-based index to column name according to spreadsheet conventions.
    
    Assumes [A, B, C, ..., Y, Z, AA, AB, ..., AZ, BA, BB, ...]
    '''
    def indexToColForm(self, index):
        columnName = ""

        while (index >= 0):
            columnName = chr(ord('A') + (index % 26)) + columnName
            index = (index // 26) - 1

        return columnName

    '''
    Converts (row, col) to respective cell mapping according to spreadsheet conventions.
    
    Anchored at (0, 0)
    '''
    def getCellName(self, colIndex, rowIndex):
        col = self.indexToColForm(colIndex)
        return f"{col}{rowIndex+1}"

    '''
    Evaluates all expressions in each cell of the spreadsheet

    Iterates through cell-by-cell, using DFS to handle cell references

    Values of all cells are stored as floats
    '''        
    def evaluate(self):
        for row in self.grid:
            for cell in row:
                if cell in self.exprMap:
                    self.evaluateDFS(cell, set())

    '''
    Core evaluation function; recursively evaluates a cell's expression using DFS

    Takes in the cell to be evaluated (as identified by cell name), populates value map,
        and returns evaluated result of cell

    Follows specific version of post-order syntax, where the presence of an operator immediately
        signifies that all previously seen operands should be consumed using that operation

    As an example, 2 3 + 4 * is the correct syntax for the expression (2+3) * 4

    Detects any circular references and other common errors
    '''
    def evaluateDFS(self, cell, visiting):
        queue = deque()
        
        if cell in self.valMap:
            return self.valMap[cell]
        
        if cell in visiting:
            raise Exception(f"Circular reference at {cell}")
        
        if cell not in self.exprMap: # Allows for us to effectively skip evaluation of blank cells
            return ""

        visiting.add(cell)

        ops = self.exprMap[cell]
        
        for op in ops:
            if len(ops) > self.maxTokensPerCell:
                raise Exception(f"Expression too long in {cell} - max of {self.maxTokensPerCell} tokens in a cell")

            if op in {"+", "-", "*", "/"}:
                if len(queue) < 2:
                    raise Exception(f"Need at least 1 operand for {op} in {cell}")
                a = queue.popleft, 
                b = queue.popleft
                res = self.calculate(a, b, op)
                queue.append(res)
            elif self.isCellReference(op):
                val = self.evaluateDFS(op, visiting)
                queue.append(val)
            elif re.match(r"^[+-]?\d*(\.\d+)?$", op):
                try:
                    queue.append(float(op))
                except Exception:
                    raise Exception(f"Error evaluating number {op} in {cell}")
            else:
                raise Exception(f"Invalid token '{op}' in {cell}")

        if len(queue) != 1:
            raise Exception(f"Invalid expression in {cell}")

        res = queue.pop()
        self.valMap[cell] = res
        visiting.remove(cell)
        return res

    '''
    Performs calculation on operands in the queue using the given operator
    '''
    def calculate(self, a, b, operator): # FIXME: change back to queue type
        if operator == "+":
            res = a + b
        elif operator == "-":
            res = a - b
        elif operator == "*":
            res = a * b
        elif operator == "/":
            if b == 0:
                raise Exception("Division by zero")
            res = a / b
        return res

    '''
    Determines if a token is a reference to another cell, following pattern of at least one
        uppercase letter followed by some positive integer
    '''
    def isCellReference(self, op):
        if not op:
            return False
        
        colCount = 0
        for char in op:
            if char.isalpha() and char.isupper():
                colCount += 1
            else:
                break
        
        if not colCount: return False

        row = op[colCount:]
        return row and row.isdigit() and int(row) > 0

    '''
    Writes evaluated cell results to output file (creating or overwriting said file)
    '''
    def writeOutput(self):
            with open(self.outputFile, 'w') as out:
                for row in self.grid:
                    cells = []
                    for cell in row:
                        cells.append(str(self.valMap[cell]))
                    out.write(",".join(cells) + "\n")
    
def main():
    
    # Checks args to ensure usage is correct
    if len(sys.argv) != 3:
        print("Invalid usage.\npython3 SpreadsheetEvaluator.py <inputfile> <outputfile>")
        return
    
    spreadsheetEvaluator = SpreadsheetEval(sys.argv[1], sys.argv[2])

    try:
        print("Parsing input...\n")
        spreadsheetEvaluator.parseInput()

        print("Evaluating cell expressions...\n")
        spreadsheetEvaluator.evaluate()

        print(f"Writing to {sys.argv[2]}...\n")
        spreadsheetEvaluator.writeOutput()

        print("Spreadsheet successfully evaluated and tabulated.\n")
    except Exception as e:
        print("Error: ", e)


if __name__ == "__main__": main()