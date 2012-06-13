#!/usr/bin/env python
#
# Copyright (C) 2012 JT Olds
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Open Header/Body plugin for Gedit3
https://github.com/jtolds/gedit3-openheader

Originally written for Gedit2 by Pierre-Luc Beaudoin
<pierre-luc.beaudoin@collabora.co.uk>, this plugin was rewritten for Gedit3 by
JT Olds.
"""

__author__ = "JT Olds"
__email__ = "hello@jtolds.com"

import os
from gi.repository import GObject, Gtk, Gedit, Gio

UI_XML = """<ui>
<menubar name="MenuBar">
  <menu name="ToolsMenu" action="Tools">
    <placeholder name="ToolsOps_3">
      <menuitem name="Open Header" action="OpenHeaderAction"/>
    </placeholder>
  </menu>
</menubar></ui>"""

class OpenHeader(GObject.Object, Gedit.WindowActivatable):
  __gtype_name__ = "OpenHeader"
  window = GObject.property(type=Gedit.Window)

  def __init__(self):
    GObject.Object.__init__(self)

  def _add_ui(self):
    manager = self.window.get_ui_manager()
    self._actions = Gtk.ActionGroup("OpenHeaderActions")
    self._actions.add_actions([
        ('OpenHeaderAction', Gtk.STOCK_INFO, "Open _Header/Body",
            "<control>r", "Open the corresponding header/body file",
            self.on_action_activate),
      ])
    manager.insert_action_group(self._actions)
    self._ui_merge_id = manager.add_ui_from_string(UI_XML)
    manager.ensure_update()

  def _remove_ui(self):
    manager = self.window.get_ui_manager()
    manager.remove_ui(self._ui_merge_id)
    manager.remove_action_group(self._actions)
    manager.ensure_update()

  def on_action_activate(self, action, data=None):
    doc = self.window.get_active_document()
    if not doc: return
    loc = doc.get_location()
    if not loc: return
    path = loc.get_path()
    root, ext = os.path.splitext(path)
    if ext.lower() in (".h", ".hpp"):
      new_extensions = [".c", ".cpp"]
    elif ext.lower() in (".c", ".cpp"):
      new_extensions = [".h", ".hpp"]
    else:
      return
    other = None
    for ext in new_extensions:
      for case in [ext.lower(), ext.upper()]:
        if os.path.isfile(root + case):
          other = root + case
          break
    if not other: return
    for doc in self.window.get_documents():
      loc = doc.get_location()
      if not loc: continue
      path = loc.get_path()
      if path == other:
        tab = Gedit.Tab.get_from_document(doc)
        if not tab: continue
        self.window.set_active_tab(tab)
        return
    self.window.create_tab_from_location(Gio.file_new_for_path(other), None,
        0, 0, False, True)

  def do_activate(self):
    self._add_ui()

  def do_deactivate(self):
    self._remove_ui()
