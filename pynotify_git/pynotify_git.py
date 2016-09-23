#!/usr/bin/env python

import os
import re
import pyinotify
import argparse
from git import Git, Repo, Head, exc

path_filter = [ 
	".*\.git*", 		# git repo
	".*\.swp*", 		# vim swap files
	".*4913$", ".*5036$",	# vim tmp file that makes sure the directory
	".*5159$", ".*5282$",	# is writable for swap files.
] 

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		for filter in path_filter:
			if (re.match(filter, event.pathname)):
				return

		print("File created %s !" % event.pathname)


	def process_IN_MODIFY(self, event):
		for filter in path_filter:
			if (re.match(filter, event.pathname)):
				return

		print("File modified %s !" % event.pathname)


def init_inotify():
	wm = pyinotify.WatchManager()
	mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY

	handler = EventHandler()
	notifier = pyinotify.Notifier(wm, handler)
	wdd = wm.add_watch(args.dir, mask, rec = True)
	notifier.loop()


def init_git():
	# Create Repository object.
	try:
		repo = Repo(args.dir)
	except exc.InvalidGitRepositoryError as e:
		print("dir is not versioned.\n")
		exit(0)
	except exc.NoSuchPathError as e:
		print("dir does not exist.\n")
		exit(0)
	

parser = argparse.ArgumentParser(description = 'Automatically create git commit when a file is saved')
parser.add_argument('--dir', default = "",
	            help = 'Directory to watch.')
args = parser.parse_args()

init_git()
init_inotify()

