from tkinter import *
from main import Chatbot
from tkinter import ttk

class gui:

    def __init__(self, database_name, nrows):
        self.bot = Chatbot(database_name = "base_offres_propre.csv", nrows=1000)
        botrun = self.bot.run(information = ' ')
        print(botrun)
        self.fenetre = Tk()

        self.question = StringVar(self.fenetre)
        self.question.set(botrun[0])
        self.reponse = StringVar(self.fenetre)
        self.reponse.set(botrun[1])
        self.entree = Entry(self.fenetre, textvariable=' ', width=30)
        self.LabelResultat = Label(self.fenetre, textvariable = self.reponse, width=30, wraplength=250)
        self.label = Label(self.fenetre, textvariable=self.question)

        self.canvas = Canvas(self.fenetre, borderwidth=0, background="#ffffff")
        self.frame = Frame(self.canvas, background="#ffffff")
        self.vsb = Scrollbar(self.fenetre, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.run()




    def populate(self,frame, liste_offres):
        for row in range(10):
            Label(self.frame, text="%s" % row, width=3, borderwidth="1",
                     relief="solid").grid(row=row, column=0)
            Label(self.frame, text=liste_offres[i]).grid(row=row, column=1)

    def send_info(self, event):
        print(self.entree.get())
        botrun = self.bot.run(self.entree.get())
        self.question.set(botrun[0])
        self.reponse.set(botrun[1])
        self.LabelResultat.configure(textvariable = self.reponse)

        if self.bot.step == 5 :
            self.populate(self.fenetre, self.bot.liste_offres)

    def affiche_fenetre_texte(self):
        pass

    def reset(self, event):
        bot.reset()
        label.configure(textvariable =self.question)
        self.entree.delete(0, 'end')
        self.LabelResultat.configure(textvariable = "")

    def onFrameConfigure(self):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def run(self):
        self.fenetre.wm_title("Chatbot")
        self.fenetre.resizable(width=True, height=True)
        self.fenetre.bind('<Return>', self.send_info)


        self.label.grid(row=0,column=0)

        self.entree.grid(row=1,column=0)

        ok_button = Button(self.fenetre, text ='OK')
        ok_button.bind("<Button-1>", self.send_info)
        ok_button.grid(row=2,column=0)

        reset_button = Button(self.fenetre, text ='Reset')
        reset_button.bind("<Button-1>", self.reset)
        reset_button.grid(row=2,column=1)

        quit_button = Button(self.fenetre, text ='Quitter', command=self.fenetre.destroy)
        quit_button.grid(row=2,column=2)

        self.LabelResultat.grid(row=3,column=0)


        self.vsb.pack(side="right", fill="y")
        print("a")
        self.canvas.pack( side="left", fill="both", expand=True)
        print("b")
        self.canvas.create_window((10,10), window=self.frame, anchor="nw")
        print("c")

        self.frame.bind("<Configure>", lambda event, canvas=self.canvas: onFrameConfigure(self.canvas))
        print("d")
        self.fenetre.mainloop()

# bot = Chatbot(database_name = "base_offres.csv", nrows=1000 )
bot_gui = gui(database_name = "base_offres.csv", nrows=1000 )
