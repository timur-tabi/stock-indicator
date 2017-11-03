#!/usr/bin/env python

# Gnome Unity stock price appindicator
#
# This appindicator displays the price of a single stock in the Notification
# area.
#
# Copyright 2013, Timur Tabi
#
# Based on the Gmail appindicator from
# http://conjurecode.com/create-indicator-applet-for-ubuntu-unity-with-python/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# This software is provided by the copyright holders and contributors "as is"
# and any express or implied warranties, including, but not limited to, the
# implied warranties of merchantability and fitness for a particular purpose
# are disclaimed. In no event shall the copyright holder or contributors be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of
# the possibility of such damage.

import sys
import os
import gtk
import urllib2
import appindicator
import json

import Image
import ImageDraw
import ImageFont
import tempfile

import imaplib
import re

PING_FREQUENCY = 1 # minutes

class CheckStock:
    symbol = 'QCOM'

    def __init__(self):
        font = ImageFont.truetype('/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-C.ttf', size=64)
        image = Image.new('RGBA', font.getsize(self.symbol))
        draw = ImageDraw.Draw(image)
        # I don't know why, but we need to specify -10 to make sure it's
        # vertically centered.
        draw.text((0, -10), self.symbol, font=font)
        image.save('/tmp/stock.png')

        self.ind = appindicator.Indicator('new-stock-indicator',
                                           '/tmp/stock.png',
                                           appindicator.CATEGORY_OTHER)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.refresh_item = gtk.MenuItem('Refresh')
        self.refresh_item.connect('activate', self.refresh)
        self.refresh_item.show()
        self.menu.append(self.refresh_item)

        self.reload_item = gtk.MenuItem('Reload')
        self.reload_item.connect('activate', self.reload)
        self.reload_item.show()
        self.menu.append(self.reload_item)

        self.quit_item = gtk.MenuItem('Quit')
        self.quit_item.connect('activate', self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.update_stock_price()
        gtk.timeout_add(PING_FREQUENCY * 60000, self.update_stock_price)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def refresh(self, widget):
        self.update_stock_price()

    def reload(self, widget):
        # If this script was updated, just reload it instead of forcing the
        # user to quit first.
        os.execl(sys.executable, *([sys.executable]+sys.argv))

    def update_stock_price(self):
        try:
            url = urllib2.urlopen('https://finance.google.com/finance?q=%s&output=json' % self.symbol)
            response = url.read()
            # Google apparently adds 5 bytes at the beginning and 2 bytes at the
            # end of the JSON that should be ignored.
            j = json.loads(response[5:len(response) - 2])
            price = float(j['l'])
            open = float(j['op'])

            if price > open:
                # Price has gone up
                self.ind.set_label(u'%0.2f\u25B3' % price)
            elif price < open:
                # Price has gone down
                self.ind.set_label(u'%0.2f\u25BD' % price)
            else:
                self.ind.set_label('%0.2f' % price)
        except:
            self.ind.set_label('?')

        return True

if __name__ == '__main__':
    indicator = CheckStock()
    indicator.main()
