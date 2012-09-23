from collections.abc import Set, MutableSet, Mapping, MutableMapping

class LeftLeaningRedBlackTree:

	"""A Sedgwick red black tree with left-leaning red edges to support mapping."""

	__slots__ = 'left', 'right', 'color', 'key', 'value'

	RED = True
	BLACK = False

	def __init__(self, key, value, color):
		self.left = None
		self.right = None
		self.color = color
		self.key = key
		self.value = value

	def _get(self, key):
		root = self
		while root is not None:
			if key < root.key:
				root = root.left
			elif key > root.key:
				root = root.right
			else:
				return root.value
		raise KeyError('Cannot find key: {!r}'.format(key))

	def _insert(self, key, value):
		self = self.put(self, key, value)

	def __len__(self):
		if self.left is not None:
			leftlen = len(self.left)
		if self.right is not None:
			rightlen = len(self.right)
		return 1 + leftlen + rightlen

	def __iter__(self):
		if self.left is not None:
			yield from self.left
		yield self.key
		if self.right is not None:
			yield from self.right

	@staticmethod
	def _isred(self):
		if self is None:
			return False
		return self.color

	@staticmethod
	def _put(self, key, value):
		if self is None:
			return LeftLeaningRedBlackTree(key, value, RED)
		if key < self.key:
			self.left = self._put(self.left, key, value)
		elif key > self.key:
			self.right = self._put(self.right, key, value)
		else:
			self.value = value

		isred = self._isred
		if isred(self.right) and not isred(self.left):
			self = self._rotate_left()
		if isred(self.left) and isred(self.left.left):
			self = self._rotate_right()
		if isred(self.left) and isred(self.right):
			self = self._flip_colors()

		return self

	def _flip_colors(self):
		self.left.color = self.BLACK
		self.right.color = self.BLACK
		self.color = self.RED

	def _rotate_left(self):
		t = self.right
		self.right = t.left
		t.left = self
		t.color = self.color
		self.color = self.RED
		return t

	def _rotate_right(self):
		t = self.left
		self.left = t.right
		t.right = self
		t.color = self.color
		self.color = self.RED
		return t


