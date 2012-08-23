#!/usr/bin/env python3

import unittest
import tempfile
import os
import time
import functools
import organize
import random
import itertools
import collections

RANDOM_SEED = 0xdeadbeef

def setUpModule():
	random.seed(RANDOM_SEED)

class OrganizeScenario:

	"Set up basic scenario for organize.py to operate on"

	vcs = organize.Git

	def setup_dirs(self):
		return tempfile.TemporaryDirectory(), tempfile.TemporaryDirectory()

	def setUp(self):
		self.old_dir, self.new_dir = self.setup_dirs()
		self.old_files = self.setup_old_dir(self.old_dir.name)
		self.new_repo = self.setup_new_repo(self.new_dir.name)

	def setup_new_repo(self, dir):
		repo = self.vcs(dir)
		repo.init()
		self.assertIn('master', repo.branches)
		return repo

	def setup_old_dir(self, dir):
		files = self.setup_file_names()
		total = len(files)
		for count, file, time in zip(itertools.count(), files, self.SetUpFileTimes(total)):
			files[count] = abspath = os.path.join(dir, file)
			if os.path.sep in file:
				os.mkdirs(os.path.dirname(abspath), mode=0o600, exist_ok=True)
			self._excl_touch(abspath, time)
			self.assertEqual(os.path.getmtime(abspath), time)
		return files

	def setup_file_names(self):
		"Return a list of file names"
		return ['file' + str(i) for i in range(10)]

	def _excl_touch(self, path, time=None):
		"""Safely write a random file, optionally setting access and modification times.

		`path` must be an absolute path. `time`, if specified, is an int or
		float in seconds.
		"""
		if not os.path.isabs(path):
			raise ValueError('Expected absolute path but got %r' % path)
		file_len = random.randint(0x100,  0x1ff)
		file_content = bytes([random.randint(0, 0xff) for i in range(file_len)])
		with open(path, 'xb') as f:
			f.write(file_content)
		if time is not None:
			os.utime(path, (time, time))

	class SetUpFileTimes(collections.abc.Iterator):

		"Iterator of date-times to be used for `total` files"

		time_interval = 3600 # Seconds

		def __init__(self, total):
			self.total = total
			self.count = 0
			self.start = int(time.time() - total * self.time_interval)

		def __next__(self):
			if self.count >= self.total:
				raise StopIteration
			time = int(self.start + self.count * self.time_interval)
			self.count += 1
			return time

	def tearDown(self):
		self.old_dir.cleanup()
		self.new_dir.cleanup()

	def run_main(self, *args):
		try:
			organize.main(args)
		except SystemExit as e:
			return e.code


class TestAssumptionsCorrect(OrganizeScenario, unittest.TestCase):

	"Basic test of ogranize.py on a simple case when its assumptions are correct"

	def runTest(self):
		rc = self.run_main('--source', self.old_dir.name, '--repo', self.new_dir.name, 'test-branch')
		self.assertEqual(rc, 0)
		log_entries = self.new_repo.issue_command('log', '--oneline',
				'--all-match', '--grep="^Auto-add.*"').split('\n')
		self.assertEqual(len(log_entries), len(self.old_files))


