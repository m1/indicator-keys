#Caps
from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq
from threading import Thread
import threading
#app
try:
    from gi.repository import AppIndicator3 as AppIndicator
except:
    from gi.repository import AppIndicator

from gi.repository import Gtk, GLib, Notify
import commands
import sys
import conf
import Image
import os



class IndicatorKeys(Thread):
    def run(self):
        self.running = True
        Notify.init('indicator-keys')
        self.n = Notify.Notification.new("hello", 'Message', 'dialog-information')
        print threading.current_thread()
        self.on = Image.open("on.png")
        self.off = Image.open("off.png")
        self.app_first_run()
        self.menu = Gtk.Menu()

        item = Gtk.MenuItem()
        item.set_label("Config")
        item.connect("activate",self.config)
        item.show()
        self.menu.append(item)

        item = Gtk.MenuItem()
        item.set_label("Exit")
        item.connect("activate",self.app_exit)
        item.show()
        self.menu.append(item)

        self.menu.show()
        self.ik.set_menu(self.menu)
        print "dix"
        self.main()

    def app_first_run(self):
        self.status = int(commands.getoutput("xset q | grep LED")[65])
        if conf.show_caps and conf.show_num:
            #default nothing on
            self.caps_on = False
            self.num_on = False
            self.scroll_on = False

            if self.status == 1: #caps
                self.caps_on = True
            elif self.status == 2: #num
                self.num_on = True
            elif self.status == 3: #num & caps
                self.caps_on = True
                self.num_on = True
            elif self.status == 4: #scroll
                self.scroll_on = True
            elif self.status == 5: #caps & scroll
                self.caps_on = True
                self.scroll_on = True
            elif self.status == 6: #num & scroll
                self.num_on = True
                self.scroll_on = True
            elif self.status == 7: #all
                self.caps_on = True
                self.num_on = True
                self.scroll_on = True

            self.ik = AppIndicator.Indicator.new(
            "indicator-keys",
            "indicatorkeys",
            AppIndicator.IndicatorCategory.HARDWARE)
        self.ik.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.run = 0;
        self.makeImg()
    def config(self,evt):
        os.system("gedit conf.py")
    def makeImg(self):
        print "caps: ",self.caps_on
        print "num: ",self.num_on
        print "scroll: ", self.scroll_on

        fin = Image.new("RGBA",(62,22))
        if conf.show_caps and conf.show_num and conf.show_scroll:
            if self.caps_on:
                fin.paste(self.on,(0,0))
            else:
                fin.paste(self.off,(0,0))

            if self.num_on:
                fin.paste(self.on,(20,0))
            else:
                fin.paste(self.off,(20,0))

            if self.scroll_on:
                fin.paste(self.on,(40,0))
            else:
                fin.paste(self.off,(40,0))

        if self.run == 0:
            fin.save("/usr/share/icons/Faenza/actions/22/indicatorkeys2.png")
            self.ik.set_icon("indicatorkeys2")
        else:
            fin.save("/usr/share/icons/Faenza/actions/22/indicatorkeys.png")
            self.ik.set_icon("indicatorkeys")
        if self.run == 0:
            self.run = 1
        else:
            self.run = 0


    def app_exit(self,evt):
        self.running = False
        Gtk.main_quit()
        sys.exit(1)

    def caps_update(self):
        if self.caps_on:
            self.caps_on = False
            stri = "Caps lock Off"
            img = "milesoff"
        else:
            self.caps_on = True
            stri = "Caps lock On"
            img = "mileson"

        self.n.update(stri, None, img)
        self.n.show();
        self.makeImg()
    def num_update(self):
        if self.num_on:
            self.num_on = False
            stri = "Num lock Off"
            img = "milesoff"
        else:
            self.num_on = True
            stri = "Num lock On"
            img = "mileson"

        self.n.update(stri, None, img)
        self.n.show();
        self.makeImg()
    def scroll_update(self):
        if self.scroll_on:
            self.scroll_on = False
            os.system("xset -led named 'Scroll Lock'")
            stri = "Scroll lock Off"
            img = "milesoff"
        else:
            self.scroll_on = True
            os.system("xset led named 'Scroll Lock'")
            stri = "Scroll lock On"
            img = "mileson"
        self.n.update(stri, None, img)
        self.n.show();
        self.makeImg()
    def main(self):
        Gtk.main()



class caps(Thread):
    def __init__(self, aa):
        print threading.current_thread()
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        self.aa = aa

        if not self.record_dpy.has_extension("RECORD"):
            print "RECORD extension not found"
            sys.exit(1)
        self.r = self.record_dpy.record_get_version(0, 0)
        self.ctx = self.record_dpy.record_create_context(
                0,
                [record.AllClients],
                [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress,X.KeyPress),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
                }])
        self.record_dpy.record_enable_context(self.ctx, self.record_callback)
        self.record_dpy.record_free_context(self.ctx)

    def record_callback(self,reply):
        self.reply = reply
        if not len(self.reply.data) or ord(self.reply.data[0]) < 2:
            return
        self.data = self.reply.data
        while len(self.data):
            self.event, self.data = rq.EventField(None).parse_binary_value(self.data, self.record_dpy.display, None, None)
            if self.event.type in [X.KeyPress, X.KeyRelease]: 
                if self.event.type in [X.KeyPress, X.KeyRelease]:
                    self.pr = self.event.type == X.KeyPress and "Press" or "Release"
                    self.keysym = self.local_dpy.keycode_to_keysym(self.event.detail, 0)
                    if self.lookup_keysym(self.keysym) == "Caps_Lock":
                        self.aa.caps_update()
                    if self.lookup_keysym(self.keysym) == "Num_Lock":
                        self.aa.num_update()
                    if self.lookup_keysym(self.keysym) == "Scroll_Lock":
                        self.aa.scroll_update()

    def lookup_keysym(self,keysym):
        for name in dir(XK):
            if name[:3] == "XK_" and getattr(XK, name) == self.keysym:
                return name[3:]
        return "[%d]" % self.keysym

if __name__ == "__main__":
    GLib.threads_init()
    ik = IndicatorKeys()
    ik.start()
    caps(ik)


