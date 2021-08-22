from create_unit_test import *

class Testing(TestExcel):
	 def test_formula(self):
	 	formula = '=SUM(A1,B1)'
	 	func = create_unit_test_from_formula(formula)
	 	result = func(2, 2)
	 	self.assertEqual(result, 4)

	 def test_data(self):
	 	formula = '=SUM(A1,B1)'
	 	path = self.files['uscities.xlsx']
	 	result = create_unittest_from_file(formula, path)
	 	self.assertEqual(result, 4)

