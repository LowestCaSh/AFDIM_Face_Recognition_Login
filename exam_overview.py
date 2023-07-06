from tkinter import *
import tkinter as tk
from tkinter import ttk
from tinydb import TinyDB, Query

db = TinyDB('db.jason')
Search = Query()

root = Tk()
root.iconbitmap('C:/Users/Lenovo/Downloads/HSKL_logo_bitmap.ico')
root.title("AFDIM: Übersicht der Klausuranmeldungen und -teilnahmen")
root.state("zoomed")

def sort():
    rows = [(exam_table.item(item, 'values'), item) for item in exam_table.get_children('')]
    # if you want to sort according to a single column:
    # rows = [(tree.set(item, column), item) for item in tree.get_children('')]
    rows.sort()

    # rearrange items in sorted positions
    for index, (values, item) in enumerate(rows):
        exam_table.move(item, '', index)

exam_table = ttk.Treeview(root)
exam_table.pack(fill='both', expand='true')

exam_table['columns'] = ('exam_id', 'exam_name', 'student_id', 'student_name', 'participation')

exam_table.column("#0", width=0, stretch=NO)
exam_table.column('exam_id', anchor=CENTER, width=70)
exam_table.column('exam_name', anchor=CENTER, width=200)
exam_table.column('student_id', anchor=CENTER, width=70)
exam_table.column('student_name', anchor=CENTER, width=70)
exam_table.column('participation', anchor=CENTER, width=70)

exam_table.heading("#0", text="", anchor=CENTER)
exam_table.heading('exam_id', text="Klausur-ID", anchor=CENTER)
exam_table.heading('exam_name', text="Klausurname", anchor=CENTER)
exam_table.heading('student_id', text="Matrikelnummer", anchor=CENTER)
exam_table.heading('student_name', text="Name", anchor=CENTER)
exam_table.heading('participation', text="Teilnahme", anchor=CENTER)

for item in db.table('Klausurteilnahme'):
    exam = db.table('Klausuren').search(Search.Klausurid == item['Klausurid'])
    student = db.table('Studierende').search(Search.Matrikelnummer == item['Matrikelnummer'])
    exam_table.insert(parent='', index='end', text='', values=(item['Klausurid'], exam[0]['Klausurname'], item['Matrikelnummer'], student[0]['Vorname'] + ' ' + student[0]['Nachname'], item['Teilnahme']))

sort()
root.mainloop()