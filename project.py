from tkinter import *
from tkinter import ttk
import sqlite3
from datetime import datetime

class CreateStudent:
    def __init__(self, main):
        self.main_window = main
        self.setup_ui()
        self.create_table()
        self.load_data()

    def setup_ui(self):
        # Setup Frames
        self.C_Frame = Frame(self.main_window, height=600, width=400, relief=GROOVE, border=2, bg="white")
        self.C_Frame.pack(side=LEFT, fill=BOTH, padx=10, pady=10)
        self.C_Frame.pack_propagate(0)

        self.S_S_Details = Frame(self.main_window, height=600, width=800, relief=GROOVE, border=2, bg="white")
        self.S_S_Details.pack(side=LEFT, fill=BOTH, padx=10, pady=10)

        # Setup Labels and Entries (without "Status")
        labels = ["ID", "Name", "Department"]
        self.entries = {}

        for idx, label in enumerate(labels):
            Label(self.C_Frame, text=f"{label}:", font="arial 12 bold", bg="white").place(x=40, y=60 + idx * 30)
            entry = Entry(self.C_Frame, width=40)
            entry.place(x=150, y=60 + idx * 30)
            self.entries[label] = entry

        # Setup Buttons
        self.Button_Frame = Frame(self.C_Frame, height=250, width=250, relief=GROOVE, border=2, bg="white")
        self.Button_Frame.place(x=40, y=150)
        buttons = [("Add", self.add_record), ("Delete", self.delete_record), ("Update", self.update_record), ("Clear", self.clear_entries)]

        for text, command in buttons:
            Button(self.Button_Frame, text=text, font="arial 15 bold", width=25, command=command).pack(pady=5)

        # Setup Treeview (with "Status")
        self.tree = ttk.Treeview(self.S_S_Details, columns=("ID", "Name", "Department", "Arrived At", "Status"), show='headings', height=25)
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", anchor=CENTER, width=80)  # Adjusted width
        self.tree.heading("Name", text="Name")
        self.tree.column("Name", anchor=CENTER, width=170)  # Adjusted width
        self.tree.heading("Department", text="Department")
        self.tree.column("Department", anchor=CENTER, width=170)  # Adjusted width
        self.tree.heading("Arrived At", text="Arrived At")
        self.tree.column("Arrived At", anchor=CENTER, width=170)  # Adjusted width
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", anchor=CENTER, width=170)  # Adjusted width
        self.tree.pack(fill=BOTH, expand=True)

    def create_table(self):
        try:
            with sqlite3.connect("data.db") as conn:
                cursor = conn.cursor()
                cursor.execute('DROP TABLE IF EXISTS data')
                cursor.execute('''
                    CREATE TABLE data (
                        ID INTEGER PRIMARY KEY,
                        NAME TEXT,
                        DEPARTMENT TEXT,
                        ARRIVED_AT TEXT,
                        STATUS TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def load_data(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data
        try:
            with sqlite3.connect("data.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM data")
                rows = cursor.fetchall()
                for row in rows:
                    self.tree.insert("", END, values=row)
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")

    def add_record(self):
        id = self.entries["ID"].get()
        name = self.entries["Name"].get()
        department = self.entries["Department"].get()
        arrived_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = self.get_status(arrived_at)

        try:
            with sqlite3.connect("data.db") as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO data (ID, NAME, DEPARTMENT, ARRIVED_AT, STATUS) VALUES (?, ?, ?, ?, ?)', (id, name, department, arrived_at, status))
                conn.commit()
            self.tree.insert("", END, values=(id, name, department, arrived_at, status))
            self.clear_entries()
        except sqlite3.Error as e:
            print(f"Error adding record: {e}")

    def delete_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        selected_id = self.tree.item(selected_item[0])['values'][0]
        try:
            with sqlite3.connect("data.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM data WHERE ID=?", (selected_id,))
                conn.commit()
            self.tree.delete(selected_item[0])
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")

    def update_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        id = self.entries["ID"].get()
        name = self.entries["Name"].get()
        department = self.entries["Department"].get()
        arrived_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = self.get_status(arrived_at)
        old_id = self.tree.item(selected_item[0])['values'][0]

        try:
            with sqlite3.connect("data.db") as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE data SET ID=?, NAME=?, DEPARTMENT=?, ARRIVED_AT=?, STATUS=? WHERE ID=?', (id, name, department, arrived_at, status, old_id))
                conn.commit()
            self.tree.item(selected_item[0], values=(id, name, department, arrived_at, status))
        except sqlite3.Error as e:
            print(f"Error updating record: {e}")

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, END)

    def get_status(self, arrived_at):
        try:
            expected_time = datetime.strptime('10:00:00', '%H:%M:%S').time()
            arrival_time = datetime.strptime(arrived_at, '%Y-%m-%d %H:%M:%S').time()
            if arrival_time > expected_time:
                return "Late"
            else:
                return "On Time"
        except ValueError:
            return "Invalid Time"

if __name__ == "__main__":
    main_window = Tk()
    main_window.title("Late Comers Analysis")
    main_window.resizable(False, False)
    main_window.geometry("1200x600")

    Title = Frame(main_window, height=50, width=1200, relief=GROOVE, bg="white")
    Title.pack(fill=X)
    T_Text = Label(Title, text="Student Data Management System", font="arial 24 bold", bg="white")
    T_Text.pack()

    CreateStudent(main_window)

    main_window.mainloop()
