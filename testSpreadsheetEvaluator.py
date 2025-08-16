import subprocess
import tempfile
import unittest

outputTests = [
    {
        "test": "Basic arithmetic",
        "input": "2 3 +,6 2 /\n8 8 *",
        "expected": "5.0,3.0\n64.0"
    },
    {
        "test": "Basic references",
        "input": "1,2\nA1 B1 +,A2 B1 *",
        "expected": "1.0,2.0\n3.0,6.0"
    },
    {
        "test": "Empty cells",
        "input": ",1.0\n2,",
        "expected": ",1.0\n2.0,"
    },
    {
        "test": "Reference to an empty cell",
        "input": ",\nA1",
        "expected": ",\n"
    },
    {
        "test": "Negative nums and decimals",
        "input": "-3 -2 +,5.5 2 *\n8.78 .1 *",
        "expected": "-5.0,11.0\n0.878"
    },
    {
        "test": "Reference with arithmetic",
        "input": "2,\nA1 3 +",
        "expected": "2.0,\n5.0"
    }
]

errorTests = [
    {
        "test": "Division by zero",
        "input": "1 0 /",
        "error": "Division by zero"
    },
    {
        "test": "Circular reference",
        "input": "A2\nA1",
        "error": "Circular reference at A1"
    },
    {
        "test": "Invalid token",
        "input": "2 3 & +",
        "error": "Invalid token '&' in A1"
    },
    {
        "test": "No operands",
        "input": "-",
        "error": "Need at least 1 operand for - in A1"
    },
    {
        "test": "Too many tokens",
        "input": " ".join(["1"] * 500),
        "error": "Expression too long in A1"
    }
]

class SpreadsheetEvaluatorTest(unittest.TestCase):
    def testOutputCases(self):
        for test in outputTests:
            with self.subTest(test=test["test"]):
                inputFile = tempfile.NamedTemporaryFile(mode="w", delete=False)
                inputFile.write(test["input"])
                inputFile.close()

                outputFile = tempfile.NamedTemporaryFile(mode="r", delete=False)
                outputFile.close()

                subprocess.run(["python3", "SpreadsheetEvaluator.py", inputFile.name, outputFile.name], capture_output=True, text=True)

                with open(outputFile.name, "r") as f:
                    output = f.read().strip()
                self.assertEqual(output, test["expected"].strip())
 
    def testErrorCases(self):
        for test in errorTests:
            with self.subTest(test=test["test"]):
                inputFile = tempfile.NamedTemporaryFile(mode="w", delete=False)
                inputFile.write(test["input"])
                inputFile.close()

                outputFile = tempfile.NamedTemporaryFile(mode="r", delete=False)
                outputFile.close()

                result = subprocess.run(["python3", "SpreadsheetEvaluator.py", inputFile.name, outputFile.name], capture_output=True, text=True)

                errorOutput = result.stdout + result.stderr
                self.assertIn(test["error"], errorOutput)

if __name__ == "__main__": unittest.main()