import unittest
from performance.app.performance import ServiceStats
 
class TddInPythonExample(unittest.TestCase):
 
    def test_calculator_add_method_returns_correct_result(self):
        calc = ServiceStats()
        result = calc.add(2,2)
        self.assertEqual(4, result)
 
 
if __name__ == '__main__':
    unittest.main()