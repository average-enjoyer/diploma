#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 6.2
#  in conjunction with Tcl version 8.6
#    Nov 11, 2021 05:20:09 PM EET  platform: Linux

import asyncio
import re
from tkinter import *
from tkinter.filedialog import askopenfilename

import pyshark

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk

    py3 = False
except ImportError:
    import tkinter.ttk as ttk

    py3 = True

import main_support

# SIPp files
caller = open("caller.xml", "w")
callee = open("callee.xml", "w")


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = Toplevel1(root)
    main_support.init(root, top)
    root.mainloop()


w = None


def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    rt = root
    root = rt
    w = tk.Toplevel(root)
    top = Toplevel1(w)
    main_support.init(w, top, *args, **kwargs)
    return (w, top)


def destroy_Toplevel1():
    global w
    w.destroy()
    w = None


def get_unique_list(list):  # BROKES THE ORDER IN THE LIST!!!!!!!!!!!!!!!!!!!!!
    list_of_unique_items = []
    unique_items = set(list)
    for i in unique_items:
        list_of_unique_items.append(i)
    return list_of_unique_items


def parse_call_ids(pcap_file):
    capture = pyshark.FileCapture(pcap_file)
    listbox_entries = []

    for packet in capture:
        try:
            if hasattr(packet, 'sip'):
                field_names = packet.sip._all_fields
                field_values = packet.sip._all_fields.values()

                for field_name, field_value in zip(field_names, field_values):
                    if field_name != '':
                        # exclude BLF packets
                        if field_name == 'sip.Request-Line' and (
                                'OPTIONS' or 'NOTIFY' or 'OPTIONS' or 'PUBLISH') not in field_value or field_name == 'sip.Status-Line':
                            str1 = packet.sip.msg_hdr.replace('  ', '\n')
                            # packet as an array
                            in_arr = str1.split("\n")
                            for item in in_arr:
                                if item[:7] == "Call-ID":
                                    listbox_entries.append(item[9:])
        except OSError:
            pass
        except asyncio.TimeoutError:
            pass

    return listbox_entries


def get_packets(
        pcap_file):  # It'll return an array with all the packets. After that there won't be any parsings of .pcap file. Only going through the array
    capture = pyshark.FileCapture(pcap_file)

    packets = []  # Full list of the SIP packets. It' filtered that the packets are unique (Resent Packet: False) and No
    # BLF or OPTIONS packets.
    caller_socket = ""
    callee_socket = ""

    for packet in capture:
        try:
            if hasattr(packet, 'sip'):
                field_names = packet.sip._all_fields
                field_values = packet.sip._all_fields.values()
                for field_name, field_value in zip(field_names, field_values):
                    if "Resent Packet: True" not in str(packet):
                        if field_name == 'sip.Request-Line' and (
                                'OPTIONS' or 'NOTIFY' or 'PUBLISH') not in field_value or field_name == 'sip.Status-Line' and "OPTIONS" not in \
                                field_names["sip.CSeq"]:
                            packets.append(packet)

        except OSError:
            pass
        except asyncio.TimeoutError:
            pass
    return packets


def cli_cld_getter(arr):
    # Finding CLI IP:PORT
    print(" PPPPP ", len(arr))
    for packet in arr:

        field_names = packet.sip._all_fields  # DICTIONARY!!!! we can take any value from there!
        field_values = packet.sip._all_fields.values()

        if "sip.Method" in field_names:
            if field_names["sip.Method"] == "INVITE" and \
                    re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b:[0-9]{1,5}', field_names["sip.Via"])[0] == \
                    re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b:[0-9]{1,5}', field_names["sip.Contact"])[0]:
                caller_socket = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b:[0-9]{1,5}', field_names["sip.Contact"])
                print("CLI", caller_socket)
                break
    # Finding CLD IP:PORT
    for packet in arr:
        field_names = packet.sip._all_fields  # DICTIONARY!!!! we can take any value from there!
        field_values = packet.sip._all_fields.values()
        if "sip.Status-Line" in field_names:
            if "200 OK" in field_names["sip.Status-Line"] and "INVITE" in field_names["sip.CSeq"]:
                callee_socket = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b:[0-9]{1,5}', field_names["sip.Contact"])
                print("CLD", callee_socket)
                print("QQQQ", packet.ip.src)
                break
    return caller_socket, callee_socket


def get_packets_by_side(packets, socket):
    side_ip = "".join(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "".join(socket[0])))

    result_list = []
    for packet in packets:
        field_names = packet.sip._all_fields  # DICTIONARY!!!! we can take any value from there!

        # check if the CLI == packet source ip
        if side_ip == packet.ip.src or side_ip == packet.ip.dst:  # "".join(cli_and_cld[0]) -- removes ['...'] coverage
            result_list.append(packet)

    return result_list


def generate(listbox, Label2):
    # temp solution for obtaining SDP
    flag = False

    pcap_file = Label2['text']
    # List with [CLI IP:PORT] and [CLD IP_PORT]
    packets = get_packets(pcap_file)  # whole list of SIP packets
    cli_and_cld = cli_cld_getter(packets)

    arr_caller = get_packets_by_side(packets, cli_and_cld[0])
    arr_callee = get_packets_by_side(packets, cli_and_cld[1])

    # TODO   check if the CLI == packet source ip. If yes we write form of SIP packet to the SIPp script for caller
    #   if no - we write the "expect" construction to the SIPp script for caller
    #   analogically for callee

    for i in listbox.curselection():
        print("Chosen Call-ID: ", listbox.get(i))

    side_ip = "".join(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "".join(cli_and_cld[0])))
    print("SIDE", side_ip)
    caller.write(
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n<!DOCTYPE scenario SYSTEM \"sipp.dtd\">\n<scenario name=\"UAC\">\n")
    for packet in arr_caller:
        field_names = packet.sip._all_fields  # DICTIONARY!!!! we can take any value from there!
        field_values = packet.sip._all_fields.values()

        if side_ip == packet.ip.src:
            caller.write("<send>\n<![CDATA[\n\n")
            packet.sip.get_field("sip.Request-Line")
            # TODO change it get by 'sip.msg_hdr' in future
            for field_name, field_value in zip(field_names, field_values):
                if field_name != '':
                    if field_name == 'sip.Request-Line' and (
                            'OPTIONS' or 'NOTIFY') not in field_value or field_name == 'sip.Status-Line':
                        caller.write(field_value + "\n")
                    if field_name == 'sip.Via' or \
                            field_name == 'sip.From' or \
                            field_name == 'sip.To' or \
                            field_name == 'sip.Call-ID' or \
                            field_name == 'sip.CSeq' or \
                            field_name == 'sip.Contact' or \
                            field_name == 'sip.Max-Forwards' or \
                            field_name == 'sip.Subject' or \
                            field_name == 'sip.mime.type' or \
                            field_name == 'sip.Content-Length' or \
                            field_name == 'sip.User-Agent':
                        # if field_name == 'sip.Call-ID':
                        #     print(field_value, "\n")
                        caller.write(field_name[4:] + ": " + field_value + "\n")

            # SDP processing (Just copying for now)
            if packet.sip.get_field("sdp_media_attr"):
                # caller.write('v=' + packet.sip.get_field("sdp.version") + '\n')
                # caller.write(packet.sip.get_field("sdp.media_attr") + '\n')
                # caller.write('m=' + packet.sip.get_field("sdp.media") + '\n')

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
            caller.write("\n]]>\n</send>\n\n")
        elif side_ip == packet.ip.dst:
            if "sip.Status-Line" in field_names:
                expected_code = "".join(re.findall(r'[0-9]{3}', field_names["sip.Status-Line"]))
                caller.write("<recv response=\"" + expected_code + "\" optional=\"true\">\n</recv>\n")
    caller.write("\n</scenario>")
    caller.close()

    # CLD processing
    side_ip = "".join(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "".join(cli_and_cld[1])))
    print("SIDE", side_ip)
    callee.write(
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\" ?>\n<!DOCTYPE scenario SYSTEM \"sipp.dtd\">\n<scenario name=\"UAC\">\n")
    for packet in arr_caller:
        field_names = packet.sip._all_fields  # DICTIONARY!!!! we can take any value from there!
        field_values = packet.sip._all_fields.values()

        if side_ip == packet.ip.src:
            callee.write("<send>\n<![CDATA[\n\n")
            packet.sip.get_field("sip.Request-Line")
            # TODO change it get by 'sip.msg_hdr' in future
            for field_name, field_value in zip(field_names, field_values):
                if field_name != '':
                    if field_name == 'sip.Request-Line' and (
                            'OPTIONS' or 'NOTIFY') not in field_value or field_name == 'sip.Status-Line':
                        callee.write(field_value + "\n")
                    if field_name == 'sip.Via' or \
                            field_name == 'sip.From' or \
                            field_name == 'sip.To' or \
                            field_name == 'sip.Call-ID' or \
                            field_name == 'sip.CSeq' or \
                            field_name == 'sip.Contact' or \
                            field_name == 'sip.Max-Forwards' or \
                            field_name == 'sip.Subject' or \
                            field_name == 'sip.mime.type' or \
                            field_name == 'sip.Content-Length' or \
                            field_name == 'sip.User-Agent':
                        # if field_name == 'sip.Call-ID':
                        #     print(field_value, "\n")
                        callee.write(field_name[4:] + ": " + field_value + "\n")

            # SDP processing (Just copying for now)
            if packet.sip.get_field("sdp_media_attr"):
                # callee.write('v=' + packet.sip.get_field("sdp.version") + '\n')
                # callee.write(packet.sip.get_field("sdp.media_attr") + '\n')
                # callee.write('m=' + packet.sip.get_field("sdp.media") + '\n')

                str1 = packet.sip.msg_hdr.replace('  ', '\n')
                # packet as an array
                in_arr = str1.split("\n")

                for item in in_arr:
                    if len(item) == 0:
                        callee.write(item)
                        if not flag:
                            callee.write("\n")
                        flag = not flag
                    elif flag:
                        callee.write(item + '\n')
            callee.write("\n]]>\n</send>\n\n")
        elif side_ip == packet.ip.dst:
            if "sip.Status-Line" in field_names:
                expected_code = "".join(re.findall(r'[0-9]{3}', field_names["sip.Status-Line"]))
                callee.write("<recv response=\"" + expected_code + "\" optional=\"true\">\n</recv>\n")

    callee.close()


class Toplevel1:

    # Makes unique values in the list

    def open_file(self):
        pcap_file = askopenfilename(defaultextension='.pcap', filetypes=[
            (".pcap", ".pcapng")])  # show an "Open" dialog box and return the path to the selected file
        # capture = pyshark.FileCapture(pcap_file)
        # the source of the packets
        self.Label2.configure(text=pcap_file)

        # List of call-ids
        listbox_entries = get_unique_list(parse_call_ids(pcap_file))
        for entry in listbox_entries:
            self.Listbox1.insert(END, entry)

    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'

        # termf = Frame(root, height=400, width=500)
        # termf.pack(fill=BOTH, expand=YES)
        # wid = termf.winfo_id()
        # os.system('xterm -into %d -geometry 40x20 -sb &' % wid)

        pcap_file = '''The file hasn't been chosen.'''
        top.geometry("610x480+645+330")
        top.minsize(1, 1)
        top.maxsize(1905, 1050)
        top.resizable(1, 1)
        top.title("SIPp generator")
        top.configure(highlightcolor="black")

        self.Button1 = tk.Button(top)
        self.Button1.place(relx=0.367, rely=0.221, height=31, width=151)
        self.Button1.configure(activebackground="#f9f9f9")
        self.Button1.configure(borderwidth="2")
        self.Button1.configure(cursor="gobbler")
        self.Button1.configure(text='''Choose a .pcap file''')
        self.Button1.configure(command=self.open_file)

        self.Label1 = tk.Label(top)
        self.Label1.place(relx=0.033, rely=0.09, height=33, width=567)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(font="-family {Tlwg Typewriter} -size 15 -weight bold")
        self.Label1.configure(text='''SIPp scripts generator''')

        self.Label2 = tk.Label(top)
        self.Label2.place(relx=0.033, rely=0.288, height=33, width=556)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(font="-family {Tlwg Typewriter} -size 12")
        self.Label2.configure(text=pcap_file)

        self.Listbox1 = tk.Listbox(top)
        self.Listbox1.place(relx=0.033, rely=0.445, relheight=0.169
                            , relwidth=0.931)
        self.Listbox1.configure(background="white")
        self.Listbox1.configure(font="-family {Tlwg Typewriter} -size 10")
        self.Listbox1.configure(selectbackground="#4603ff")
        self.Listbox1.configure(selectforeground="white")
        # self.Listbox1.configure(setgrid="1") # breaks window

        self.Button2 = tk.Button(top)
        self.Button2.place(relx=0.411, rely=0.668, height=31, width=91)
        self.Button2.configure(activebackground="#f9f9f9")
        self.Button2.configure(borderwidth="2")
        self.Button2.configure(cursor="gobbler")
        self.Button2.configure(text='''Generate''')

        self.Button2.configure(
            command=lambda: generate(self.Listbox1, self.Label2))  # lambda is important when we pass arguments

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)
        top.configure(menu=self.menubar)

        self.Label3 = tk.Label(top)
        self.Label3.place(relx=0.033, rely=0.378, height=23, width=111)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(font="-family {Tlwg Typewriter} -size 12")
        self.Label3.configure(text='''Call-IDs:''')

        self.Label4 = tk.Label(top)
        self.Label4.place(relx=0.033, rely=0.731, height=34, width=149)
        self.Label4.configure(font="-family {Tlwg Typewriter} -size 12")
        self.Label4.configure(text='''Log messages:''')

        self.Text1 = tk.Text(top)
        self.Text1.place(relx=0.033, rely=0.797, relheight=0.169, relwidth=0.931)

        self.Text1.configure(background="white")
        self.Text1.configure(font="-family {Tlwg Typewriter} -size 10")
        self.Text1.configure(selectbackground="blue")
        self.Text1.configure(selectforeground="white")
        self.Text1.configure(wrap="word")


if __name__ == '__main__':
    vp_start_gui()
