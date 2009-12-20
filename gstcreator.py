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

EXTRA_EVENT_SOUNDS = (('Press a button', 'button-pressed'),
('Activate a check button', 'button-toggle-on'),
('Deactivate a check button', 'button-toggle-off'),
('Click a menu', 'menu-click'),
('Change a tab', 'notebook-tab-changed'),
None,
('Empty Trash', 'trash-empty'),
None,
('Recieve a new instant message', 'message-new-instant'),
None,
('Open a new window', 'window-new'),
('Close a window', 'window-close'))

class GSoundThemeCreator:

    flocation = None
    extras = {}

    def __init__(self):
        """Initializer"""

        uifile = UI_PATH
        self.xml = gtk.Builder()
        self.xml.add_from_file(uifile)
        self.xml.connect_signals(self)

        # set radio buttion
        self.xml.get_object('rb_install').set_active(True)

        # filters
        self.oggfilter = gtk.FileFilter()
        self.oggfilter.set_name('Ogg/WAV files')
        self.oggfilter.add_pattern('*.oga')
        self.oggfilter.add_pattern('*.ogg')
        self.oggfilter.add_pattern('*.wav')
        self.allfilter = gtk.FileFilter()
        self.allfilter.set_name('All files')
        self.allfilter.add_pattern('*')
        for fc in ['fc_login', 'fc_logout', 'fc_error', 'fc_warning', 'fc_information', 'fc_question', 'fc_sysready']:
            obj = self.xml.get_object(fc)
            obj.add_filter(self.oggfilter)
            obj.add_filter(self.allfilter)

        # Other event sounds
        self.vb_others = self.xml.get_object('vb_other_events')
        self.cmb_events = self.xml.get_object('cmb_events')
        func = lambda model, iter, data=None :  model.get_value(iter, 0) == ''
        self.cmb_events.set_row_separator_func(func)
        self.btn_add_events = self.xml.get_object('btn_add_another_event')
        self.list_events = self.cmb_events.get_model()
        for i in EXTRA_EVENT_SOUNDS:
            if i is None:
                self.list_events.append(('', True, ''))
            else:
                self.list_events.append((i[0], True, i[1]))
        self.cmb_events.set_active(0)

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
            needsu = True
            target = SOUND_DIR
        else:
            dist = self.xml.get_object('fc_distination').get_filename() or '~/'
            target = dist
        command += ' --target='+target


        # --Overwrite? (Only in direct install) -------
        themedir = os.path.join(target, title)
        if needsu and os.path.exists(themedir):
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_YES_NO)
            dialog.set_transient_for(self.window)
            dialog.set_markup('There is the same title theme already.\nDo you overwrite it? (The theme overwritten cannot restore.)')
            answer = dialog.run()
            dialog.destroy()
            if answer == gtk.RESPONSE_YES:
                import commands # TODO not so beautiful code :)
                status, output = commands.getstatusoutput('gksu -D "Sound Theme Creator" "rm -r %s"' % themedir)
                if status:
                    dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
                    dialog.set_transient_for(self.window)
                    dialog.set_markup('Error while removing the old theme...')
                    dialog.run()
                    dialog.destroy()
                    return
            else:
                return


        # --Sound files--------------------------
        if self.xml.get_object('cb_login').get_active():
            login = self.xml.get_object('fc_login').get_filename()
            if login:
                command += ' --login '+self.escapesh(login)
        if self.xml.get_object('cb_logout').get_active():
            logout = self.xml.get_object('fc_logout').get_filename()
            if logout:
                command += ' --logout '+self.escapesh(logout)
        if self.xml.get_object('cb_error').get_active():
            error = self.xml.get_object('fc_error').get_filename()
            if error:
                command += ' --error '+self.escapesh(error)
        if self.xml.get_object('cb_warning').get_active():
            warning = self.xml.get_object('fc_warning').get_filename()
            if warning:
                command += ' --warning '+self.escapesh(warning)
        if self.xml.get_object('cb_information').get_active():
            information = self.xml.get_object('fc_information').get_filename()
            if information:
                command += ' --information '+self.escapesh(information)
        if self.xml.get_object('cb_question').get_active():
            question = self.xml.get_object('fc_question').get_filename()
            if question:
                command += ' --question '+self.escapesh(question)
        if self.xml.get_object('cb_sysready').get_active():
            sysready = self.xml.get_object('fc_sysready').get_filename()
            if sysready:
                command += ' --sysready '+self.escapesh(sysready)


        # --Extra events---------------------
        for spec, fcb in self.extras.items():
            sound = fcb.get_filename()
            if sound:
                command += ' %s %s' % (spec, self.escapesh(sound))

        # --Execute--------------------------
        import commands
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

    def escapesh(self, value):
        value = value.replace(' ', '\\ ')
        value = value.replace('"', '\\"')
        value = value.replace('$', '\\$')
        value = value.replace('`', '\\`')
        value = value.replace('\\', '\\\\')
        return value

    def on_fc_file_set(self, widget, *args):
        self.flocation = widget.get_current_folder()
        for fc in ['fc_login', 'fc_logout', 'fc_error', 'fc_warning', 'fc_information', 'fc_question', 'fc_sysready']:
            obj = self.xml.get_object(fc)
            obj.get_filename() or obj.set_current_folder(self.flocation)
        for obj in self.extras.values():
            obj.get_filename() or obj.set_current_folder(self.flocation)

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

    def on_btn_add_another_event_clicked(self, widget, *args):

        # Selection in combobox
        current_iter = self.cmb_events.get_active_iter()
        value = self.list_events.get_value(current_iter, 0)
        spec = self.list_events.get_value(current_iter, 2)
        if not self.list_events.get_value(current_iter, 1):
            return


        # |--------------------------|----------|--------|
        # | label                    | fcbutton | remove |
        # |--------------------------|----------|--------|
        hb = gtk.HBox(spacing=6)

        # CheckButton
        lb = gtk.Label()
        lb.set_alignment(0, 0.5)
        lb.set_label('%s :' % value)

        # FileChooserButton
        fb = gtk.FileChooserButton(title='')
        fb.add_filter(self.oggfilter)
        fb.add_filter(self.allfilter)
        fb.connect('file-set', self.on_fc_file_set)
        if self.flocation:
            fb.set_current_folder(self.flocation)

        # Button
        bt = gtk.Button(stock=gtk.STOCK_REMOVE)
        bt.connect('clicked', self.on_btn_remove_clicked, hb, current_iter, spec)
        
        hb.pack_start(lb, expand=True)
        hb.pack_start(fb, expand=True)
        hb.pack_start(bt, expand=False)

        self.vb_others.pack_start(hb)
        self.vb_others.show_all()

        # add to dic
        self.extras[spec] = fb

        # get back focus TODO it doesnt work
        self.btn_add_events.grab_focus()

        # Mark as already selected
        self.list_events.set(current_iter, 1, False)

    def on_btn_remove_clicked(self, widget, hbox, event_iter, key, *args):
        self.vb_others.remove(hbox)
        self.list_events.set(event_iter, 1, True)

        # remove from dic
        del self.extras[key]

    def gtk_main_quit(self, *args):
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    app = GSoundThemeCreator()
    app.main()
