import tkinter as tk
from tkinter import *
from tinydb import TinyDB, Query
import cv2
from simple_facerec_v2 import SimpleFacerec
from PIL import Image, ImageTk
import subprocess
from time import strftime
from datetime import datetime, timedelta

db = TinyDB('db.jason')
Search = Query()

def build_student_login_window(username, selected_exam_name, selected_exam_id):
    root = Tk()
    root.iconbitmap('C:/Users/Lenovo/Downloads/HSKL_logo_bitmap.ico')
    root.title("AFDIM: Klausuranmeldung mit Gesichtserkennung")
    # root.attributes('-fullscreen', True)
    root.state("zoomed")
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Full frame for whole window
    full_frame = tk.Frame(root, background="#06606a", width=500, height=500)
    full_frame.grid(row=0, column=0, sticky="nsew")

    student_id_string = ""

    def show_info_of_recognized_person(student_id):
        student_information.config(state='normal')
        student_information.delete('1.0', 'end')
        student_information.config(foreground="Black")

        if student_id != "":
            students = db.table('Studierende')
            student_list = students.search(Search.Matrikelnummer == student_id)
            if student_list != []:
                student_list_clean = []
                for element in student_list:
                    student_list_clean.append(element['Matrikelnummer'])
                    student_list_clean.append(element['Nachname'])
                    student_list_clean.append(element['Vorname'])

                student_information.insert(1.0,
                                           "Matrikelnummer:\t\t" + student_list_clean[0].strip() +
                                           "\nNachname:\t\t" + student_list_clean[1] +
                                           "\nVorname:\t\t" + student_list_clean[2])
            else:
                student_information.configure(foreground="Red")
                student_information.insert(1.0, "Person nicht in Datenbank!")
        else:
            student_information.insert('1.0', "Matrikelnummer:\nNachname:\nVorname:")
        student_information.config(state='disabled')

    def login_recognized_student():
        db = TinyDB('db.jason') #Get the newest version of the Database
        #Search=Query()
        login_confirmation.config(state='normal')
        login_confirmation.delete(1.0, 'end')

        student_id = student_information.get(1.17, 1.23)  # Get Matrikelnummer
        student = db.table('Studierende').search(Search.Matrikelnummer == student_id)
        exam_participant = db.table('Klausurteilnahme').search((Search.Klausurid == selected_exam_id) & (Search.Matrikelnummer == student_id) & (Search.Teilnahme == False))

        if student != [] and exam_participant != []:
            # Student exists and not already set as "nimmt teil" for this Exam
            db.table('Klausurteilnahme').update({'Teilnahme': True}, (Search.Klausurid == selected_exam_id) & (Search.Matrikelnummer == student_id) & (Search.Teilnahme == False))
            login_confirmation.insert(1.0, student_id + " nimmt an der Klausur teil.")
        elif db.table('Klausurteilnahme').search((Search.Klausurid == selected_exam_id) & (Search.Matrikelnummer == student_id) & (Search.Teilnahme == True)) != []:
            # Student already set as "nimmt teil" for this Exam
            login_confirmation.insert(1.0, student_id + " nimmt an dieser Klausur bereits teil.")
        elif student != [] and exam_participant == []:

            # Student not "angemeldet" for this Exam
            login_confirmation.insert(1.0, student_id + " ist für diese Klausur nicht\nangemeldet.")
        else:
            login_confirmation.insert(1.0, "Teilnahme war nicht möglich.")
        login_confirmation.config(state='disabled')

    def return_to_login_window():
        cv2.destroyAllWindows()
        cap.release()
        root.destroy()
        subprocess.call("main.py", shell=True)

    def build_timer_window():
        cv2.destroyAllWindows()
        cap.release()
        student_login_ui_frame.destroy()

        selected_exam = db.table('Klausuren').search(Search.Klausurid == selected_exam_id)
        selected_exam_length = selected_exam[0]['Dauer']

        # Inner Frame
        timer_ui_frame = tk.Frame(full_frame, bg="white")
        timer_ui_frame.place(relx=.5, rely=.5, anchor="center", relwidth=.95, relheight=.95)

        # Equal Weight for whole grid
        timer_ui_frame.grid_columnconfigure(0, weight=1)
        timer_ui_frame.grid_rowconfigure(0, weight=1)
        timer_ui_frame.grid_rowconfigure(1, weight=1)
        timer_ui_frame.grid_rowconfigure(2, weight=1)
        timer_ui_frame.grid_rowconfigure(3, weight=1)

        def time_clock():
            hour = strftime('%H:%M:%S')
            time_label.config(text='Uhrzeit: ' + hour)
            time_label.after(1000, time_clock)

        #Time
        time_label = Label(timer_ui_frame, text='Uhrzeit: ', bg=timer_ui_frame["background"],  font=("Arial", 60))
        time_label.grid(row=0, column=0, sticky="EW")

        #Exam End-time
        now = datetime.now().time()
        # Just use January the first, 2000
        d1 = datetime(2000, 1, 1, now.hour, now.minute)#, now.second)
        d2 = d1 + timedelta(minutes=selected_exam_length)
        timer_label = Label(timer_ui_frame, text='Klausurende: ' + d2.strftime('%H:%M:%S') + ' Uhr', bg=timer_ui_frame["background"], font=("Arial", 60))
        timer_label.grid(row=1, column=0, sticky="EW")

        # Exam Info
        # Exam detailled Infos
        text_box = Text(timer_ui_frame, height=7, font=("Arial", 25), relief="solid")
        text_box.grid(row=2, padx=10, pady=10, sticky="EW")

        exam = db.table('Klausuren').search(Search.Klausurid == selected_exam_id)
        text_box.insert(1.0, "Klausur:\t\t" + exam[0]['Klausurname'] +
                        "\nDozent:\t\t" + exam[0]['Dozent'] + "\nDatum:\t\t" + exam[0]['Datum'] +
                        "\nRaum:\t\t" + exam[0]['Raum'] + "\nZeitraum:\t\t" + exam[0]['Zeitraum'] +
                        "\nDauer:\t\t" + str(exam[0]['Dauer']) + " min" +
                        "\nErlaubte Hilfsmittel:\t" + exam[0]['Hilfsmittel'])
        text_box.config(state='disabled')

        #Quit Button
        quit_button = Button(timer_ui_frame, text="Beenden", width=35, relief='groove', highlightcolor='black', bg='red', fg='black', activeforeground='black', activebackground='grey',  command=lambda: root.destroy(), font=("Arial", 15)).grid(row=3, padx=10, pady=10)

        time_clock()
        root.mainloop()


    # Inner Frame
    student_login_ui_frame = tk.Frame(full_frame, bg="white")
    student_login_ui_frame.place(relx=.5, rely=.5, anchor="center", relwidth=.95, relheight=.95)

    # Equal Weight for whole grid
    student_login_ui_frame.grid_columnconfigure(0, weight=1)
    student_login_ui_frame.grid_columnconfigure(1, weight=1)
    student_login_ui_frame.grid_columnconfigure(2, weight=5)
    student_login_ui_frame.grid_rowconfigure(0, weight=1)
    student_login_ui_frame.grid_rowconfigure(1, weight=1)
    student_login_ui_frame.grid_rowconfigure(2, weight=1)
    student_login_ui_frame.grid_rowconfigure(3, weight=1)
    student_login_ui_frame.grid_rowconfigure(4, weight=1)
    student_login_ui_frame.grid_rowconfigure(5, weight=1)

    #Title
    exam_title = Label(student_login_ui_frame, text=selected_exam_name, bg=student_login_ui_frame["background"], font=("Arial", 15))
    exam_title.grid(row=0, column=0, columnspan=3, sticky="EW")

    #Camera View
    camera_frame = LabelFrame(student_login_ui_frame, bg ="white")
    camera_frame.grid(row=1, column=0, rowspan=3, padx=10, pady=10,  sticky="NESW")

    L1 = Label(camera_frame, bg="white")
    L1.pack()

    #Right Information
    student_information = Text(student_login_ui_frame, height=3, font=("Arial", 25), relief='flat')
    student_information.insert('1.0',  "Matrikelnummer:\nNachname:\nVorname:")
    student_information.config(state='disabled')
    student_information.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="NESW")

    login_confirmation = Text(student_login_ui_frame, height=1, font=("Arial", 25), relief="flat")
    login_confirmation.grid(row=2, column=1, columnspan=2, rowspan=2, padx=10, pady=10, sticky="NESW")
    login_confirmation.config(state='disabled')

    #Buttons
    button_student_participate = Button(student_login_ui_frame, text="Klausurteilnahme bestätigen", width=35, relief='groove', highlightcolor='black', bg='lightgreen', fg='black', activeforeground='black', activebackground='grey', command= login_recognized_student, font=("Arial", 15)).grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky='EW')
    button_start_exam = Button(student_login_ui_frame, text="Klausur starten", width=35, relief='groove', highlightcolor='black', bg='green', fg='black', activeforeground='black', activebackground='grey', command=build_timer_window, font=("Arial", 15)).grid(row=5, column=0, padx=10, pady=10)
    button_back = Button(student_login_ui_frame, text="Zurück", width=35, relief='groove', highlightcolor='black', bg='yellow', fg='black', activeforeground='black', activebackground='grey', command=return_to_login_window, font=("Arial", 15)).grid(row=5, column=1, padx=10, pady=10)
    button_quit = Button(student_login_ui_frame, text="Beenden", width=35, relief='groove', highlightcolor='black', bg='red', fg='black', activeforeground='black', activebackground='grey',  command=lambda: root.destroy(), font=("Arial", 15)).grid(row=5, column=2, padx=10, pady=10)


    cap = cv2.VideoCapture(0)
    # Encode faces from a folder
    sfr = SimpleFacerec()
    sfr.load_encoding_images('C:/Users/Lenovo/Desktop/images')

    while True:
        ret, img = cap.read()
        face_locations, student_id, prob_text = sfr.detect_known_faces(img)
        for face_loc, name in zip(face_locations, student_id):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            student_id_string = str(student_id)[2:-2]

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 8)
            cv2.rectangle(img, (x1, y1), (x2, y2), (50, 205, 50), 4)
            cv2.putText(img, prob_text, (x1 + 50, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 8)
            cv2.putText(img, prob_text, (x1 + 50, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            #cv2.putText(img, name, (x1 + 50, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 8)
            #cv2.putText(img, name, (x1 + 50, y2 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            # text = "{:.2f}%".format(confi * 100)
            # cv2.putText(img, prob_text, (x1 + 50, y2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 200), 2)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(img))
        L1['image'] = img

        show_info_of_recognized_person(student_id_string)
        student_id_string = ""

        root.update()

#build_student_login_window("admin", "Layout-Test", 1)
