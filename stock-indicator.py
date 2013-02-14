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
import urllib
import urllib2
import appindicator

import imaplib
import re

PING_FREQUENCY = 1 # minutes

def wget(url):
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    except:
        return None

class CheckStock:
    symbol = 'FSL'

    def __init__(self):
        self.ind = appindicator.Indicator('new-stock-indicator',
                                           '',
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
            data = wget('http://finance.yahoo.com/d/quotes.csv?s=%s&f=l1o' % self.symbol).strip().split(',')
            # Before the market opens, the Opening Price is "N/A"
            if data[1] == 'N/A':
                price = open = float(data[0])
            else:
                (price, open) = map(float, data)

            if price > open:
                self.ind.set_label(u'%s %0.2f \u2191' % (self.symbol, price))
            elif price < open:
                self.ind.set_label(u'%s %0.2f \u2193' % (self.symbol, price))
            else:
                self.ind.set_label('%s %0.2f' % (self.symbol, price))
        except:
            self.ind.set_label('%s ?' % self.symbol)

        return True

if __name__ == '__main__':
    indicator = CheckStock()
    indicator.main()
