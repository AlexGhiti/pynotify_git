#!/usr/bin/env python

import os
import re
import pyinotify
import argparse
import datetime
from git import Git, Repo, Head, exc
os.environ['KIVY_TEXT'] = 'pil'
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.lang import Builder

Window.size = (500, 200)

path_filter = [ 
    ".*\.git*", 		# git repo
    ".*\.swp*", 		# vim swap files
    ".*4913$", ".*5036$",	# vim tmp file that makes sure the directory
    ".*5159$", ".*5282$",	# is writable for swap files
    ".*\.blend@$", ".*\.blend[0-9]+$", # Blender tmp files.
]

# Object that polls for inotify events.
notifier = None

class PynotifyGitApp(App):
  layout = None
  text_commit = None
  text_branch = None

  def valid_commit(instance, value):
    # Here, modified/created/... files have already been 
    # added by inotify event handlers, we just have to change
    # the branch and push the commit according to what user
    # entered.
    branch_name = instance.text_branch.text
    if (branch_name != "" and branch_name != "Branch"):
      try:
        dev_branch = repo.heads["%s" % branch_name]
      except IndexError:
        dev_branch = repo.create_head("%s" % branch_name)

      # And work on this new branch.
      dev_branch.checkout()

    repo.index.commit("%s" % instance.text_commit.text)
    Window.minimize()

  def exit_app(*largs):
    notifier.stop()
    kivy_app.stop()

  def restore(*largs):
    for arg in largs:
      print(arg)

  def build(self):
    self.text_branch = TextInput(text = "Branch", multiline = False)
    self.text_commit = TextInput(text = "Commit", Focus = True)
    btn = Button(text = "Ok")
    btn.bind(on_press = self.valid_commit)

    self.layout = GridLayout(cols = 1, row_force_default = True, row_default_height = 55,
		    				col_force_default = True, col_default_width = 480,
						padding = 10, spacing = 10);
    self.layout.add_widget(self.text_branch);
    self.layout.add_widget(self.text_commit);
    self.layout.add_widget(btn);
    
    Window.bind(on_close = self.exit_app)
    Window.bind(on_restore = self.restore)
    Window.minimize()

    return self.layout

class EventHandler(pyinotify.ProcessEvent):
  def process_IN_CREATE(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File created %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    Window.restore()

  def process_IN_MODIFY(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File modified %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    Window.restore()

  def process_IN_MOVED_TO(self, event):
    for filter in path_filter:
      if (re.match(filter, event.pathname)):
        return

    print("File moved %s !" % event.pathname)
    repo.index.add([event.pathname]) 
    Window.restore()

def launch_inotify():
  wm = pyinotify.WatchManager()
  mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_MOVED_TO

  handler = EventHandler()
  notifier = pyinotify.ThreadedNotifier(wm, handler)
  wdd = wm.add_watch(args.dir, mask, rec = True)
  notifier.start()


parser = argparse.ArgumentParser(description = 'Automatically create git commit when a file is saved')
parser.add_argument('--dir', default = "",
                    help = 'Directory to watch.')
args = parser.parse_args()

try:
  # Create Repository object.
  repo = Repo(args.dir)
except exc.InvalidGitRepositoryError as e:
  print("dir is not versioned.\n")
  exit(1)
except exc.NoSuchPathError as e:
  print("dir does not exist.\n")
  exit(1)

if __name__ == "__main__":
  notifier = launch_inotify()
  kivy_app = PynotifyGitApp()
  kivy_app.run()
  print("Finished !")

