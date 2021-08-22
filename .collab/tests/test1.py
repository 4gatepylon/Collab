from create_unit_test import *

class Testing(TestExcel):
	#  def test_formula(self):
	#  	formula = '=MAx(A1,B1)'
	#  	func = create_unit_test_from_formula(formula)
	#  	result = func(2, 2)
	#  	self.assertEqual(result, 4)

	#  def test_data(self):
	# 	 filename = self.files['sampledatainsurance.xlsx']
	# 	 formula = '=MIN(F2:F501)'
	# 	 result = create_unittest_from_file(formula, filename)
	# 	 self.assertGreater(result, 10000)

	 def test_data_min_value(self):
		 filename = self.files['sampledatainsurance.xlsx']
		 result = min(retrieve_col(filename, 'F2', 'F501')).value
		 self.assertGreater(result, 10000)



	 def test_data_valid_cols(self):
		 filename = self.files['sampledatainsurance.xlsx']
		 possibleValues = set(['Y', 'N'])
		 result = [value in possibleValues for value, _ in retrieve_col(filename, 'I2', 'I501')]
		 self.assertTrue(result)
