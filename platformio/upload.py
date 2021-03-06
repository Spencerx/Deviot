#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from ..libraries.tools import get_setting, save_setting, save_sysetting
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n


class Upload(Initialize):
    def __init__(self):
        super(Upload, self).__init__()

        self.nonblock_upload()

    def start_upload(self):
        """Upload

        Run the upload platformio command checking if a board (environment)
        and a serial port is selected
        """
        if(not self.check_main_requirements()):
            exit(0)

        save_sysetting('last_action', self.UPLOAD)

        # check board selected or make select it
        self.check_board_selected()
        if(not self.board_id):
            self.print("select_board_list")
            return

        # check port selected or make select it
        self.check_port_selected()
        if(not self.port_id):
            self.print("select_port_list")
            return

        port_id = self.port_id

        # initialize board if it's not
        self.add_board()

        # add extra library board
        self.add_option('lib_extra_dirs', append=True)

        # check if there is a new speed to overwrite
        self.add_option('upload_speed')

        # loads data from platformio.ini
        self.read_pio_preferences()

        # check if there is a programmer selected
        self.programmer()

        programmer = get_setting('programmer_id', None)
        if(programmer):
            cmd = ['run', '-t', 'program', '-e', self.board_id]
        else:
            cmd = ['run', '-t', 'upload', '-e', self.board_id]
            if(port_id != 'not'):
                cmd.extend(['--upload-port', port_id])

        if(not self.check_auth_ota()):
            self.print("ota_error_platform")
            save_sysetting('last_action', None)
            return

        self.check_serial_monitor()

        # add src_dir flag if it's neccesary
        self.override_src()

        self.run_command(cmd)

        self.after_complete()

        if(get_setting('run_monitor', None)):
            from ..libraries.serial import toggle_serial_monitor
            toggle_serial_monitor(port_id)
        save_setting('run_monitor', None)

    def nonblock_upload(self):
        """New Thread Execution

        Starts a new thread to run the start_upload method
        """
        from threading import Thread
        translate = I18n().translate

        thread = Thread(target=self.start_upload)
        thread.start()
        ThreadProgress(thread, translate('processing'), '')
