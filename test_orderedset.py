import unittest
import orderedset

class TestLeftLeaningRedBlackTree(unittest.TestCase):

	def setUp(self):
		self.cls = orderedset.LeftLeaningRedBlackTree
		self.data = tuple(chr(i + 0x20) for i in range(95))

	def test_insert_search(self):
		for i in range(len(self.data)):
			t = self.cls()
			data = list(self.data[:i])
			for j in range(i):
				t.insert(j, self.data[j])
				self.assertEqual(self.data[j], t.search(j))
			for j in range(i):
				self.assertEqual(self.data[j], t.search(j))
			self.assertRaises(KeyError, t.search, i + 1)


	def test_insert_replaces(self):
		t = self.cls()
		t.insert(1, 'a')
		self.assertEqual('a', t.search(1))
		t.insert(1, 'b')
		self.assertEqual('b', t.search(1))

if __name__ == '__main__':
	unittest.main()
