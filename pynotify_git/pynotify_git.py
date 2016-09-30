#!/usr/bin/env python

import os
import re
import pyinotify
import argparse
import datetime
from git import Git, Repo, Head, exc

path_filter = [ 
    ".*\.git*", 		# git repo
    ".*\.swp*", 		# vim swap files
    ".*4913$", ".*5036$",	# vim tmp file that makes sure the directory
    ".*5159$", ".*5282$",	# is writable for swap files
    ".*\.blend@$", ".*\.blend[0-9]+$", # Blender tmp files.
]

class EventHandler(pyinotify.ProcessEvent):
  def process_IN_CREATE(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File created %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    repo.index.commit("save %s" % event.pathname)

  def process_IN_MODIFY(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File modified %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    repo.index.commit("save %s" % event.pathname)

  def process_IN_MOVED_TO(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File moved %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    repo.index.commit("save %s" % event.pathname)


def __format_time():
  return datetime.datetime.now().strftime('%d%m%Y')


def launch_inotify():
  wm = pyinotify.WatchManager()
  mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO

  handler = EventHandler()
  notifier = pyinotify.Notifier(wm, handler)
  wdd = wm.add_watch(args.dir, mask, rec = True)
  notifier.loop()


parser = argparse.ArgumentParser(description = 'Automatically create git commit when a file is saved')
parser.add_argument('--dir', default = "",
                    help = 'Directory to watch.')
args = parser.parse_args()

try:
  # Create Repository object.
  repo = Repo(args.dir)

  # Create a new head (<=> branch) for today's dev.
  try:
	  dev_branch = repo.heads["dev/%s" % __format_time()]
  except IndexError:
	  dev_branch = repo.create_head("dev/%s" % __format_time())

  # And work on this new branch.
  dev_branch.checkout()
except exc.InvalidGitRepositoryError as e:
  print("dir is not versioned.\n")
  exit(1)
except exc.NoSuchPathError as e:
  print("dir does not exist.\n")
  exit(1)

launch_inotify()

