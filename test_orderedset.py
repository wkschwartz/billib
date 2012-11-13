import unittest
import orderedset

class TestLeftLeaningRedBlackTree(unittest.TestCase):

	def setUp(self):
		self.cls = orderedset.LeftLeaningRedBlackTree
		self.data = tuple(chr(i + 0x20) for i in range(95))

	def test_int_keys_in_order(self):
		for i in range(len(self.data)):
			t = self.cls()
			data = list(self.data[:i])
			for j in range(i):
				self.assertEqual(j, len(t))
				self.assertNotIn(j, t)
				self.assertEqual(list(range(j)), list(t))
				t.insert(j, data[j])
				self.assertEqual(data[j], t.search(j))
				self.assertIn(j, t)
			self.assertEqual(i, len(t))
			self.assertEqual(list(range(len(data))), list(t))
			self.assertRaises(KeyError, t.search, i + 1)

	def test_insert_replaces(self):
		t = self.cls()
		t.insert(1, 'a')
		self.assertEqual('a', t.search(1))
		t.insert(1, 'b')
		self.assertEqual('b', t.search(1))

	def test_only_ordered_keys(self):
		t = self.cls()
		for k in None, object(), type, {}:
			self.assertRaises(TypeError, t.search, k, 'a')
			self.assertRaises(TypeError, t.insert, k, 'a')

if __name__ == '__main__':
	unittest.main()
