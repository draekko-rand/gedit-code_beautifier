
import gi
from gi.repository import Gtk, GObject, Gedit, Gio, PeasGtk
import subprocess
import os
import os.path
from os.path import expanduser
#import pdb; pdb.set_trace()

#OPTIONS=None
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

def _selection_changed(second):
    global LANGUAGE
    global TREEVIEW
    (model, iter) = second.get_selected()
    LANGUAGE = model[iter][0]
    indexval = get_index(STYLES, LANGUAGE)
    TREEVIEW.set_cursor(indexval);
    _save_setting(LANGUAGE)
    return True

def create_configure_dialog():
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
    tree_selection.connect("changed", _selection_changed)

    vbox.pack_start(TREEVIEW, False, False, 0)
    return vbox

################## ADD MENU ##################
class CodeBeautifierPluginAppActivatable(GObject.Object, Gedit.AppActivatable, PeasGtk.Configurable):
    __gtype_name__ = "CodeBeautifierPlugin"
    app = GObject.Property(type=Gedit.App)

    def __init__(self):
        global LANGUAGE
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
        global LANGUAGE
        GObject.Object.__init__(self)
        self.settings = Gio.Settings.new("org.gnome.gedit.preferences.editor")
        LANGUAGE = _load_setting()

    def do_create_configure_widget(self):
        print(" ")
        ret = create_configure_dialog()
        print(" ")
        return ret

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

        view = self.window.get_active_view()
        tabwidth = view.get_tab_width()
        tabval = str(tabwidth)
        maxwidth=view.get_right_margin_position()
        maxwidthval=str(maxwidth)
        command = ["~/.local/share/gedit/plugins/code_beautifier/code_beautifier/astyle --style="+LANGUAGE+" -xC"+ maxwidthval +" -c -s"+tabval]

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        process.stdin.write(bytes(code, 'utf-8'))
        process.stdin.close()
        return process.stdout.read()
