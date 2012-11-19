import unittest
import orderedtable
import random
import sys
import math
import pickle


RECURSION_LIMIT = sys.getrecursionlimit()


class NodeChecker:

	"Check integrity of red-black BST data structure."

	class NodeError(AssertionError):
		"A left-leaning red-black tree invariant has been violated unexpectedly."

	def assertNode(self, h):
		"Check integrity of red-black BST data structure."
		if isinstance(h, orderedtable.BinarySearchTree):
			h = h._root
		if isinstance(h, orderedtable._NullNode):
			return True
		if not self._is_23_BST(h):
			raise self.NodeError("Not in symmetric order or not a 2-3 tree")
		if not self._is_rank_consistent(h):
			raise self.NodeError("Ranks not consistent")
		if not self._is_balanced(h):
			raise self.NodeError("Not balanced")
		return True

	def _is_23_BST(self, h, min=None, max=None):
		"""Check that h is a 2-3 tree in symmetric (binary search) order.

		Is `h` a BST?
		----------------
		Return whether this binary tree satisfies symmetric order.

		More specifically, return wehther the tree rooted at `h` a BST with all
		keys strictly between `min` and `max`. When those arguments aren't given
		(or they are `None`), this constraint is treated as non-binding. Thus,
		to test the root of a tree h, call as `_is_23_BST(h)`. Credit: Bob
		Dondero.

		Is `h` a 2-3 tree?
		---------------------
		Return wehther this tree properly models a 2-3 tree with red and black.

		Specifically, return wether the tree rooted at `h` has no red right
		links and at most one (left) red links in a row on any path.

		Is `h._N` correct?
		---------------------
		Return whether the field that tracks container size is correct.
		"""
		# Is 2-3 tree?
		isred = h._isred
		if isred(h._right): return False
		if isred(h) and isred(h._left): return False
		# Is BST?
		if min is not None and h._key <= min: return False
		if max is not None and h._key >= max: return False
		# Is length correct?
		if h._N != h._recursive_len():
			return False
		return ((h._left is None or self._is_23_BST(h._left, min, h._key)) and
				(h._right is None or self._is_23_BST(h._right, h._key, max)))

	def _is_rank_consistent(self, h):
		"""Check that ranks are internally consistent.

		Specifically, test that `h.select` and `h.rank` are inverse functions.
		"""
		for i in range(len(h)):
			if i != h.rank(h.select(i)):
				return False
		for key in h:
			if key != h.select(h.rank(key)):
				return False
		return True

	def _is_balanced(self, h):
		"Return whether all paths h to leaf have the same number of black edges."
		black = 0
		x = h
		while x is not None:
			if x._color != x._RED:
				black += 1
			x = x._left
		return self._is_balanced_all_paths(h, black)

	def _is_balanced_all_paths(self, h, black):
		"Return whether every path from h to leaf has the given number of black links"
		if h._color != h._RED:
			black -= 1
		l = black == 0 if h._left is None else self._is_balanced_all_paths(h._left, black)
		r = black == 0 if h._right is None else self._is_balanced_all_paths(h._right, black)
		return l and r


class TestBinarySearchTree(NodeChecker, unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.BinarySearchTree
		self.data = tuple(chr(i + 0x20) for i in range(95))

	def test_pickle(self):
		t = self.cls()
		self.assertNode(t)
		pickled = pickle.loads(pickle.dumps(t))
		self.assertNode(pickled)
		self.assertEqual(len(pickled), 0)
		for i in range(6):
			pickled._insert(i, chr(i))
			self.assertNode(pickled)
			pickled = pickle.loads(pickle.dumps(pickled))
			self.assertNode(pickled)
			self.assertEqual(len(pickled), i + 1)
			for j in range(i):
				self.assertEqual(chr(j), pickled._search(j))

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
		self.assertNode(t)
		for i in data:
			t._insert(i, i)
			self.assertNode(t)
		self.assertLessEqual(t._root.height(), 2.0 * math.log(size, 2))

	def test_height_after_ordered_insert(self):
		data = list(range(2 * RECURSION_LIMIT))
		size = len(data)
		t = self.cls()
		self.assertNode(t)
		for i in data:
			t._insert(i, i)
			self.assertNode(t)
		self.assertLessEqual(t._root.height(), 2.0 * math.log(size, 2))

	def _int_keys(self, data):
		t = self.cls()
		self.assertNode(t)
		self.assertEqual(t._root.height(), 0)
		i = len(data)
		for j in range(i):
			self.assertEqual(j, len(t))
			self.assertNotIn(j, t)
			self.assertEqual(list(range(j)), list(t))
			t._insert(j, data[j])
			self.assertNode(t)
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
		self.assertNode(t)
		t._insert(1, 'a')
		self.assertNode(t)
		self.assertEqual('a', t._search(1))
		t._insert(1, 'b')
		self.assertNode(t)
		self.assertEqual('b', t._search(1))

	def test_only_ordered_keys(self):
		t = self.cls()
		self.assertNode(t)
		for k in None, object(), type, {}:
			self.assertRaises(TypeError, t._search, k, 'a')
			self.assertRaises(TypeError, t._insert, k, 'a')

	def test_disjoint_keys(self):
		t = self.cls()
		self.assertNode(t)
		t._insert({1}, 'a')
		self.assertNode(t)
		self.assertRaises(KeyError, t._search, set())
		self.assertRaises(TypeError, t._search, {2})
		self.assertRaises(TypeError, t._insert, {2})

	def test_unhashable_keys(self):
		t = self.cls()
		self.assertNode(t)
		for k in [], [1], [2]:
			t._insert(k, 'a')
			self.assertNode(t)
			self.assertEqual(t._search(k), 'a')

	def test_min_max(self):
		t = self.cls()
		self.assertNode(t)
		self.assertRaises(ValueError, t.min)
		self.assertRaises(ValueError, t.max)
		data = list(self.data)
		random.shuffle(data)
		for item in data:
			t._insert(item, ord(item))
			self.assertNode(t)
		self.assertEqual(min(data), t.min())
		self.assertEqual(max(data), t.max())

	def test_floor_ceiling(self):
		t = self.cls()
		self.assertNode(t)
		self.assertRaises(KeyError, t.floor, 10)
		self.assertRaises(KeyError, t.ceiling, 10)
		for i in -1, 5, 10:
			t._insert(i, range(i))
			self.assertNode(t)
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
		self.assertNode(t)
		data = list(self.data)
		random.shuffle(data)
		for i in data:
			t._insert(i, i)
			self.assertNode(t)
		data.sort()
		self.assertEqual(data, list(t))
		t = self.cls()
		self.assertNode(t)
		data = list(self.data)
		random.shuffle(data)
		for i in data:
			t._insert(i, i)
			self.assertNode(t)
		data.sort()
		self.assertEqual(list(reversed(data)), list(reversed(t)))

	def test_bool(self):
		t = self.cls()
		self.assertNode(t)
		self.assertFalse(t)
		t._insert(1, 1)
		self.assertNode(t)
		self.assertTrue(t)

	def test_width(self):
		t = self.cls()
		self.assertNode(t)
		self.assertEqual(0, t.width(0, 10))
		for i in range(10):
			t._insert(i, i)
			self.assertNode(t)
		self.assertEqual(10, t.width(-1, 11))
		self.assertEqual(10, t.width(0, 10))
		self.assertEqual(9, t.width(0, 9))
		for i in range(10):
			for j in range(10):
				self.assertEqual(abs(i - j), t.width(i, j))

	def test_rank_select(self):
		t = self.cls()
		self.assertNode(t)
		self.assertEqual(t.rank(10), 0)
		self.assertRaises(IndexError, t.select, 0)
		for i in range(10):
			t._insert(i, chr(i))
			self.assertNode(t)
			self.assertEqual(i + 1, t.rank(10))
			self.assertEqual(i, t.select(i))
			self.assertEqual(i, t.rank(i))
			self.assertRaises(IndexError, t.select, i + 1)
		self.assertEqual(0, t.rank(-1))

	def test_range(self):
		t = self.cls()
		self.assertNode(t)
		for lo in -1, 0, 1, None:
			for hi in -1, 0, 1, None:
				self.assertEqual([], list(t.range(lo, hi)))
				self.assertEqual([], list(t.range(lo, hi, -1)))
		for i in range(3):
			t._insert(i, i)
			self.assertNode(t)
		for lo, hi in (None, None), (-1, 3), (0, 3), (None, 3), (0, None):
			self.assertEqual([0, 1, 2], list(t.range(lo, hi)))
			self.assertEqual([2, 1, 0], list(t.range(hi, lo, -1)))
		for lo, hi in (0, 2), (-.5, 1.5):
			self.assertEqual([0, 1], list(t.range(lo, hi)))
			self.assertEqual([1, 0], list(t.range(hi, lo, -1)))
		for lo, hi in (1, 1.0001), (0.99, 1.001), (0.0001, 2):
			self.assertEqual([1], list(t.range(lo, hi)))
			self.assertEqual([1], list(t.range(hi, lo, -1)))
		for lo, hi in (1, 1), (2, 0), (3, 0), (4, -1):
			self.assertEqual([], list(t.range(lo, hi)))
			self.assertEqual([], list(t.range(hi, lo, -1)))

class TestOrderedMapping(NodeChecker, unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.OrderedMapping
		self.data = [(i, chr(i)) for i in range(2 * RECURSION_LIMIT)]

	def assert_contents(self, m, contents):
		self.assertNode(m)
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

	def test_pickle(self):
		m = self.cls()
		self.assertNode(m)
		pickled = pickle.loads(pickle.dumps(m))
		self.assertNode(pickled)
		self.assertEqual(len(pickled), 0)
		for i in range(6):
			pickled[i] = chr(i)
			self.assertNode(pickled)
			pickled = pickle.loads(pickle.dumps(pickled))
			self.assertNode(pickled)
			self.assertEqual(len(pickled), i + 1)
			for j in range(i):
				self.assertEqual(chr(j), pickled[j])

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


class TestOrderedSet(NodeChecker, unittest.TestCase):

	def setUp(self):
		self.cls = orderedtable.OrderedSet
		self.data = list(range(2 * RECURSION_LIMIT))

	def assert_contents(self, s, contents):
		self.assertNode(s)
		self.assertEqual(len(contents), len(s))
		for i in contents:
			self.assertIn(i, s)
			self.assertEqual(i, s.search(i))
		count = 0
		for i in s:
			self.assertIn(i, contents)
			count += 1
		self.assertEqual(count, len(contents))

	def test_pickle(self):
		s = self.cls()
		self.assertNode(s)
		pickled = pickle.loads(pickle.dumps(s))
		self.assertNode(pickled)
		self.assertEqual(len(pickled), 0)
		for i in range(6):
			pickled.add(i)
			self.assertNode(pickled)
			pickled = pickle.loads(pickle.dumps(pickled))
			self.assertNode(pickled)
			self.assertEqual(len(pickled), i + 1)
			for j in range(i):
				self.assertEqual(j, pickled.search(j))

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
