import sys
import tkinter as tk
from tkinter import messagebox
from pywebostv.connection import WebOSClient
from pywebostv.controls import InputControl, MediaControl

class TVRemoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LG WebOS Remote")
        self.root.geometry("360x700")
        self.root.configure(bg="#000000")
        
        self.client = None
        self.inp = None
        self.audio = None
        
        self.main_container = tk.Frame(self.root, bg="#000000")
        self.main_container.pack(fill="both", expand=True)
        
        self.show_connection_screen()

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_connection_screen(self):
        self.clear_screen()
        
        tk.Label(self.main_container, text="Connect to TV", font=("Arial", 24, "bold"), 
                 bg="#000000", fg="#ffffff").pack(pady=(100, 20))

        ip_frame = tk.Frame(self.main_container, bg="#000000")
        ip_frame.pack(pady=10)
        
        self.ip_entry = tk.Entry(ip_frame, font=("Arial", 14), bg="#222222", fg="#ffffff", 
                                 insertbackground="white", bd=0, width=15)
        self.ip_entry.insert(0, "192.168.1.147")
        self.ip_entry.grid(row=0, column=0, padx=5, ipady=8)
        
        tk.Button(ip_frame, text="X", command=lambda: self.ip_entry.delete(0, tk.END),
                  bg="#440000", fg="white", font=("Arial", 12, "bold"), bd=0).grid(row=0, column=1, padx=2)

        tk.Button(self.main_container, text="CONNECT", command=self.connect_to_tv,
                  bg="#005500", fg="white", font=("Arial", 12, "bold"), 
                  width=20, height=2, bd=0).pack(pady=30)

    def show_remote_screen(self):
        self.clear_screen()
        
        tk.Label(self.main_container, text="LG Remote", font=("Arial", 18), 
                 bg="#000000", fg="#ffffff").pack(pady=10)

        nav_frame = tk.Frame(self.main_container, bg="#000000")
        nav_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 10, "bold"), "width": 8, "height": 2, 
                     "bg": "#1a1a1a", "fg": "#ffffff", "bd": 0}

        tk.Button(nav_frame, text="UP", command=lambda: self.safe_call("up"), **btn_style).grid(row=0, column=1, pady=5)
        tk.Button(nav_frame, text="LEFT", command=lambda: self.safe_call("left"), **btn_style).grid(row=1, column=0)
        tk.Button(nav_frame, text="RIGHT", command=lambda: self.safe_call("right"), **btn_style).grid(row=1, column=2)
        tk.Button(nav_frame, text="DOWN", command=lambda: self.safe_call("down"), **btn_style).grid(row=2, column=1, pady=5)

        self.mouse_pad = tk.Canvas(self.main_container, width=300, height=180, bg="#111111", 
                                   highlightthickness=1, highlightbackground="#333333")
        self.mouse_pad.pack(pady=10)
        self.mouse_pad.bind("<Button-1>", self.on_pad_press)
        self.mouse_pad.bind("<B1-Motion>", self.on_pad_drag)
        self.mouse_pad.bind("<ButtonRelease-1>", self.on_pad_release)

        ctrl_frame = tk.Frame(self.main_container, bg="#000000")
        ctrl_frame.pack(pady=10)
        tk.Button(ctrl_frame, text="HOME", command=lambda: self.safe_call("home"), **btn_style).grid(row=0, column=0, padx=5)
        tk.Button(ctrl_frame, text="BACK", command=lambda: self.safe_call("back"), **btn_style).grid(row=0, column=1, padx=5)
        
        tk.Button(self.main_container, text="Disconnect", command=self.show_connection_screen,
                  bg="#333333", fg="white", font=("Arial", 10), bd=0).pack(side="bottom", pady=20)

    def connect_to_tv(self):
        ip = self.ip_entry.get()
        try:
            self.client = WebOSClient(ip, secure=True)
            self.client.connect()
            store = {}
            for status in self.client.register(store):
                if status == WebOSClient.PROMPTED:
                    messagebox.showinfo("Pairing", "Please accept the prompt on your TV!")
                elif status == WebOSClient.REGISTERED:
                    self.inp = InputControl(self.client)
                    self.audio = MediaControl(self.client)
                    self.inp.connect_input()
                    self.show_remote_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def safe_call(self, cmd):
        if self.inp:
            try: getattr(self.inp, cmd)()
            except: pass

    def on_pad_press(self, event):
        self.last_x, self.last_y = event.x, event.y
        self.dragged = False

    def on_pad_drag(self, event):
        if self.inp:
            self.dragged = True
            dx, dy = event.x - self.last_x, event.y - self.last_y
            try: self.inp.move(dx * 2, dy * 2)
            except: pass
            self.last_x, self.last_y = event.x, event.y

    def on_pad_release(self, event):
        if self.inp and not self.dragged:
            try: self.inp.click()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = TVRemoteApp(root)
    root.mainloop()
