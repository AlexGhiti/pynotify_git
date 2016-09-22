#!/usr/bin/env python

import os
import re
import pyinotify
import argparse

path_filter = [ ".*\.git*", ".*\.swp*" ] 

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


parser = argparse.ArgumentParser(description = 'Automatically create git commit when a file is saved')
parser.add_argument('--dir', default = "",
                    help = 'Directory to watch.')

args = parser.parse_args()

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)
wdd = wm.add_watch(args.dir, mask, rec = True)

notifier.loop()
