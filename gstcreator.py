#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
except:
    print >> sys.stderr, "Error: PyGTK not installed"
    sys.exit(1)

if gtk.pygtk_version < (2,12,0):
    errtitle = "Error"
    errmsg = "PyGTK 2.12.0 or later required"
    if gtk.pygtk_version < (2,4,0):
        print >> sys.stderr, errtitle + ": " + errmsg
    else:
        errdlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK)
        errdlg.set_title(errtitle)
        errdlg.set_markup(errmsg)
        errdlg.run()
    sys.exit(1)


import os.path
UI_PATH = os.path.join(os.getcwd(), 'gstcreator.ui')
STCREATOR = '/usr/bin/stcreator'
SOUND_DIR = '/usr/share/sounds'

# For testing
#STCREATOR = '/home/wasabi/src/stcreator/stcreator.py'
#SOUND_DIR = '/home/wasabi/src'

class GSoundThemeCreator:

    def __init__(self):
        """Initializer"""

        uifile = UI_PATH
        self.xml = gtk.Builder()
        self.xml.add_from_file(uifile)
        self.xml.connect_signals(self)

        # set radio buttion
        self.xml.get_object('rb_install').set_active(True)

        # filters
        oggfilter = gtk.FileFilter()
        oggfilter.set_name('Ogg/WAV files')
        oggfilter.add_pattern('*.oga')
        oggfilter.add_pattern('*.ogg')
        oggfilter.add_pattern('*.wav')
        allfilter = gtk.FileFilter()
        allfilter.set_name('All files')
        allfilter.add_pattern('*')
        for fc in ['fc_login', 'fc_logout', 'fc_error', 'fc_warning', 'fc_information', 'fc_question', 'fc_sysready']:
            obj = self.xml.get_object(fc)
            obj.add_filter(oggfilter)
            obj.add_filter(allfilter)

        self.window = self.xml.get_object('mainwindow')
        self.window.show_all()

    def on_btn_apply_clicked(self, widget, *args):
        command = ''+STCREATOR
        needsu = False


        # --Title-------------------------------
        title = self.xml.get_object('ety_title').get_text()
        if title is None or title == '':
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self.window)
            dialog.set_markup('Specify theme title.')
            dialog.run()
            dialog.destroy()
            return
        command += ' --name='+title


        # --Distination-------------------------
        if self.xml.get_object('rb_install').get_active():
            needsu = not not os.geteuid()
            target = SOUND_DIR
        else:
            dist = self.xml.get_object('fc_distination').get_filename() or '~/'
            target = dist
        command += (' --target='+target)


        # --Sound files--------------------------
        if self.xml.get_object('cb_login').get_active():
            login = self.xml.get_object('fc_login').get_filename() or ''
            if login:
                command += (' --login='+login)
        if self.xml.get_object('cb_logout').get_active():
            logout = self.xml.get_object('fc_logout').get_filename() or ''
            if logout:
                command += (' --logout='+logout)
        if self.xml.get_object('cb_error').get_active():
            error = self.xml.get_object('fc_error').get_filename() or ''
            if error:
                command += (' --error='+error)
        if self.xml.get_object('cb_warning').get_active():
            warning = self.xml.get_object('fc_warning').get_filename() or ''
            if warning:
                command += (' --warning='+warning)
        if self.xml.get_object('cb_information').get_active():
            information = self.xml.get_object('fc_information').get_filename() or ''
            if information:
                command += (' --information='+information)
        if self.xml.get_object('cb_question').get_active():
            question = self.xml.get_object('fc_question').get_filename() or ''
            if question:
                command += (' --question='+question)
        if self.xml.get_object('cb_sysready').get_active():
            sysready = self.xml.get_object('fc_sysready').get_filename() or ''
            if sysready:
                command += (' --sysready='+sysready)


        # --Execute--------------------------
        import commands
        command = command.replace('"', '\\"') # escape
        command = command.replace('$', '\\$')
        command = command.replace('`', '\\`')
        command = command.replace('\\', '\\\\')
        command = needsu and ('gksu -D "Sound Theme Creator" "%s" ' % command) or command
        status, output = commands.getstatusoutput(command)

        if status:
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self.window)
            dialog.set_markup(output or 'Failed to create theme')
            dialog.run()
            dialog.destroy()
        else:
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
            dialog.set_transient_for(self.window)
            dialog.set_markup('Successfully done'+(not needsu and ('\nSee: %s' % target) or ''))
            dialog.run()
            dialog.destroy()

    def on_fc_file_set(self, widget, *args):
        location = widget.get_current_folder()
        for fc in ['fc_login', 'fc_logout', 'fc_error', 'fc_warning', 'fc_information', 'fc_question', 'fc_sysready']:
            obj = self.xml.get_object(fc)
            obj.get_filename() or obj.set_current_folder(location)

    def on_cb_login_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_login')
        fc.set_sensitive(widget.get_active())

    def on_cb_logout_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_logout')
        fc.set_sensitive(widget.get_active())

    def on_cb_error_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_error')
        fc.set_sensitive(widget.get_active())

    def on_cb_warning_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_warning')
        fc.set_sensitive(widget.get_active())

    def on_cb_information_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_information')
        fc.set_sensitive(widget.get_active())

    def on_cb_question_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_question')
        fc.set_sensitive(widget.get_active())

    def on_cb_sysready_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_sysready')
        fc.set_sensitive(widget.get_active())

    def on_rb_save_toggled(self, widget, *args):
        fc = self.xml.get_object('fc_distination')
        fc.set_sensitive(widget.get_active())

    def gtk_main_quit(self, *args):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = GSoundThemeCreator()
    app.main()
