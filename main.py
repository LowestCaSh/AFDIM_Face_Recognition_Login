import tkinter as tk
from tkinter import *
from tkinter import ttk
from tinydb import TinyDB, Query
import keyboard
from PIL import ImageTk, Image
import student_login_window

db = TinyDB('db.jason')

headline_size = 25
LARGEFONT = ("Arial", headline_size)
root = Tk()
root.iconbitmap('C:/Users/Lenovo/Downloads/HSKL_logo_bitmap.ico')
root.title("AFDIM: Klausuranmeldung mit Gesichtserkennung")
#root.attributes('-fullscreen', True)
root.state("zoomed")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Full frame for whole window
full_frame = tk.Frame(root, background="#06606a", width=500, height=500)
full_frame.grid(row=0, column=0, sticky="nsew")

#Login Window
def build_login_window():

    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return ("break")

    def get_password_by_username(username):
        Search = Query()
        aufsicht = db.table('Aufsicht')
        person = aufsicht.search(Search.Benutzername == username)
        if(person == []):
            return
        else:
            for element in person:
                passwort = element['Passwort']
            return str(passwort)

    def check_login_data(event=None):
        username = username_textbox.get('1.0', 'end-1c')
        password = password_textbox.get()
        if(password == get_password_by_username(username)):
            login_ui_frame.destroy()
            build_exam_selection_window(username)
        else:
            print("Login failed")
            error_textbox.config(state='normal')
            error_textbox.delete('1.0', 'end')
            error_textbox.insert('1.0', "Benutzername und Passwort stimmen nicht überein!")
            error_textbox.config(state='disabled')

    #Inner Frame
    login_ui_frame = tk.Frame(full_frame, bg="white")
    login_ui_frame.place(anchor="center", relwidth=.95, relheight=.95, rely=.5, relx=.5)

    # Equal Weight for whole grid
    login_ui_frame.grid_columnconfigure(0, weight=1)
    login_ui_frame.grid_columnconfigure(1, weight=1)
    login_ui_frame.grid_columnconfigure(2, weight=1)
    login_ui_frame.grid_rowconfigure(0, weight=1)
    login_ui_frame.grid_rowconfigure(1, weight=1)
    login_ui_frame.grid_rowconfigure(2, weight=1)
    login_ui_frame.grid_rowconfigure(3, weight=1)
    login_ui_frame.grid_rowconfigure(4, weight=1)

    login_label = Label(login_ui_frame, background=login_ui_frame["background"], text="Login Page", font=("Arial", 35)).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

    # Username/Password + Label/EntryBox
    username_label = Label(login_ui_frame, background=login_ui_frame["background"], text="Benutzername: ", font=("Arial", 25))
    username_label.grid(row=1, column=0, padx=10, pady=10,)
    username_textbox = Text(login_ui_frame, bg="white", relief="solid", height=1, font=("Arial", 15))
    username_textbox.bind("<Tab>", focus_next_widget)
    username_textbox.bind("<Return>", check_login_data)
    username_textbox.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    password_label = Label(login_ui_frame, background=login_ui_frame["background"], text="Passwort: ", font=("Arial", 25))
    password_label.grid(row=2, column=0, padx=10, pady=10,)
    password_textbox = Entry(login_ui_frame,  show="*", bg="white", relief="solid", font=("Arial", 15))
    password_textbox.bind("<Tab>", focus_next_widget)
    password_textbox.bind("<Return>", check_login_data)
    password_textbox.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    error_textbox = Text(login_ui_frame, bg=login_ui_frame["background"], relief="flat", height=1, font=("Arial", 15), foreground="red")
    error_textbox.config(state='disabled')
    error_textbox.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    #Buttons
    button_login = Button(login_ui_frame, text="Login", width=40, relief='groove', highlightcolor='black', bg='green', fg='black', activeforeground='black', activebackground='grey', command=check_login_data, font=("Arial", 15))
    button_login.grid(row=4, column=0, padx=10, pady=10)
    button_quit = Button(login_ui_frame, text="Beenden", width=40, relief='groove', highlightcolor='black', bg='red', fg='black', activeforeground='black', activebackground='grey', command=lambda: root.quit(), font=("Arial", 15)).grid(row=4, column=2, padx=10, pady=10, sticky="e")

#Exam Selection Window
def build_exam_selection_window(username):

    def get_exams_by_admin(username):
        Search = Query()
        return db.table('Klausuren').search(Search.Aufsicht == username)

    exam_list_for_dropdown = []
    exam_list = get_exams_by_admin(username)

    def get_exams_for_dropdown():
        for element in exam_list:
            exam_list_for_dropdown.append(element['Klausurname'] + "; Raum: " + element['Raum'] + "; Dozent: " + element['Dozent'])
        return(exam_list_for_dropdown)

    def get_all_exams():
        exam_list = get_exams_by_admin(username)
        exam_list_clean = []
        for element in exam_list:
            temp_list = []
            temp_list.append(element['Klausurid'])
            temp_list.append(element['Klausurname'])
            temp_list.append(element['Raum'])
            temp_list.append(element['Dozent'])
            temp_list.append(element['Datum'])
            temp_list.append(element['Zeitraum'])
            temp_list.append(element['Dauer'])
            temp_list.append(element['Hilfsmittel'])
            exam_list_clean.append(temp_list)
        return (exam_list_clean)

    def set_exam_info(command):
        #get Index of Selection, exam_list uses the same, so we can use the index for that as well
        index = 0
        for i in range(len(exam_list_for_dropdown)):
            if(selection.get() == exam_list_for_dropdown[i]):
                index = i
        exam = exam_list[index]

        global exam_id
        exam_id = exam['Klausurid']

        text_box.config(state='normal')
        text_box.delete('1.0', 'end')


        text_box.insert(1.0, "Klausur:\t\t" + exam['Klausurname'] +
                        "\nDozent:\t\t" + exam['Dozent'] +
                        "\nDatum:\t\t" + exam['Datum'] +
                        "\nRaum:\t\t" + exam['Raum'] +
                        "\nZeitraum:\t\t" + exam['Zeitraum'] +
                        "\nDauer:\t\t" + str(exam['Dauer']) + " min" +
                        "\nErlaubte Hilfsmittel:\t" + exam['Hilfsmittel'])
        text_box.config(state='disabled')

    def set_exam_info_by_index(index):
        exam = exam_list[index]
        global exam_id
        exam_id = exam['Klausurid']

        text_box.config(state='normal')
        text_box.delete('1.0', 'end')

        text_box.insert(1.0, "Klausur:\t\t" + exam['Klausurname'] +
                        "\nDozent:\t\t" + exam['Dozent'] +
                        "\nDatum:\t\t" + exam['Datum'] +
                        "\nRaum:\t\t" + exam['Raum'] +
                        "\nZeitraum:\t\t" + exam['Zeitraum'] +
                        "\nDauer:\t\t" + str(exam['Dauer']) + " min" +
                        "\nErlaubte Hilfsmittel:\t" + exam['Hilfsmittel'])
        text_box.config(state='disabled')

    exam_selection_frame = tk.Frame(full_frame, bg="white")
    exam_selection_frame.place(relx=.5, rely=.5, anchor="center", relwidth=.95, relheight=.95)

    # Equal Weight for whole grid
    exam_selection_frame.grid_columnconfigure(0, weight=1)
    exam_selection_frame.grid_columnconfigure(1, weight=1)
    exam_selection_frame.grid_columnconfigure(2, weight=1)
    exam_selection_frame.grid_rowconfigure(0, weight=1)
    exam_selection_frame.grid_rowconfigure(1, weight=1)
    exam_selection_frame.grid_rowconfigure(2, weight=1)

    # Exam Label
    exam_text = Label(exam_selection_frame, text="Klausur:", bg=exam_selection_frame["background"], font=("Arial", 25)).grid(row=0, column=0, sticky="EW")
    textStyle = ttk.Style()
    textStyle.configure('my.TMenubutton', font=('Arial', 15))

    #Dropdown Menu
    exam_list_for_dropdown = get_exams_for_dropdown()

    selection = StringVar()
    exam_selection = ttk.OptionMenu(exam_selection_frame, selection, exam_list_for_dropdown[0], *exam_list_for_dropdown, command=set_exam_info, style='my.TMenubutton')
    exam_selection.config(width=100)
    exam_selection.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="EW")

    # Exam detailled Infos
    text_box = Text(exam_selection_frame, height=7, font=("Arial", 25), relief="solid")
    set_exam_info_by_index(0) #this is only for the default selection, in this case index 0
    text_box.grid(row=1, columnspan=3, padx=10, pady=10, sticky="EW")
    text_box.config(state='disabled')

    # Buttons
    button_confirm_exam = Button(exam_selection_frame, text="Bestätigen", width=35, relief='groove', highlightcolor='black', bg='green', fg='black', activeforeground='black', activebackground='grey', command=lambda: build_student_login_window(username, selection.get(), exam_id), font=("Arial", 15)).grid(row=2, column=0, padx=10, pady=10)
    button_back = Button(exam_selection_frame, text="Zurück", width=35, relief='groove', highlightcolor='black', bg='yellow', fg='black', activeforeground='black', activebackground='grey',  command=lambda: build_login_window(), font=("Arial", 15)).grid(row=2, column=1, padx=10, pady=10)
    keyboard.add_hotkey('Escape', lambda: build_login_window())
    button_quit = Button(exam_selection_frame, text="Beenden", width=35, relief='groove', highlightcolor='black', bg='red', fg='black', activeforeground='black', activebackground='grey',  command=lambda: root.quit(), font=("Arial", 15)).grid(row=2, column = 2, padx=10, pady=10)

def build_student_login_window(username, selected_exam_name, selected_exam_id):
    root.destroy()
    student_login_window.build_student_login_window(username, selected_exam_name, selected_exam_id)

build_login_window()
root.mainloop()


