# sources :
# https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# Chatbox :
# http://code.activestate.com/recipes/580757-chatbox-megawidget-for-tkinter/
#

import tkinter
import tkinter.ttk as tk
from Chatbox import Chatbox
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from Front_speech_from_mic import recognize_speech_from_mic
import json
import speech_recognition as sr
import inflect
import operator
import collections
import predict_animal_on_model


class Gameplay():
    def __init__(self):
        #define online or offline playing
        self.online = False

        if self.online:
            self.es = Elasticsearch(
                hosts=["https://d4e3033cb97744efaf30d6fb0aa64dc9.europe-west1.gcp.cloud.es.io:9243"],
                http_auth=("elastic", "M00PV83HRM8ozH9k6CrXU1wB"))
            self.a = helpers.scan(self.es, query={"query": {"match_all": {}}}, scroll='1m',
                                  index='zoo_raw')  # like others so far
            self.names = [aa['_id'] for aa in self.a]

        self.root = tkinter.Tk()
        self.root.title("Animal Guesser")
        self.root.geometry('450x580')

        # Define game variables
        self.game_running = False
        self.steps = 0
        self.call = 0
        self.memory_guess = []
        self.time_out_job = None

        # Create Animal Guesser
        self.my_guesser = predict_animal_on_model.AnimalPredictor()
        self.names = self.my_guesser.name_dict.keys()


        # Define styling
        self.s = tk.Style()
        self.s.configure("exit.TButton", font=('Arial', '18', 'bold'))
        self.s.configure("start.TButton", font=('Arial', '18', 'bold'))
        self.s.map('exit.TButton',
                   foreground=[('pressed', 'dark red'), ('active', 'red')],
                   background=[('pressed', 'red'), ('active', 'red')])
        self.s.map('start.TButton',
                   foreground=[('pressed', 'dark green'), ('active', 'green')],
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
        tk.Label(self.home_menu, text='The objective of this game is to describe an animal.',
                 style='G.Desc.TLabel').pack(pady=(20, 5))
        tk.Label(self.home_menu, text='After every single description the AI will make a guess.',
                 style='G.Desc.TLabel').pack(pady=(0, 5))
        tk.Label(self.home_menu, text='If the guess is correct you can answer with "Yes",', style='G.Desc.TLabel').pack(
            pady=(0, 5))
        tk.Label(self.home_menu, text='if the guess is wrong you must answer with "No"', style='G.Desc.TLabel').pack(
            pady=(0, 5))
        tk.Label(self.home_menu, text='and provide a following description.', style='G.Desc.TLabel').pack()
        tk.Button(self.home_menu, text='QUIT', width=18, style='exit.TButton', command=exit).pack(pady=(20, 60),
                                                                                                  side=tkinter.BOTTOM)
        tk.Button(self.home_menu, text='PLAY', width=18, style='start.TButton', command=self.show_selection_frame).pack(
            pady=(0, 20), side=tkinter.BOTTOM)

        # building animal selection (FRAME)
        self.selected_animal = tkinter.StringVar()
        self.display_animal = tkinter.StringVar()
        self.display_taboo_words = tkinter.StringVar()
        self.selected_animal.trace_add("write", self.selected_cb)
        tk.Label(self.selection_frame, text='Pick an animal to describe', style='G.TLabel',
                 font=('Arial', '14', 'bold')).pack(
            pady=(30, 5))
        tk.Label(self.selection_frame, text='Double click to select', style='G.TLabel', font=('Arial', '14')).pack(
            pady=(5, 15))

        self.lb_frame = tk.Frame(self.selection_frame)
        self.listbox = tkinter.Listbox(self.lb_frame, height=16, width=22, bg="white", activestyle='dotbox',
                                       font="Helvetica 16",
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
        tk.Label(self.game_frame, textvariable=self.display_animal, style='Game.TLabel').pack(pady=(2, 2))
        tk.Label(self.game_frame, textvariable=self.display_taboo_words, style='Game.TLabel').pack(pady=(0, 0))

        # create tag to pass to Chatbox to style AI/player text
        self.tags = {
            'player': {'font': 'Helvetica 10'},
            'computer': {'font': 'Helvetica 10 bold italic'}
        }
        self.chatbox = Chatbox(self.game_frame, tags=self.tags, history_padx=20, history_pady=15)
        self.chatbox.user_message("AI", "Hi there player, press the Describe button when you are ready to play!",
                                  "computer")
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)

        self.b_rec = tk.Button(self.game_frame, text='Describe', width=10, style='start.TButton',
                               command=self.recognize_text)
        self.b_rec.pack(pady=(2, 2))

        self.b_home = tk.Button(self.game_frame, text='End Game', width=15, style='exit.TButton',
                                command=self.show_home_frame).pack()

        self.root.mainloop()

    def exit(self):
        self.root.destroy()

    def show_game_frame(self):
        self.chatbox.clear()
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)
        self.chatbox.user_message("AI", "Hi there player, press the Describe button when you are ready to play!",
                                  "computer")
        self.game_frame.pack_forget()
        self.home_menu.pack_forget()
        self.selection_frame.pack_forget()
        self.lb_frame.pack_forget()
        self.game_frame.pack(fill=tkinter.BOTH, expand=1)

    def show_home_frame(self):
        self.game_frame.pack_forget()
        self.selection_frame.pack_forget()
        self.lb_frame.pack_forget()
        self.home_menu.pack(fill=tkinter.BOTH, expand=1)
        self.root.after_cancel(self.time_out_job)
        #if self.game_running:
        self.reset_game()
            
###########################################################
###############SPEECH RECOGNITION SCRIPT###################
###########################################################

#Inspired from https://realpython.com/python-speech-recognition/
#Using Google Web Speech API
    def recognize_text(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.no_error_in_ans = True
        # First time the player describes the animal
        if self.call == 0:
            self.description = recognize_speech_from_mic(self.recognizer, self.microphone)
        # After having the guess
        else:
            answer = recognize_speech_from_mic(self.recognizer, self.microphone)
            #If no error (unable to recognize speech or API not available) in player's answer
            if answer["transcription"]:
                #If agent's guess is correct
                if "yes" in answer["transcription"]:
                    self.update_chat_box_player("Yes")
                    self.update_chat_box_ai("Correct! I won!")
                    self.root.after_cancel(self.time_out_job)
                    #To end the game
                    self.description["transcription"] = False
                    self.game_running = False
                #If agent's guess is incorrect, the player provides more information
                #And these new information are added to make another guess
                else:
                    more_info = answer["transcription"].split()
                    add_more_info = " ".join(more_info)
                    self.description["transcription"] = self.description["transcription"] + " " + add_more_info
                    self.update_chat_box_player(self.description["transcription"])
                    self.update_chat_box_ai("Incorrect. Ok I'll try again.")
            #Error in player's answer
            else:
                if self.game_running == True:
                    self.update_chat_box_ai(answer['error'] + '. Please repeat.')
                self.no_error_in_ans = False
        #If no error in player's description and answer
        if self.description["transcription"] and self.no_error_in_ans:
            if self.call == 0:
                self.update_chat_box_player(self.description["transcription"])
            #Check if the player didn't say the taboo words
            for w in self.selected_words:
                if w in self.description["transcription"]:
                    self.update_chat_box_ai("You said {}! It's not allowed, you lost.".format(w))
                    self.game_running = False
            #Agent makes the guess
            if self.game_running:
                if self.online == True:
                    self.taboo_game(self.description["transcription"])
                else:
                    self.guess_animal(self.description["transcription"])
        #If error in player's description
        elif self.description["error"]:
            self.update_chat_box_ai(self.description["error"] + '. Please repeat.')
            #Reset to zero
            self.call= -1
        #If the game was not stopped, loop over the function again
        if self.game_running:
            self.call += 1
            print(self.call)
            self.root.after(200, self.recognize_text)

    def update_chat_box_player(self, new_line):
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)
        self.chatbox.user_message("PLAYER", new_line, "player")

    def update_chat_box_ai(self, new_line):
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)
        self.chatbox.user_message("AI", new_line, "computer")
        
    ########################################################    
    ##################TABOO GAME SCRIPT#####################
    ########################################################

    # Select the Taboo words, the top 3 occuring words in each description
    def taboo_words(self):
        if self.online:
            animal = self.selected_animal.get()
            counts = dict()
            engine = inflect.engine()
            self.selected_words = []
            to_remove = []
            #Get the animal description from ElasticSearch
            self.get_text = helpers.scan(self.es, query={"query": {"terms": {"_id": [str(animal)]}}}, scroll='1m',
                                         index='zoo_cleaned')
            full_text = [hit['_source']['wiki'] for hit in self.get_text]
            words = full_text[0].split()
            # Compute the most recurring words in the description
            for word in words:
                if word in counts:
                    counts[word] += 1
                else:
                    counts[word] = 1
            # Sort the dictionary to get the top three recurring words at the top
            sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
            sorted_dict = collections.OrderedDict(sorted_counts)
            # Remove words with less than 2 characters (often missplit alone letters or numbers)
            for w in list(sorted_dict.keys()):
                # w.split()
                if len(w) > 2:
                    self.selected_words.append(w)
            # Words appearing a lot in all descriptions
            to_remove.extend(['areas', 'years', 'males', 'females', 'used', 'occur', 'called', 'western', 'families', 'family'])
            self.selected_words = [w for w in self.selected_words if w.lower() not in to_remove]
            # Take the top 3 words
            self.selected_words = self.selected_words[:3]
            #Append with animal name (forbidden as well)
            self.selected_words.append(animal)
        else:
            #play without taboo words
            self.selected_words = ['offline', 'dummy', 'variables']
        return self.selected_words
    
    #ElasticSearch query
    def search_func(self, search_query):

        search_object = {
            "query": {
                "query_string": {
                    "query": search_query
                }
            }
        }
        return json.dumps(search_object)
    

    # Make the guess based on the ElasticSearch query
    def taboo_game(self, player_description):
        guesses_scoring = self.es.search(index='zoo_cleaned', body=self.search_func(player_description))
        if len(guesses_scoring['hits']['hits']) > 0:
            for i in range(0, len(guesses_scoring['hits']['hits'])):
                guess = guesses_scoring['hits']['hits'][i]['_id']
                if guess not in self.memory_guess:
                    self.memory_guess.append(guess)
                    self.update_chat_box_ai("Is it a {}?".format(guess))
                    break
                else:
                    continue
        else:
            self.update_chat_box_ai("I have no idea of what you are describing, provide more info!")

    def guess_animal(self, player_description):
        ranking = self.my_guesser.get_prediction_ranking_exclude_wrong_animals(player_description, self.memory_guess)
        guess = list(ranking.keys())[0]
        self.memory_guess.append(guess)
        self.update_chat_box_ai("Is it a {}?".format(guess))

    def reset_chat_box(self):
        self.chatbox.clear()
        self.chatbox.interior.pack(expand=True, fill=tkinter.BOTH)

    def reset_game(self):
        self.steps = 0
        self.game_running = False
        self.call = 0
        self.memory_guess = []
        self.reset_chat_box()
        # TODO
        #self.show_home_frame()

    def show_selection_frame(self):
        self.game_frame.pack_forget()
        self.home_menu.pack_forget()
        self.lb_frame.pack(padx=(80, 80))
        self.selection_frame.pack(fill=tkinter.BOTH, expand=1)

    def time_ran_out(self):
        self.update_chat_box_ai("Sorry your time ran out ... ")
        self.update_chat_box_ai("We can try again, go back to homescreen to start new game !")
        # TODO
        self.game_running = False
        self.out_of_time = True

    def doubleclick(self, event):
        cs = self.listbox.curselection()
        self.selected_animal.set(self.listbox.get(cs))
        self.game_running = True
        self.time_out_job = self.root.after(40000, self.time_ran_out)
        self.show_game_frame()

    def selected_cb(self, var, indx, mode):
        words = self.taboo_words()
        word1 = words[0]
        word2 = words[1]
        word3 = words[2]

        self.display_animal.set('Describe selected animal: ' + self.selected_animal.get())
        self.display_taboo_words.set('Do NOT say the words: ' + word1 + ', ' + word2 + ', ' + word3)


game = Gameplay()
