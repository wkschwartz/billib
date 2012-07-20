#!/usr/bin/env python3

"Automatically create a Git repository out of a directory of versioned files."

import argparse
import os.path
import functools
import subprocess
import os
import shutil
import sys
import collections
import time
import operator

def truepath(path):
	p = os.path
	path = p.normcase(p.normpath(p.realpath(p.expanduser(path))))
	return path

class ArgumentParser(argparse.ArgumentParser):

	def _rename(name):
		@functools.wraps
		def wrapper(f):
			f.__name__ = name
			return f
		return wrapper

	@staticmethod
	@_rename('new git branch name')
	def _new_ref_name(ref):
		# See http://git-scm.com/docs/git-check-ref-format.html
		if '"' in ref or '\n' in ref:
			raise ValueError
		# check-ref-format will output prefix + ref, so prepare to chop of prefix
		prefix = '"refs/heads/'
		cmd = 'git check-ref-format --normalize ' + prefix + '{!s}"'.format(ref)
		return subprocess.check_output(cmd.split())[len(prefix):-2]

	@staticmethod
	@_rename('directory name')
	def _dir_name(path):
		path = truepath(path)
		if not os.path.isdir(path):
			raise ValueError
		return path

	def __init__(self, *args, description=__doc__,
				 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
				 **kwargs):
		super().__init__(description=description, formatter_class=formatter_class,
				*args, **kwargs)
		self.add_argument('-s', '--source', nargs='?', type=self._dir_name,
				help='Source directory', default='.')
		self.add_argument('-r', '--repo', nargs='?', type=self._dir_name,
				help='Destination repository', default='.')
		self.add_argument('-n', '--name', type=str,
				help="Name to use for file in repo (default: first version's name")
		self.add_argument('-d', '--delete', action='store_true',
				help='Delete files as they are successfully added to the repo')
		self.add_argument('-R', '--recurse', action='store_true',
				help='Include subdirectories of source directory in file search')
		self.add_argument('-f', '--force', action='store_true',
				help="Assume answer is 'yes' to all safety prompts")
		self.add_argument('-v', '--verbose', action='store_true',
				help='Verbose mode: say what is happening')
		self.add_argument('branch', type=self._new_ref_name,
				help='Branch to create')


def RFC2822timestamp(secs_since_epoch):
	"Convert local time in seconds since epoch to a RFC-2822-compliant time stamp"
	# See http://docs.python.org/py3k/library/time.html#time.strftime
	return time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(secs_since_epoch))


class SortedFiles(collections.OrderedDict):

	def __init__(self, root, key=os.path.getmtime):
		self._root = root
		self._key = key
		filtered_files = filter(self.relevant, self.listdir(root))
		files_gen = ((f, key(f)) for f in filtered_files)
		super().__init__(sorted(files_gen, key=operator.itemgetter(1)))

	@property
	def root(self):
		return self._root

	@staticmethod
	def relevant(file):
		p = os.path
		return (p.exists(file) and p.isfile(file) and not p.basename(file).startswith('.'))

	@staticmethod
	def listdir(root):
		return map(functools.partial(os.path.join, root), os.listdir(root))


class RecursiveSortedFiles(SortedFiles):

	def listdir(self, start):
		root, normpath, join = self.root, os.path.normpath, os.path.join
		for parent, children, files in os.walk(join(root, start)):
			if '.git' in children:
				children.remove('.git')
			for items in children, files:
				for item in items:
					yield normpath(join(root, start, parent, item))


def main(args):
	parser = ArgumentParser()
	args = parser.parse_args(args)
	if args.recurse:
		ls = RecursiveSortedFiles(args.source)
	else:
		ls = SortedFiles(args.source)
	if args.name is None:
		args.name = os.path.basename(next(iter(ls)))
	oldwd = os.getcwd()
	os.chdir(args.repo)
	try:
		# Find out if the file's been modified
		status = subprocess.check_output('git status --porcelain'.split())
		if args.name.encode(sys.getfilesystemencoding()) in status:
			if not args.force:
				resp = input(args.name + ' modified in working tree. Overwrite? ')
				if resp.lower() not in ['y', 'yes', 'ok', 'okay', '1']:
					parser.error(args.name + ' modified in working tree.')
					assert False, 'NOTREACHED'
		# Create the branch
		subprocess.check_call(['git', 'checkout', '-b', args.branch])
		for file, timestamp in ls.items():
			if args.verbose:
				print('Copying {!r} to {!r}'.format(file, args.name))
			shutil.copy2(file, args.name)
			subprocess.check_call(['git', 'add', args.name])
			msg = '--message="Auto-add {!r} as {!r}."'.format(
					os.path.basename(file), args.name)
			date = '--date="' + RFC2822timestamp(timestamp) + '"'
			subprocess.check_call(['git', 'commit', date, msg])
			if args.delete:
				os.unlink(file)
	finally:
		os.chdir(oldwd)
if __name__ == '__main__':
	main(sys.argv[1:])
