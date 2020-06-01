# Author: Miguel Martinez Lopez
# http://code.activestate.com/recipes/580757-chatbox-megawidget-for-tkinter/

import datetime
import collections

from tkinter import StringVar, Text, Frame, PanedWindow, Scrollbar, Label
from tkinter.constants import *
import tkinter.ttk as ttk

class Chatbox(object):
    def __init__(self, master, scrollbar_background=None, scrollbar_troughcolor=None, history_background=None, history_font=None, history_padx=None, history_pady=None, label_template=u"{nick}", tags=None):
        self.interior = Frame(master, class_="Chatbox")

        self._is_empty = True
        self._label_template = label_template
        
        top_frame = Frame(self.interior, class_="Top")
        top_frame.pack(expand=True, fill=BOTH)
                
        self._textarea = Text(top_frame, state=DISABLED, spacing1=1)

        self._vsb = Scrollbar(top_frame, takefocus=0, command=self._textarea.yview)
        self._vsb.pack(side=RIGHT, fill=Y)

        self._textarea.pack(side=RIGHT, expand=YES, fill=BOTH)
        self._textarea["yscrollcommand"]=self._vsb.set

        if history_background:
            self._textarea.configure(background=history_background)
        if history_font:
            self._textarea.configure(font=history_font)
        if history_padx:
             self._textarea.configure(padx=history_padx)
        if history_pady:
            self._textarea.configure(pady=history_pady)
        if scrollbar_background:
            self._vsb.configure(background = scrollbar_background)
        if scrollbar_troughcolor:
            self._vsb.configure(troughcolor = scrollbar_troughcolor)
        if tags:
            for tag, tag_config in tags.items():
                self._textarea.tag_config(tag, **tag_config)
        
    def bind_textarea(self, event, handler):
        self._textarea.bind(event, handler)
        
    def bind_tag(self, tagName, sequence, func, add=None):
        self._textarea.tag_bind(tagName, sequence, func, add=add) 

    def user_message(self, nick, content, tag):
        self._write((u"%s:"%nick, "nick"), " ", (content, tag))

    def tag(self, tag_name, **kwargs):
        self._textarea.tag_config(tag_name, **kwargs)

    def clear(self):
        self._is_empty = True
        self._textarea.config(state=NORMAL)
        self._textarea.delete('1.0', END)
        self._textarea.config(state=DISABLED)

    def _filter_text(self, text):
        return "".join(ch for ch in text if ch <= u"\uFFFF")
    
    def _write(self, *args):
        if len(args) == 0: return
            
        relative_position_of_scrollbar = self._vsb.get()[1]
        
        self._textarea.config(state=NORMAL)
        
        if self._is_empty:
            self._is_empty = False
        else:
            self._textarea.insert(END, "\n")

        for arg in args:
            if isinstance(arg, tuple):
                text, tag = arg
                        # Parsing not allowed characters
                text = self._filter_text(text)
                self._textarea.insert(END, text, tag)
            else:
                text = arg

                text = self._filter_text(text)
                self._textarea.insert(END, text)

        self._textarea.config(state=DISABLED)
        
        if relative_position_of_scrollbar == 1:
            self._textarea.yview_moveto(1)