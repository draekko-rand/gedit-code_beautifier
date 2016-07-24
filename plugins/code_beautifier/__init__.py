
from gi.repository import Gtk, GObject, Gedit, Gio
import subprocess
import gettext
import re
import textwrap

ACCELERATOR = ['<Control><Alt>l']

class CodeBeautifierPluginAppActivatable(GObject.Object, Gedit.AppActivatable):
    __gtype_name__ = "CodeBeautifierPlugin"
    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.app.set_accels_for_action("win.codebeautifier", ACCELERATOR)
        self.menu_ext = self.extend_menu("edit-section")
        item = Gio.MenuItem.new(_("Code Beautifier"), "win.codebeautifier")
        self.menu_ext.prepend_menu_item(item)

    def do_deactivate(self):
        self.app.set_accels_for_action("win.codebeautifier", [])
        self.menu_ext = None

    def do_update_state(self):
        pass


class CodeBeautifierPluginWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new("org.gnome.gedit.preferences.editor")

    def do_activate(self):
        action = Gio.SimpleAction(name="codebeautifier")
        action.connect('activate', self.format_code)
        self.window.add_action(action)

    def format_code(self, action, parameter, user_data=None):
        document = self.window.get_active_document()
        if not document:
            return
        start, end = document.get_bounds()
        code = document.get_text(start, end, True)
#        code = document.get_text(document.get_start_iter(), document.get_end_iter(), True)
        lang_id = self.window.get_active_view().get_buffer().get_language().get_id()
        result = self.go(code, lang_id)
        document.set_text(str(result, 'utf-8'))

    def go (self, code, lang_id):
        if lang_id == 'ruby':
            command = ["ruby ~/.local/share/gedit/plugins/code-beautifier/code_beautifier/ruby.rb - "]
        elif lang_id in ['php', 'c', 'c++', 'java', 'js']:
            command = ["~/.local/share/gedit/plugins/code-beautifier/code_beautifier/astyle --style=java --indent=tab"]
        else:
            return code

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        process.stdin.write(bytes(code, 'utf-8'))
        process.stdin.close()
        return process.stdout.read()

