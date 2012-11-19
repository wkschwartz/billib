import unittest
import orderedtable
import random
import sys
import math


RECURSION_LIMIT = sys.getrecursionlimit()


class TestBinarySearchTree(unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.BinarySearchTree
		self.data = tuple(chr(i + 0x20) for i in range(95))

	def test_int_keys_in_order(self):
		for i in range(len(self.data)):
			self._int_keys(self.data[:i])

	def test_int_keys_rand_order(self):
		for i in range(len(self.data)):
			data = list(self.data[:i])
			random.shuffle(data)
			self._int_keys(data)

	def test_height_after_random_insert(self):
		data = list(range(2 * RECURSION_LIMIT))
		size = len(data)
		random.shuffle(data)
		t = self.cls()
		for i in data:
			t._insert(i, i)
		self.assertLessEqual(t._root.height(), 2.0 * math.log(size, 2))

	def test_height_after_ordered_insert(self):
		data = list(range(2 * RECURSION_LIMIT))
		size = len(data)
		t = self.cls()
		for i in data:
			t._insert(i, i)
		self.assertLessEqual(t._root.height(), 2.0 * math.log(size, 2))

	def _int_keys(self, data):
		t = self.cls()
		self.assertEqual(t._root.height(), 0)
		i = len(data)
		for j in range(i):
			self.assertEqual(j, len(t))
			self.assertNotIn(j, t)
			self.assertEqual(list(range(j)), list(t))
			t._insert(j, data[j])
			if j > 1:
				self.assertLess(t._root.height(), 2.0 * math.log(j + 1, 2))
			else:
				self.assertEqual(t._root.height(), j + 1)
			self.assertEqual(data[j], t._search(j))
			self.assertIn(j, t)
		self.assertEqual(i, len(t))
		self.assertEqual(list(range(len(data))), list(t))
		self.assertRaises(KeyError, t._search, i + 1)

	def test_insert_replaces(self):
		t = self.cls()
		t._insert(1, 'a')
		self.assertEqual('a', t._search(1))
		t._insert(1, 'b')
		self.assertEqual('b', t._search(1))

	def test_only_ordered_keys(self):
		t = self.cls()
		for k in None, object(), type, {}:
			self.assertRaises(TypeError, t._search, k, 'a')
			self.assertRaises(TypeError, t._insert, k, 'a')

	def test_disjoint_keys(self):
		t = self.cls()
		t._insert({1}, 'a')
		self.assertRaises(KeyError, t._search, set())
		self.assertRaises(TypeError, t._search, {2})
		self.assertRaises(TypeError, t._insert, {2})

	def test_unhashable_keys(self):
		t = self.cls()
		for k in [], [1], [2]:
			t._insert(k, 'a')
			self.assertEqual(t._search(k), 'a')

	def test_min_max(self):
		t = self.cls()
		self.assertRaises(ValueError, t.min)
		self.assertRaises(ValueError, t.max)
		data = list(self.data)
		random.shuffle(data)
		for item in data:
			t._insert(item, ord(item))
		self.assertEqual(min(data), t.min())
		self.assertEqual(max(data), t.max())

	def test_floor_ceiling(self):
		t = self.cls()
		self.assertRaises(KeyError, t.floor, 10)
		self.assertRaises(KeyError, t.ceiling, 10)
		for i in -1, 5, 10:
			t._insert(i, range(i))
		for i, f in {100: 10, 10.00001: 10, 10: 10, 9.9999: 5, 8: 5, 5: 5, 0: -1,
					 -0.99999: -1, -1: -1}.items():
			self.assertEqual(f, t.floor(i))
		self.assertRaises(KeyError, t.floor, -1.000001)
		self.assertRaises(KeyError, t.floor, -10)
		for i, c in {-10: -1, -1.000001: -1, -1: -1, -0.99999: 5, 2: 5, 5: 5,
					 9: 10, 9.999999: 10, 10: 10}.items():
			self.assertEqual(c, t.ceiling(i))
		self.assertRaises(KeyError, t.ceiling, 10.000001)
		self.assertRaises(KeyError, t.ceiling, 11)

	def test_sorting(self):
		t = self.cls()
		data = list(self.data)
		random.shuffle(data)
		for i in data:
			t._insert(i, i)
		data.sort()
		self.assertEqual(data, list(t))
		t = self.cls()
		data = list(self.data)
		random.shuffle(data)
		for i in data:
			t._insert(i, i)
		data.sort()
		self.assertEqual(list(reversed(data)), list(reversed(t)))

	def test_bool(self):
		t = self.cls()
		self.assertFalse(t)
		t._insert(1, 1)
		self.assertTrue(t)

	def test_width(self):
		t = self.cls()
		self.assertEqual(0, t.width(0, 10))
		for i in range(10):
			t._insert(i, i)
		self.assertEqual(10, t.width(-1, 11))
		self.assertEqual(10, t.width(0, 10))
		self.assertEqual(9, t.width(0, 9))
		for i in range(10):
			for j in range(10):
				self.assertEqual(abs(i - j), t.width(i, j))

	def test_rank_select(self):
		t = self.cls()
		self.assertEqual(t.rank(10), 0)
		self.assertRaises(IndexError, t.select, 0)
		for i in range(10):
			t._insert(i, chr(i))
			self.assertEqual(i + 1, t.rank(10))
			self.assert_rank_consistent(t._root)
		self.assertEqual(0, t.rank(-1))

	def assert_rank_consistent(self, n):
		"""Check that ranks of node `n` are internally consistent.

		Specifically, test that `n.select` and `n.rank` are inverse functions.
		"""
		for i in range(len(n)):
			self.assertEqual(i, n.rank(n.select(i)))
		for key in n:
			self.assertEqual(key, n.select(n.rank(key)))

	def test_range(self):
		t = self.cls()
		for lo in -1, 0, 1, None:
			for hi in -1, 0, 1, None:
				self.assertEqual([], list(t.__iter__(lo=lo, hi=hi)))
				self.assertEqual([], list(t.__reversed__(lo=lo, hi=hi)))
		for i in range(3):
			t._insert(i, i)
		def toargs(lh): return {'lo': lh[0], 'hi': lh[1]}
		for lohi in (None, None), (-1, 3), (0, 3), (None, 3), (0, None):
			self.assertEqual([0, 1, 2], list(t.__iter__(**toargs(lohi))))
			self.assertEqual([2, 1, 0], list(t.__reversed__(**toargs(lohi))))
		for lohi in (0, 2), (-.5, 1.5):
			self.assertEqual([0, 1], list(t.__iter__(**toargs(lohi))))
			self.assertEqual([1, 0], list(t.__reversed__(**toargs(lohi))))
		for lohi in (1, 1.0001), (0.99, 1.001), (0.0001, 2):
			self.assertEqual([1], list(t.__iter__(**toargs(lohi))), lohi)
			self.assertEqual([1], list(t.__reversed__(**toargs(lohi))), lohi)
		for lohi in (1, 1), (2, 0), (3, 0), (4, -1):
			self.assertEqual([], list(t.__iter__(**toargs(lohi))), lohi)
			self.assertEqual([], list(t.__reversed__(**toargs(lohi))), lohi)

class TestOrderedMapping(unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.OrderedMapping
		self.data = [(i, chr(i)) for i in range(2 * RECURSION_LIMIT)]

	def assert_contents(self, m, contents):
		self.assertEqual(len(contents), len(m))
		for k, v in contents.items():
			self.assertIn(k, m)
			self.assertEqual(v, m[k])
		count = 0
		for k in m:
			self.assertIn(k, contents)
			count += 1
		self.assertEqual(count, len(contents))
		count = 0
		for k in m.keys():
			self.assertIn(k, contents)
			count += 1
		self.assertEqual(count, len(contents))
		count = 0
		for k, v in m.items():
			self.assertEqual(v, contents[k])
			count += 1
		self.assertEqual(count, len(contents))
		count = 0
		contents_values = contents.values()
		for v in m.values():
			self.assertIn(v, contents_values)
			count += 1
		self.assertEqual(count, len(contents))

	def test_create_empty_and_add(self):
		m = self.cls()
		contents = {}
		self.assert_contents(m, contents)
		for k, v in self.data[:100]:
			m[k] = v
			contents[k] = v
			self.assert_contents(m, contents)

	def test_init_with_dict(self):
		d = dict(self.data)
		m = self.cls(d)
		self.assert_contents(m, d)

	def test_init_with_list(self):
		m = self.cls(self.data)
		self.assert_contents(m, dict(self.data))

	def test_create_empty_update_dict(self):
		m = self.cls()
		self.assert_contents(m, {})
		d = dict(self.data)
		m.update(d)
		self.assert_contents(m, d)

	def test_create_empty_update_list(self):
		m = self.cls()
		self.assert_contents(m, {})
		m.update(self.data)
		self.assert_contents(m, dict(self.data))

	def test_init_with_data_then_update(self):
		data_start = dict(self.data[:3*len(self.data)//4])
		data_update = dict(self.data[2*len(self.data)//4:])
		m = self.cls(data_start)
		self.assert_contents(m, data_start)
		m.update(data_update)
		data_start.update(data_update)
		self.assert_contents(m, data_start)

	def test_bad_data(self):
		self.assertRaises(TypeError, self.cls, [1, 2, 3])
		m = self.cls()
		self.assertRaises(TypeError, m.update, [1, 2, 3])
		self.assertRaises(TypeError, m.__setitem__, [1, 2, 3])


class TestOrderedSet(unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.OrderedSet
		self.data = list(range(2 * RECURSION_LIMIT))

	def assert_contents(self, s, contents):
		self.assertEqual(len(contents), len(s))
		for i in contents:
			self.assertIn(i, s)
			self.assertEqual(i, s.search(i))
		count = 0
		for i in s:
			self.assertIn(i, contents)
			count += 1
		self.assertEqual(count, len(contents))

	def test_create_empty_and_add(self):
		s = self.cls()
		contents = set()
		self.assert_contents(s, contents)
		for i in self.data[:100]:
			s.add(i)
			contents.add(i)
			self.assert_contents(s, contents)

	def test_init_with_list(self):
		s = self.cls(self.data)
		self.assert_contents(s, self.data)

	def test_create_empty_update_list(self):
		s = self.cls()
		self.assert_contents(s, [])
		s |= self.data
		self.assert_contents(s, self.data)

	def test_init_with_data_then_update(self):
		data_start = set(self.data[:3*len(self.data)//4])
		data_update = set(self.data[2*len(self.data)//4:])
		s = self.cls(data_start)
		self.assert_contents(s, data_start)
		s |= data_update
		data_start |= data_update
		self.assert_contents(s, data_start)

	def test_bad_data(self):
		self.assertRaises(TypeError, self.cls, 1)
		s = self.cls()
		self.assertRaises(TypeError, self.cls.__ior__, 1)

	def test_sort(self):
		data = list(range(2 * RECURSION_LIMIT))
		rnddata = list(data)
		random.shuffle(rnddata)
		self.assertNotEqual(data, rnddata)
		self.assertEqual(data, list(self.cls(rnddata)))
		self.assertEqual(list(reversed(data)), list(reversed(self.cls(rnddata))))

	def test_deduplication(self):
		data = [i % 10  for i in range(100)]
		self.assertEqual([i for i in range(10)], list(self.cls(data)))


if __name__ == '__main__':
	unittest.main()
