
import gi
from gi.repository import Gtk, GObject, Gedit, Gio, PeasGtk
import subprocess
import os
import os.path
from os.path import expanduser
#import pdb; pdb.set_trace()

HOME=expanduser("~")
FILENAME = HOME+"/.codebeautifier"
TREEVIEW = None
ACCELERATOR = ['<Control><Alt>b']
LANGUAGE = "google"
STYLES = [ "1tbs", "banner", "allman", "gnu", "google", "horstmann", "java",
           "kr", "linux", "lisp", "pico", "stroustrup", "whitesmith" ]

################## FUNCTIONS ##################
def get_index(listval, strval):
    for itemval in listval:
        if itemval == strval:
            return listval.index(strval)
    return 0

def _save_setting(TALK):
    global LANGUAGE
    global FILENAME
    w_file = open(FILENAME, "w")
    w_file.write(TALK)
    w_file.close()

def _load_setting():
    global FILENAME
    if os.path.isfile(FILENAME):
        r_file = open(FILENAME, "r")
        LLANGUAGE=r_file.read()
        r_file.close()
    else:
        LLANGUAGE = "google"
        _save_setting(LLANGUAGE)
    if not LLANGUAGE:
        LLANGUAGE = "google"
    return LLANGUAGE


################## ADD MENU ##################
class CodeBeautifierPluginAppActivatable(GObject.Object, Gedit.AppActivatable, PeasGtk.Configurable):
    __gtype_name__ = "CodeBeautifierPlugin"
    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        GObject.Object.__init__(self)
        LANGUAGE = _load_setting()

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


################## ADD ACTION ##################
class CodeBeautifierPluginWindowActivatable(GObject.Object, Gedit.WindowActivatable, PeasGtk.Configurable):
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new("org.gnome.gedit.preferences.editor")
        LANGUAGE = _load_setting()

    def do_create_configure_widget(self):
        return CodeBeautifierPluginOptions.get_instance().create_configure_dialog()

    def do_activate(self):
        action = Gio.SimpleAction(name="codebeautifier")
        action.connect('activate', self.format_code)
        self.window.add_action(action)

    def format_code(self, action, parameter, user_data=None):
        global LANGUAGE
        document = self.window.get_active_document()
        if not document:
            return
        start, end = document.get_bounds()
        code = document.get_text(start, end, True)
        result = self.go(code)
        document.set_text(str(result, 'utf-8'))

    def go (self, code):
        global LANGUAGE

        if LANGUAGE == None:
            return code

        command = ["~/.local/share/gedit/plugins/code-beautifier/code_beautifier/astyle --style="+LANGUAGE+" --indent=tab"]

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        process.stdin.write(bytes(code, 'utf-8'))
        process.stdin.close()
        return process.stdout.read()

################## OPTIONS DIALOG ##################
class CodeBeautifierPluginOptions(object):

    ## static singleton reference
    singleton = None

    def __init__(self):
        global LANGUAGE
        LANGUAGE = _load_setting()

    @classmethod
    def get_instance(cls):
        if cls.singleton is None:
            cls.singleton = cls()
        return cls.singleton

    def _selection_changed(first, second):
        global LANGUAGE
        global TREEVIEW
        (model, iter) = second.get_selected()
        LANGUAGE = model[iter][0]
        indexval = get_index(STYLES, LANGUAGE)
        TREEVIEW.set_cursor(indexval);
        _save_setting(LANGUAGE)
        return True

    def create_configure_dialog(self):
        global LANGUAGE
        global TREEVIEW

        vbox = Gtk.VBox()
        vbox.set_border_width(6)

        liststore = Gtk.ListStore(str)
        for styles_ref in STYLES:
            liststore.append([styles_ref])

        TREEVIEW = Gtk.TreeView(liststore)
        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn('Language Styles')
        column.pack_start(cell, True)
        column.set_attributes(cell, text=0)
        column.set_sort_column_id(0)
        TREEVIEW.append_column(column)
        indexval = get_index(STYLES, LANGUAGE)
        TREEVIEW.set_cursor(indexval);
        tree_selection = TREEVIEW.get_selection()
        tree_selection.connect("changed", self._selection_changed)

        vbox.pack_start(TREEVIEW, False, False, 0)

        print(LANGUAGE + ":" + str(indexval));

        return vbox
