# sources :
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# Chatbox :
# http://code.activestate.com/recipes/580757-chatbox-megawidget-for-tkinter/
#

from tkinter import font, messagebox
import tkinter
import tkinter.ttk as tk
from Chatbox import Chatbox
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time

class Gameplay():
    def __init__(self):
        self.es = Elasticsearch(hosts=["https://70fa05be281c4ff8977b2a9e557f7690.westeurope.azure.elastic-cloud.com:9243/"],
                   http_auth=("elastic", "dpucymmIkDh7iOMjbUFFaRqA"))
        self.a = helpers.scan(self.es, query={"query": {"match_all": {}}}, scroll='1m', index='zoo_v4')  # like others so far
        self.names = [aa['_source']['name'] for aa in self.a]

        self.root = tkinter.Tk()
        self.root.title("Animal Guesser")
        self.root.geometry('450x550')

        # Define game variables
        self.game_running = False
        self.steps = 0

        # Define styling
        self.s = tk.Style()
        self.s.configure("exit.TButton", font=('Arial', '18', 'bold'))
        self.s.configure("start.TButton", font=('Arial', '18', 'bold'))
        self.s.map('exit.TButton', foreground=[('pressed', 'dark red'), ('active', 'red')],
              background=[('pressed', 'red'), ('active', 'red')])
        self.s.map('start.TButton', foreground=[('pressed', 'dark green'), ('active', 'green')],
              background=[('pressed', 'green'), ('active', 'green')])

        self.s.configure("G.TLabel", font=('Arial', '20', 'bold'), foreground='green')
        self.s.configure("G.Sub.TLabel", font=('Arial', '15', 'bold'), foreground='dark green')
        self.s.configure("G.Desc.TLabel", font=('Helvetica', '13'))
        self.s.configure('TFrame', background='white')
        self.s.configure('TLabel', background='white')

        self.home_menu = tk.Frame(self.root)
        self.home_menu.pack(fill=tkinter.BOTH, expand=1)
        self.game_frame = tk.Frame(self.root)
        self.selection_frame = tk.Frame(self.root)

        # building home menu (FRAME)
        tk.Label(self.home_menu, text='Animal Guesser', style='G.TLabel').pack(pady=(30, 0))
        tk.Label(self.home_menu, text='A game based on the Taboo board game..', style='G.Sub.TLabel').pack(pady=(5, 50))
        tk.Label(self.home_menu, text='The objective of this game is to describe an animal.', style='G.Desc.TLabel').pack(
            pady=(20, 5))
        tk.Label(self.home_menu, text='After every single description the AI will make a guess.',
                 style='G.Desc.TLabel').pack(
            pady=(0, 5))
        tk.Label(self.home_menu, text='If the guess is correct you can answer with "Yes",', style='G.Desc.TLabel').pack(
            pady=(0, 5))
        tk.Label(self.home_menu, text='if the guess is wrong you must answer with "No"', style='G.Desc.TLabel').pack(
            pady=(0, 5))
        tk.Label(self.home_menu, text='and provide a following description.', style='G.Desc.TLabel').pack()

        tk.Button(self.home_menu, text='QUIT', width=18, style='exit.TButton', command=exit).pack(pady=(20, 60),
                                                                                             side=tkinter.BOTTOM)
        tk.Button(self.home_menu, text='PLAY', width=18, style='start.TButton', command=self.show_selection_frame).pack(
            pady=(0, 20),
            side=tkinter.BOTTOM)

        # building animal selection (FRAME)
        self.selected_animal = tkinter.StringVar()
        self.display_animal = tkinter.StringVar()
        self.selected_animal.trace_add("write", self.selected_cb)
        tk.Label(self.selection_frame, text='Pick an animal to describe', style='G.TLabel',
                 font=('Arial', '14', 'bold')).pack(
            pady=(30, 5))
        tk.Label(self.selection_frame, text='Double click to select', style='G.TLabel', font=('Arial', '14')).pack(
            pady=(5, 15))

        self.lb_frame = tk.Frame(self.selection_frame)
        self.listbox = tkinter.Listbox(self.lb_frame, height=16, width=22, bg="white", activestyle='dotbox', font="Helvetica 16",
                                  fg="black")
        self.listbox.insert("end", *self.names)
        self.listbox.configure(justify=tkinter.CENTER)
        self.listbox.bind('<Double-1>', self.doubleclick)

        self.scrollbar = tk.Scrollbar(self.lb_frame)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # building game (FRAME)
        tk.Label(self.game_frame, textvariable=self.display_animal, style='Game.TLabel').pack(pady=(10, 10))

        # create tag to pass to Chatbox to style AI/player text
        self.tags = {
            'player': {'font': 'Helvetica 10'},
            'computer': {'font': 'Helvetica 10 bold italic'}
        }
        self.chatbox = Chatbox(self.game_frame, tags=self.tags, history_padx=20, history_pady=15)
        self.chatbox.user_message("AI", "Hi there player.", "computer")
        self.chatbox.user_message("PLAYER", "Hi there computer!", "player")
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)

        self.b_home = tk.Button(self.game_frame, text='End Game', width=15, style='exit.TButton', command=self.show_home_frame).pack(
            pady=(10, 10))

        self.root.mainloop()

    def exit(self):
        self.root.destroy()

    def show_game_frame(self):
        print("in def: show game frame")
        self.game_frame.pack_forget()
        self.home_menu.pack_forget()
        self.selection_frame.pack_forget()
        self.lb_frame.pack_forget()
        self.game_frame.pack(fill=tkinter.BOTH, expand=1)
        self.root.after(2500, self.we_are_playing)

    def we_are_playing(self):
        print("in def: we are playing")
        if self.game_running:
            new_line = self.get_next_random_answer()
            self.update_chat_box(new_line)
            self.root.after(4000, self.we_are_playing)

    def show_home_frame(self):
        self.game_frame.pack_forget()
        self.selection_frame.pack_forget()
        self.lb_frame.pack_forget()
        self.home_menu.pack(fill=tkinter.BOTH, expand=1)
        self.reset_game()
        print("put the game to an end -> game running on False and chatbox resetted")

    def get_next_random_answer(self):
        print("add new answers!")
        new_string = 'generate string number: ' + str(self.steps)
        self.steps = self.steps+1
        return new_string

    def update_chat_box(self, new_line):
        self.chatbox.user_message("AI", "give me a new line please", "computer")
        self.chatbox.user_message("PLAYER", new_line, "player")
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)

    def reset_chat_box(self):
        self.chatbox.user_message("", " --- THE GAME IS ENDED --- ", "computer")
        self.chatbox.user_message("", " ", "computer")
        self.chatbox.user_message("", " --- LETS START A NEW GAME --- ", "computer")
        self.chatbox.user_message("AI", "Hi there player.", "computer")
        self.chatbox.user_message("PLAYER", "Hi there computer!", "player")
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)

    def reset_game(self):
        self.reset_chat_box()
        self.steps = 0
        self.game_running = False

    def show_selection_frame(self):
        self.game_frame.pack_forget()
        self.home_menu.pack_forget()
        self.lb_frame.pack(padx=(80, 80))
        self.selection_frame.pack(fill=tkinter.BOTH, expand=1)

    def doubleclick(self, event):
        cs = self.listbox.curselection()
        self.selected_animal.set(self.listbox.get(cs))
        self.game_running = True
        self.show_game_frame()


    def selected_cb(self, var, indx, mode):
        self.display_animal.set('Describe selected animal: ' + self.selected_animal.get())


game = Gameplay()
