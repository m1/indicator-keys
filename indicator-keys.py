# indicator
import conf  # config file

import sys  # sys.exit
import commands  # get output of xset grep
import Image
import os  # gedit conf
try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator
from gi.repository import Gtk, GLib

# detect
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from threading import Thread


class indicator(Thread):
    def run(self):
        # workaround for refreshing indicator
        self.run = 0
        if conf.show_notify:
            from gi.repository import Notify
            Notify.init("indicator-keys")
            # blank notification so can update later
            self.notify = Notify.Notification.new("", "", " ")
            self.notify_icn_on = ("indicator-keys-on")
            self.notify_icn_off = ("indicator-keys-off")

        self.img_on = Image.open("indicator-keys-on-icon.png")
        self.img_off = Image.open("indicator-keys-off-icon.png")

        self.first_run()
        self.make_menu()
        self.main()

    def first_run(self):
        # see if locks are on
        self.status = int(commands.getoutput("xset q | grep LED")[65])

        # create dict of what to show
        self.show_keys = {'caps': conf.show_caps,
                          'num': conf.show_num,
                          'scroll': conf.show_scroll}

        # count Trues from show_keys
        self.ind_length = list(self.show_keys.values()).count(True)

        # the  status' in which the corresponding keys are toggled on
        list_keys_on = {'caps': [1, 3, 5, 7],
                        'num': [2, 3, 6, 7],
                        'scroll': [4, 5, 6, 7]}

        # if status = list_key_on then make true
        self.k_on = {x: self.status in list_keys_on[x] for x in list_keys_on}

        #make temp icon
        self.ik = AppIndicator.Indicator.new("indicator-keys",
                                             "indicatorkeys",
                                             AppIndicator.IndicatorCategory.HARDWARE)
        self.ik.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.make_img()

    def make_img(self):
        # sizes of indicator depending on items
        ind_sizes = [22, 42, 62]

        # positions of key images
        ind_positions = [0, 20, 40]

        # make new image depending on indicator size defined in ind_length
        self.ind_image = Image.new("RGBA", (ind_sizes[self.ind_length - 1], 22))

        # defines positions in order defined in conf.py
        # todo: just be able to define as order = {1, 2, 3} rather than seperate show_caps = etc
        pos = 0
        self.key_positions = {}

        if self.show_keys[conf.order[0]]:
            self.key_positions[conf.order[0]] = ind_positions[pos]
            pos += 1

        if self.show_keys[conf.order[1]]:
            self.key_positions[conf.order[1]] = ind_positions[pos]
            pos += 1

        if self.show_keys[conf.order[2]]:
            self.key_positions[conf.order[2]] = ind_positions[pos]

        self.update("all_keys")

    def update(self, obj):
        # if obj called isn't all_keys and it's meant to be shown
        if obj != "all_keys" and obj in self.key_positions:
            if self.k_on[obj]:
                img = self.img_on
            else:
                img = self.img_off
            if self.updating_all is 0 and conf.show_notify:
                self.update_notify(obj)
            self.k_on[obj] = not self.k_on[obj]
            self.ind_image.paste(img, (self.key_positions[obj], 0))

            # workaround for refresh
            if self.run == 0:
                self.ind_image.save("/usr/share/icons/Faenza/actions/22/indicatorkeys2.png")
                self.ik.set_icon("indicatorkeys2")
                self.run = 1
            else:
                self.ind_image.save("/usr/share/icons/Faenza/actions/22/indicatorkeys.png")
                self.ik.set_icon("indicatorkeys")
                self.run = 0


        elif obj == "all_keys":  # all
            # updating_all equals > 0 when updating all
            self.updating_all = self.ind_length

            if "caps" in self.key_positions:
                self.update("caps")
                self.updating_all -= 1

            if "num" in self.key_positions:
                self.update("num")
                self.updating_all -= 1

            if "scroll" in self.key_positions:
                self.update("scroll")
                self.updating_all -= 1

    def update_notify(self, obj):
        n_str_on = " lock on"
        n_str_off = " lock off"

        if obj == "caps":
                n_key = "Caps"
        elif obj == "num":
                n_key = "Num"
        elif obj == "scroll":
                n_key = "Scroll"

        if self.k_on[obj]:
            if conf.show_notify:
                n_icn = self.notify_icn_on
            n_str = n_key + n_str_on
        else:
            if conf.show_notify:
                n_icn = self.notify_icn_off
            n_str = n_key + n_str_off

        if not conf.show_notify:
            n_icn = None

        self.notify.update(n_str, None, n_icn)
        self.notify.show()

    def make_menu(self):
        self.menu = Gtk.Menu()
        self.make_menu_item("Config")
        self.make_menu_item("Exit")
        self.menu.show()
        self.ik.set_menu(self.menu)

    def make_menu_item(self, item_name):
        item = Gtk.MenuItem()
        item.set_label(item_name)

        if item_name == "Config":
            item.connect("activate", self.edit_config)
        elif item_name == "Exit":
            item.connect("activate", self.ik_exit)

        item.show()
        self.menu.append(item)

    def edit_config(self, evt):
        # todo: gui elements
        os.system("gedit conf.py")

    def ik_exit(self, evt):
        Gtk.main_quit()
        sys.exit(1)

    def main(self):
        Gtk.main()


class detect(Thread):
    def __init__(self, app):
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        self.app = app

        # create context
        self.ctx = self.record_dpy.record_create_context(
            0,
            [record.AllClients],
            [{
                'core_requests': (0, 0),
                'core_replies': (0, 0),
                'ext_requests': (0, 0, 0, 0),
                'ext_replies': (0, 0, 0, 0),
                'delivered_events': (0, 0),
                'device_events': (X.KeyPress, X.KeyPress),
                'errors': (0, 0),
                'client_started': False,
                'client_died': False,
            }])
        self.record_dpy.record_enable_context(self.ctx, self.get_events)
        self.record_dpy.record_free_context(self.ctx)

    def get_events(self, reply):
        if not len(reply.data) or ord(reply.data[0]) < 2:
            return
        data = reply.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data,
                                                self.record_dpy.display,
                                                None, None)
            if event.type in [X.KeyPress, X.KeyRelease]:
                key_pressed = self.local_dpy.keycode_to_keysym(event.detail, 0)
                if self.key_lookup(key_pressed) == "Caps_Lock":
                    self.app.update("caps")
                if self.key_lookup(key_pressed) == "Num_Lock":
                    self.app.update("num")
                if self.key_lookup(key_pressed) == "Scroll_Lock":
                    self.app.update("scroll")

    def key_lookup(self, key_pressed):
        for name in dir(XK):
            if name[:3] == "XK_" and getattr(XK, name) == key_pressed:
                return name[3:]
        return "[%d]" % key_pressed

if __name__ == "__main__":
    GLib.threads_init()
    ik = indicator()
    ik.start()
    detect(ik)
