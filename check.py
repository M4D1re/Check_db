import sqlite3
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
from idlelib.tooltip import Hovertip

def connection():
    conn = sqlite3.connect('usersDB.db')
    return conn

def setup_admin():
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, password TEXT NOT NULL)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, password TEXT NOT NULL)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
            cursor.execute("INSERT OR IGNORE INTO admin (id, password) VALUES (1, 'admin_password')")
            conn.commit()
    except sqlite3.Error as e:
        print(f"ERROR: {e}")

def user_data(username, password):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            return user
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False

def appendUser(username, password):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            cur_user = cursor.fetchone()
            if cur_user:
                return False
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            return True
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False

def deleteUser(username, password):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                cursor.execute("DELETE FROM notes WHERE user_id = ?", (user[0],))
                cursor.execute("DELETE FROM users WHERE username = ? AND password = ?", (username, password))
                conn.commit()
                return cursor.rowcount > 0  # Returns True if at least one row is deleted
            return False
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False

def deleteAllUsers(admin_password):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE password = ?", (admin_password,))
            admin = cursor.fetchone()
            if admin:
                cursor.execute("DELETE FROM notes")
                cursor.execute("DELETE FROM users")
                conn.commit()
                return True
            else:
                return False
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False

def save_note_content(user_id, content):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO notes (user_id, content) VALUES (?, ?)", (user_id, content))
            conn.commit()
    except sqlite3.Error as e:
        print(f"ERROR: {e}")

def get_note_content(user_id):
    conn = connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM notes WHERE user_id = ?", (user_id,))
            note = cursor.fetchone()
            return note[0] if note else ""
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return ""

def show_notes_window(user_id):
    notes_window = Toplevel(app)
    notes_window.title("User Notes")
    notes_window.geometry("400x300")

    text_area = Text(notes_window,
                     wrap=WORD)
    text_area.pack(expand=True,
                   fill=BOTH)

    # Load the existing note content for the user
    note_content = get_note_content(user_id)
    text_area.insert('1.0', note_content)

    def save_notes():
        content = text_area.get("1.0", END)
        save_note_content(user_id, content)
        messagebox.showinfo("Saved", "Notes have been saved.")

    save_button = Button(notes_window,
                         text="Save",
                         command=save_notes)
    save_button.pack(side=BOTTOM,
                     pady=10)

def inputLogin():
    username = entry1.get()
    password = entry2.get()
    user_info = user_data(username, password)
    if user_info:
        user_id, username, password = user_info[:3]
        messagebox.showinfo("OK!", f"Hello, {username}!")
        entry2.delete(0, END)
        show_notes_window(user_id)
    else:
        messagebox.showerror("Access Denied", "The data is not correct.")
        entry2.delete(0, END)

def inputRegister():
    username = entry1.get()
    password = entry2.get()
    if not username or not password:
        messagebox.showerror("Error", "This field must be filled in.")
        return
    if appendUser(username, password):
        messagebox.showinfo("OK!", "You have successfully registered!")
        entry2.delete(0, END)
    else:
        messagebox.showerror("Error", "This user already exists.")
        entry2.delete(0, END)

def inputDelete():
    username = entry1.get()
    password = entry2.get()
    if not username or not password:
        messagebox.showerror("Error", "This field must be filled in.")
        return
    user_info = user_data(username, password)
    if user_info:
        confirm = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this user?")
        if confirm:
            if deleteUser(username, password):
                messagebox.showinfo("OK!", "User successfully deleted.")
                entry2.delete(0, END)
            else:
                messagebox.showerror("Error", "Failed to delete user.")
        else:
            messagebox.showinfo("Cancelled", "User deletion cancelled.")
    else:
        messagebox.showerror("Error", "User not found.")
        entry2.delete(0, END)

def adminDeleteAll():
    admin_password = simpledialog.askstring("Admin Password", "Enter admin password:",
                                            show='*')
    if admin_password:
        if deleteAllUsers(admin_password):
            messagebox.showinfo("OK!", "All users successfully deleted.")
        else:
            messagebox.showerror("Error", "Failed to delete users or incorrect admin password.")

def visible(event):
    current = entry2.config()['show'][-1]
    if current == '*':
        entry2.configure(show='')
        vis.config(text=f"◡",
                   font="Calibri 14 bold")
    else:
        entry2.configure(show='*')
        vis.config(text=f"👁",
                   font="Calibri 12")

app = Tk()
app["bg"] = "#FFFFFF"
app.iconbitmap('auto.ico')
app.title("Authorization")
app.geometry("300x400")
app.resizable(False, False)
app.geometry("+820+300")
setup_admin()  # Initialize the admin table
img = PhotoImage(file="user.png")
b = Label(image=img,
          background="#FFFFFF")
b.image = img
b.pack(pady=10)

btn_style = ttk.Style()
btn_style.configure("Rounded.TButton",
                    background="#FFFFFF",
                    foreground="#000000",
                    font=("Calibri", 10),
                    relief="flat",
                    borderwidth=0,
                    focuscolor="#FFFFFF",
                    padding=6)

btn_login = Button(app,
                   text="Enter",
                   bg="#FFFFFF",
                   font=("Calibri", 10),
                   command=inputLogin,
                   relief="flat",
                   borderwidth=1)
btn_login.place(relx=0.25,
                rely=0.25,
                x=-5,
                y=200,
                width=160,
                height=35)

btn_register = Button(app,
                      text="Are you not with us yet?",
                      bg="#FFFFFF",
                      font=("Calibri", 10),
                      command=inputRegister,
                      relief="flat",
                      borderwidth=1)
btn_register.pack(side=BOTTOM,
                  pady=30)
Hovertip(btn_register,
         "To register, you need to enter\nlogin in the first field, and for the password - in the second field\n",
         hover_delay=70)

btn_delete = Button(app,
                    text="Delete User",
                    bg="#FFFFFF",
                    font=("Calibri", 10),
                    command=inputDelete,
                    relief="flat",
                    borderwidth=1)
btn_delete.place(relx=0.25,
                 rely=0.25,
                 x=-5,
                 y=150,
                 width=160,
                 height=35)

btn_delete_all = Button(app,
                        text="Delete All Users",
                        bg="#FFFFFF",
                        font=("Calibri", 10),
                        command=adminDeleteAll,
                        relief="flat",
                        borderwidth=1)
btn_delete_all.place(relx=0.25,
                     rely=0.25,
                     x=-5,
                     y=110,
                     width=160,
                     height=35)

label1 = ttk.Label(text="Login",
                   font=("Calibri", 11, "bold"),
                   background="#FFFFFF")
label1.place(x=69,
             y=67,
             width=150)
entry1 = ttk.Entry(app)
entry1.place(anchor=CENTER,
             relx=0.25,
             rely=0.25,
             x=70,
             y=0,
             width=150)

label2 = ttk.Label(text="Password",
                   font=("Calibri", 11, "bold"),
                   background="#FFFFFF")
label2.place(x=69,
             y=125,
             width=100)
entry2 = ttk.Entry(app,
                   show="*")
entry2.place(anchor=CENTER,
             relx=0.25,
             rely=0.25,
             x=70,
             y=60,
             width=150)

vis = ttk.Label(app,
                text=f"👁",
                background="#FFFFFF",
                font=("Calibri", 12))
vis.place(anchor=CENTER,
          relx=0.25,
          rely=0.25,
          x=160,
          y=60,
          width=24,
          height=24)
vis.bind("<Button-1>", visible)

mainloop()
