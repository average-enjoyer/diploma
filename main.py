import pyshark
import asyncio
from tkinter import *

# SIPp files
caller = open("caller.xml", "w")
callee = open("callee.xml", "w")



# global 3D-list of packet
packet_list = [[[]], [[]]]
n = 5
empty_list = [[[ [] for _ in range(n)] for _ in range(n)] for _ in range(n)]
dict = {}

# temp solution for obtaining SDP
flag = False

# packet counter
counter = 0


# like an object "window"
from tkinter.filedialog import askopenfilename

root = Tk()


def open_file():
    pcap_file = askopenfilename(defaultextension='.pcap', filetypes=[(".pcap", ".pcapng")])  # show an "Open" dialog box and return the path to the selected file
    print(pcap_file)
    # the source of the packets
    pcap_file = 'sip_only.pcapng'
    capture = pyshark.FileCapture(pcap_file)

def generating():
    # main cycle for parsing all the .pcap file
    for packet in capture:
        try:
            if hasattr(packet, 'sip'):
                field_names = packet.sip._all_fields
                field_values = packet.sip._all_fields.values()

                for field_name, field_value in zip(field_names, field_values):
                    if field_name != '':
                        if field_name == 'sip.Request-Line' and (
                                'OPTIONS' or 'NOTIFY') not in field_value or field_name == 'sip.Status-Line':
                            caller.write(field_value + "\n")
                        if field_name == 'sip.Via' or field_name == 'sip.From' or field_name == 'sip.To' or field_name == 'sip.Call-ID' or field_name == 'sip.CSeq' or field_name == 'sip.Contact' or field_name == 'sip.Max-Forwards' or field_name == 'sip.Subject' or field_name == 'sip.mime.type' or field_name == 'sip.Content-Length' or field_name == 'sip.User-Agent':
                            if field_name == 'sip.Call-ID':
                                print (field_value, "\n")
                            # dict =
                            # packet_list[counter].append(field_value)
                            # counter += 1

                            caller.write(field_name[4:] + ": " + field_value + "\n")

                # SDP processing (Just copying for now)
                if packet.sip.get_field("sdp_media_attr"):
                    caller.write('v=' + packet.sip.get_field("sdp.version") + '\n')
                    caller.write(packet.sip.get_field("sdp.media_attr") + '\n')
                    caller.write('m=' + packet.sip.get_field("sdp.media") + '\n')

                    str1 = packet.sip.msg_hdr.replace('  ', '\n')
                    # packet as an array
                    in_arr = str1.split("\n")

                    for item in in_arr:
                        if len(item) == 0:
                            caller.write(item)
                            if not flag:
                                caller.write("\n")
                            flag = not flag
                        elif flag:
                            caller.write(item + '\n')

                caller.write("\n")
        except OSError:
            pass
        except asyncio.TimeoutError:
            pass

    print(packet_list)
    caller.close()
    callee.close()


root['bg'] = '#d9ed92'
root.title('SIPp generator')
root.geometry('600x600')

img = PhotoImage(file='inventory/phone.png')
root.tk.call('wm', 'iconphoto', root._w, img)


frame_top = Frame(root, bg='#fbfbfb', bd=5)
frame_top.place(relx=0.05, rely=0.05)

# List of call-ids
listbox_entries = ["Entry 1", "Entry 2",
                   "Entry 3", "Entry 4"]
listbox_widget = Listbox(root)
for entry in listbox_entries:
    listbox_widget.insert(END, entry)
listbox_widget.place(relx=0.15, rely=0.25)


frame_bottom = Frame(root, bg='#fbfbfb', bd=5)
frame_bottom.place(relx=0.05, rely=0.55)

btn = Button(frame_top, text='Choose a .pcap file', command=open_file)
btn.pack()

info = Label(frame_bottom, text='Choose the Call-ID and press Generate', bg='#ffb700', font=40)
info.pack()
# frm = ttk.Frame(root, padding=10)
# frm.grid()
# ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()

