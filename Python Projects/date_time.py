import tkinter as tk
from time import strftime

root = tk.Tk()
root.title("Digital Clock")
root.geometry("400x150")
root.configure(bg="black")

def update():
    current_time = strftime("%H:%M:%S")
    current_date = strftime("%A, %d %B %Y")
    time_label.config(text=current_time)
    date_label.config(text=current_date)
    time_label.after(1000, update)

time_label = tk.Label(root, font=("Arial", 30), bg="black", fg="cyan")
time_label.pack(anchor="center")

date_label = tk.Label(root, font=("Arial", 20), bg="black", fg="white")
date_label.pack(anchor="center")

update()

root.mainloop()