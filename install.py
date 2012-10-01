import os
import shutil

global order
order = [0,0,0]
# yon = yes or no
def check_input(yesorno):
	global order
	u_in = None
	valid = False
	while not valid:
		u_in = str(raw_input()).lower()
		# yes or no question
		if yesorno:
			if u_in not in accepted:
				print "Sorry your input wasn't recognised, enter yes or no"
			else:
				valid = True
		# key lock question
		else:
			if u_in not in c_accepted:
				print "Sorry your input wasn't recognised, enter caps, num or scroll"
			elif u_in in order:
				print "Sorry you have already entered", u_in
			else:
				valid = True
	if yesorno:
		if u_in in a_yes:
			return True
		elif u_in in a_no:
			return False
	else:
		return u_in

def create_default_config():
	o_file = open('conf1.py', 'w+')
	o_file.write("debug = False" +
				 "\nshow_notify = True" +
				 "\nshow_notification_icon = True" +
				 "\nshow_caps = True" +
				 "\nshow_num = True" +
				 "\nshow_scroll = True" +
				 "\norder = ('caps', 'scroll', 'num')"
		)

accepted = ["yes", "y", "n", "no"]
c_accepted = ["caps", "scroll", "num"]
a_yes = [accepted[0],accepted[1]]
a_no = [accepted[2],accepted[3]]

print "-"*40
print "Installation for Indicator-keys"
print "-"*40

print "Do you want to create a config?"
create_config = check_input(1)

if create_config:
	print "\nCreating custom config:"
	print "-"*20

	happy = False
	while not happy:
		print "Do you want to show notifications?"
		show_notify = check_input(1)
		if show_notify:
			print "Do you want these notifications to display icons?"
			show_notification_icon = check_input(1)
		else:
			show_notification_icon = False
		print "Do you want the indicator to detect caps lock?"
		show_caps = check_input(1)
		print "How about num lock?"
		show_num = check_input(1)
		print "And finally scroll lock?"
		show_scroll = check_input(1)
		print "And in which order do you want to display these on the indicator?"
		print "First:"
		order[0] = check_input(0)
		print "Second:"
		order[1] = check_input(0)
		print "Third:"
		order[2] = check_input(0)

		print "Are you happy with this config:"
		print "-"*20
		print "show_notify =", show_notify
		print "show_notification_icon =", show_notification_icon
		print "show_caps =", show_caps
		print "show_num =", show_num
		print "show_scroll =", show_scroll
		print "order =", order
		print "-"*20


		happy = check_input(1)
	o_file = open('conf1.py', 'w+')
	o_file.write("show_notify = " + str(show_notify) + 
			"\nshow_notification_icon = "+ str(show_notification_icon) + 
			"\nshow_caps = "+ str(show_caps) +
			"\nshow_num = "+ str(show_num) +
			"\nshow_scroll = "+ str(show_scroll) +
			"\norder ="+ str(order))

else:
	print "Using default config"
	create_default_config()

print "\nInstalling icons"
dest = "/usr/share/icons/hicolor/22x22/apps"
files_to_copy = ["img/indicator-keys-main.png","img/indicator-keys-main2.png","img/indicator-keys-off.svg","img/indicator-keys-on.svg"]
for i in files_to_copy:
	try:
		shutil.copy(i, dest)
		print "Copied file", i, "to", dest
	except IOError:
		print "Error copying" + i
print "Updating icon cache"
os.system("gtk-update-icon-cache /usr/share/icons/hicolor/")