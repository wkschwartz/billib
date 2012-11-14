import unittest
import orderedset
import random

class TestLeftLeaningRedBlackTree(unittest.TestCase):

	def setUp(self):
		self.cls = orderedset.OrderedMapping
		self.data = tuple(chr(i + 0x20) for i in range(95))

	def test_int_keys_in_order(self):
		for i in range(len(self.data)):
			self._int_keys(self.data[:i])

	def test_int_keys_rand_order(self):
		for i in range(len(self.data)):
			data = list(self.data[:i])
			random.shuffle(data)
			self._int_keys(data)

	def _int_keys(self, data):
		t = self.cls()
		i = len(data)
		for j in range(i):
			self.assertEqual(j, len(t))
			self.assertNotIn(j, t)
			self.assertEqual(list(range(j)), list(t))
			t[j] = data[j]
			self.assertEqual(data[j], t[j])
			self.assertIn(j, t)
		self.assertEqual(i, len(t))
		self.assertEqual(list(range(len(data))), list(t))
		self.assertRaises(KeyError, t.__getitem__, i + 1)

	def test_insert_replaces(self):
		t = self.cls()
		t[1] = 'a'
		self.assertEqual('a', t[1])
		t[1] = 'b'
		self.assertEqual('b', t[1])

	def test_only_ordered_keys(self):
		t = self.cls()
		for k in None, object(), type, {}:
			self.assertRaises(TypeError, t.__getitem__, k, 'a')
			self.assertRaises(TypeError, t.__setitem__, k, 'a')

	def test_disjoint_keys(self):
		t = self.cls()
		t[{1}] = 'a'
		self.assertRaises(KeyError, t.__getitem__, set())
		self.assertRaises(TypeError, t.__getitem__, {2})
		self.assertRaises(TypeError, t.__setitem__, {2})

	def test_unhashable_keys(self):
		t = self.cls()
		for k in [], [1], [2]:
			t[k] = 'a'
			self.assertEqual(t[k], 'a')


class TestOrderedMapping(unittest.TestCase):

	def setUp(self):
		self.cls = orderedset.OrderedMapping
		self.data = [(i, chr(i)) for i in range(1000)]

	def assert_contents(self, m, contents):
		self.assertEqual(len(contents), len(m))
		count = 0
		for k, v in contents.items():
			self.assertIn(k, m)
			self.assertEqual(v, m[k])
			count += 1
		self.assertEqual(count, len(contents))
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
		self.assert_contents(m, {})
		m[1] = 'a'
		self.assert_contents(m, {1: 'a'})
		m[2] = 'b'
		self.assert_contents(m, {1: 'a', 2: 'b'})
		m[1] = 'c'
		self.assert_contents(m, {1: 'c', 2: 'b'})

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


if __name__ == '__main__':
	unittest.main()
