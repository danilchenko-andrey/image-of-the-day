#!/usr/bin/env python


import argparse
import appscript
import requests
import logging
import os
import shutil
from datetime import datetime

from appscript import *

from AppKit import NSWorkspace, NSScreen
from Foundation import NSURL

def change_desktop_background(file):
    file_url = NSURL.fileURLWithPath_(file)
    ws = NSWorkspace.sharedWorkspace()
    for screen in NSScreen.screens():
        (result, error) = ws.setDesktopImageURL_forScreen_options_error_(file_url, screen, {}, None)

class ImageWorker(object):
    def __init__(self, url, storage_dir_name, date_format, reload):
        self.url = url
        self.storage_dir_name = storage_dir_name
        self.logger = logging.getLogger('ImageWorker')
        self.date_format = date_format
        self.reload = reload

    def download_picture(self, output_filename):
        response = requests.get(self.url, stream=True)
        if response.status_code != 200:
            self.logger.error('Failed to download picture: got status code %d' %
                               response.status_code)
            exit(1)
        with open(output_filename, 'wb') as output_file:
            shutil.copyfileobj(response.raw, output_file)

    def prepare_output(self):
        day = datetime.now().strftime(self.date_format)
        output_filename = os.path.join(self.storage_dir_name, '%s.png' % day)
        if not self.reload and os.path.exists(output_filename):
            self.logger.info('File exists!')
            exit(0)
        return output_filename

    def set_background_image(self, image_filename):
        se = app('System Events')
        desktops = se.desktops.display_name.get()
        for i, d in enumerate(desktops):
            self.logger.debug('Change background for %s (id=%d)' % (d, i))
        change_desktop_background(image_filename)

    def run(self):
        output_filename = self.prepare_output()
        self.download_picture(output_filename)
        self.set_background_image(output_filename)
        self.logger.info('Done!')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Url of daily image')
    parser.add_argument('storage', help='Directory to store files')
    parser.add_argument('--date-format', help='Date format', default='%Y-%m-%d')
    parser.add_argument('-r', help='Reload', action='store_true', default=False)
    args = parser.parse_args()

    worker = ImageWorker(args.url, args.storage, args.date_format, args.r)
    worker.run()


