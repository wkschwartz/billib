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
import contextlib
import fnmatch

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
		return Git.validate_branch_name(ref)

	@staticmethod
	@_rename('directory name')
	def _dir_name(path):
		path = truepath(path)
		if not os.path.isdir(path):
			raise ValueError
		return path

	def __init__(self, *args, description=__doc__,
				 epilog="Commits are ordered by files' last-modified date.", **kwargs):
		super().__init__(*args, description=description, epilog=epilog, **kwargs)
		self.add_argument('--source', type=self._dir_name,
				help="source directory (default: '.')", default='.')
		self.add_argument('--filter',
				help="file name pattern to search SOURCE for (default: '*')")
		self.add_argument('--repo', type=self._dir_name,
				help="destination repository (default: '.')", default='.')
		self.add_argument('--name', type=str,
				help="name to use for file in repo (default: first version's)")
		self.add_argument('--recurse', action='store_true',
				help='include subdirectories of source directory in file search')
		self.add_argument('--force', action='store_true',
				help="assume answer is 'yes' to all safety prompts")
		self.add_argument('--verbose', action='store_true',
				help='verbose mode: say what is happening')
		self.add_argument('branch', type=self._new_ref_name,
				help='branch to create')


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

	def listdir(self, start, ignore=('.git',)):
		root, normpath, join = self.root, os.path.normpath, os.path.join
		for parent, children, files in os.walk(join(root, start)):
			for baddir in ignore:
				if baddir in children:
					children.remove(baddir)
			for items in children, files:
				for item in items:
					yield normpath(join(root, start, parent, item))


class Git:

	def __init__(self, repo):
		self.repo = os.path.abspath(repo)

	@contextlib.contextmanager
	def cd(self, dir=None):
		if dir is None:
			dir = self.repo
		oldcwd = os.getcwd()
		os.chdir(dir)
		yield self.repo
		os.chdir(oldcwd)

	@property
	def branches(self):
		with self.cd():
			stdout = subprocess.check_output(['git', 'branch', '-a'])
		return stdout.decode(sys.getfilesystemencoding()).split('\n')

	@classmethod
	def validate_branch_name(cls, ref):
		# See http://git-scm.com/docs/git-check-ref-format.html
		if '"' in ref or '\n' in ref:
			raise ValueError
		# check-ref-format will output prefix + ref, so prepare to chop of prefix
		prefix = '"refs/heads/'
		cmd = 'git check-ref-format --normalize ' + prefix + '{!s}"'.format(ref)
		normalized = subprocess.check_output(cmd.split())[len(prefix):-2]
		if not normalized:
			raise ValueError('Bad branch name: {!r}'.format(ref))
		return normalized

	def was_modified(self, file):
		with self.cd():
			status = subprocess.check_output('git status --porcelain'.split())
			return file.encode(sys.getfilesystemencoding()) in status

	def checkout_branch(self, branch):
		with self.cd():
			return subprocess.check_call(['git', 'checkout', '-b', branch])

	def commit_file(self, file, message, date=None):
		args = ['git', 'commit', '--message="' + message + '"']
		if date:
			args.extend(['--date="{!s}"'.format(date)])
		# XXX Make sure nothing else is staged. Get a lock if possible?
		with self.cd():
			subprocess.check_call(['git', 'add', file])
			subprocess.check_call(args)

	def issue_command(self, *args):
		args = list(args)
		with self.cd():
			return subprocess.check_output(['git'] + args)

	def datetime_from_timestamp(self, timestamp):
		"Convert local time in seconds since epoch to a RFC-2822-compliant time stamp"
		# See http://docs.python.org/py3k/library/time.html#time.strftime
		return time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime(timestamp))


def copy_ext(old, new):
	"Give new the same file extension that old had"
	root, ext = os.path.splitext(old)
	return new + ext


def main(args):
	parser = ArgumentParser()
	args = parser.parse_args(args)
	git = Git(args.repo)
	if args.recurse:
		ls = RecursiveSortedFiles(args.source)
	else:
		ls = SortedFiles(args.source)
	if args.name is None:
		args.name = os.path.basename(next(iter(ls)))
	# Find out if the file's been modified
	if git.was_modified(args.name):
		if not args.force:
			resp = input(args.name + ' modified in working tree. Overwrite? ')
			if resp.lower() not in ['y', 'yes', 'ok', 'okay', '1']:
				parser.error(args.name + ' modified in working tree.')
				assert False, 'NOTREACHED'
	# Create the branch
	git.checkout_branch(args.branch)
	count = 0
	for file, timestamp in ls.items():
		if not fnmatch.fnmatch(os.path.basename(file), args.filter):
			continue
		name = copy_ext(file, args.name)
		if args.verbose:
			print('Copying {!r} to {!r}'.format(file, name))
		shutil.copy2(file, os.path.join(args.repo, name))
		msg = 'Auto-add {!r} as {!r}.'.format(os.path.basename(file), name)
		date = git.datetime_from_timestamp(timestamp)
		git.commit_file(name, msg, date)
		count += 1
	print('Copied', count, 'file' + 's' * (count != 1) + '.')


if __name__ == '__main__':
	main(sys.argv[1:])
