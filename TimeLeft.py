import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import sys
import os
import subprocess

END_ART = """
███████╗███╗   ██╗██████╗
██╔════╝████╗  ██║██╔══██╗
█████╗  ██╔██╗ ██║██║  ██║
██╔══╝  ██║╚██╗██║██║  ██║
███████╗██║ ╚████║██████╔╝
╚══════╝╚═╝  ╚═══╝╚═════╝
"""

class CountdownApp:
    def __init__(self, root, direct=False, end_dt=None):
        self.root = root
        self.direct = direct
        self.timer_description = "Countdown Running"
        if direct:
            self._open_countdown(end_dt)
        else:
            self.root.title("Countdown Timer")
            self.root.geometry("500x640")
            self.root.resizable(False, False)
            self._configure_styles()
            self.build_ui()
            self.reset_defaults()

    def _configure_styles(self):
        """Configure custom styles for a classic, clean look"""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('Custom.TNotebook', background='#f0f0f0')
        style.configure('Custom.TNotebook.Tab', padding=[12, 8])
        
        # Configure button styles
        style.configure('Action.TButton', padding=(10, 5))
        style.configure('Primary.TButton', padding=(15, 8))

    def build_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Countdown Timer", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Notebook with custom style
        nb = ttk.Notebook(main_frame, style='Custom.TNotebook')
        nb.pack(fill=tk.BOTH, expand=True)

        # Start Tab
        self.start_tab = ttk.Frame(nb, padding="15")
        nb.add(self.start_tab, text="Start Time")
        
        self.start_cal = Calendar(self.start_tab, date_pattern='MM/dd/yyyy',
                                 background='white', foreground='black',
                                 selectbackground='#0078d4')
        self.start_cal.pack(pady=(0, 15))
        
        self.start_time = self._build_time_select(self.start_tab, "Start Time:")
        
        # Description section with better layout
        desc_frame = ttk.LabelFrame(self.start_tab, text="Timer Description", padding="10")
        desc_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var, width=50)
        self.desc_entry.pack(fill=tk.X, pady=(5, 0))
        self.desc_entry.bind("<KeyRelease>", self.limit_description_words)
        
        desc_help = ttk.Label(desc_frame, text="Optional: Enter a description (max 100 words)", 
                             font=('Segoe UI', 8), foreground='gray')
        desc_help.pack(anchor=tk.W, pady=(2, 0))
        
        ttk.Button(self.start_tab, text="Apply Start Time", 
                  command=self.apply_start, style='Action.TButton').pack(pady=(6, 0))

        # End Tab
        self.end_tab = ttk.Frame(nb, padding="15")
        nb.add(self.end_tab, text="End Time")
        
        self.end_cal = Calendar(self.end_tab, date_pattern='MM/dd/yyyy',
                               background='white', foreground='black',
                               selectbackground='#0078d4')
        self.end_cal.pack(pady=(0, 15))
        
        self.end_time = self._build_time_select(self.end_tab, "End Time:")
        
        ttk.Button(self.end_tab, text="Apply End Time", 
                  command=self.apply_end, style='Action.TButton').pack(pady=(15, 0))

        # Summary Tab
        self.summary_tab = ttk.Frame(nb, padding="15")
        nb.add(self.summary_tab, text="Summary")
        
        # Summary information in a nice frame
        summary_frame = ttk.LabelFrame(self.summary_tab, text="Timer Settings", padding="15")
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_start = ttk.Label(summary_frame, text="Start: Not set", 
                                  font=('Segoe UI', 10))
        self.lbl_start.pack(anchor=tk.W, pady=2)
        
        self.lbl_end = ttk.Label(summary_frame, text="End: Not set", 
                                font=('Segoe UI', 10))
        self.lbl_end.pack(anchor=tk.W, pady=2)
        
        self.lbl_duration = ttk.Label(summary_frame, text="Duration: Not calculated", 
                                     font=('Segoe UI', 10, 'bold'))
        self.lbl_duration.pack(anchor=tk.W, pady=(5, 0))
        
        # Start countdown button - prominently placed
        button_frame = ttk.Frame(self.summary_tab)
        button_frame.pack(expand=True)
        
        self.btn_countdown = ttk.Button(
            button_frame, text="🚀 Start Countdown", state=tk.DISABLED,
            command=self.launch_background_countdown, style='Primary.TButton'
        )
        self.btn_countdown.pack(pady=20)

    def limit_description_words(self, event=None):
        words = self.desc_var.get().split()
        if len(words) > 100:
            self.desc_var.set(" ".join(words[:100]))

    def _build_time_select(self, parent, label_text):
        """Build time selection widgets with improved layout to fix AM/PM overflow"""
        time_frame = ttk.LabelFrame(parent, text=label_text, padding="10")
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create two rows for better organization
        time_row = ttk.Frame(time_frame)
        time_row.pack(pady=(0, 5))
        
        period_row = ttk.Frame(time_frame)
        period_row.pack()
        
        # First row: Hour, Minute, Second (more compact)
        ttk.Label(time_row, text="Time:", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        # Hour
        ttk.Label(time_row, text="H:").grid(row=0, column=1, padx=(0, 2), sticky=tk.W)
        spin_h = ttk.Spinbox(time_row, from_=1, to=12, width=4, format="%02.0f")
        spin_h.grid(row=0, column=2, padx=(0, 8))
        
        # Minute
        ttk.Label(time_row, text="M:").grid(row=0, column=3, padx=(0, 2), sticky=tk.W)
        spin_m = ttk.Spinbox(time_row, from_=0, to=59, width=4, format="%02.0f")
        spin_m.grid(row=0, column=4, padx=(0, 8))
        
        # Second
        ttk.Label(time_row, text="S:").grid(row=0, column=5, padx=(0, 2), sticky=tk.W)
        spin_s = ttk.Spinbox(time_row, from_=0, to=59, width=4, format="%02.0f")
        spin_s.grid(row=0, column=6)
        
        # Second row: AM/PM centered
        ttk.Label(period_row, text="Period:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        combo = ttk.Combobox(period_row, values=["AM", "PM"], width=6, state="readonly")
        combo.pack(side=tk.LEFT)
        
        # Add some helpful text
        help_text = ttk.Label(time_frame, text="Use 12-hour format (1-12)", 
                             font=('Segoe UI', 8), foreground='gray')
        help_text.pack(pady=(5, 0))
        
        return (spin_h, spin_m, spin_s, combo)

    def apply_start(self):
        try:
            self.start_dt = self._get_dt(self.start_cal, self.start_time)
            # Handle description - provide default if empty or too short
            desc = self.desc_var.get().strip()
            if not desc:
                self.timer_description = "Timer Complete!"
            elif len(desc.split()) < 2:
                self.timer_description = f"Timer: {desc}"
            else:
                self.timer_description = desc
                
            self.lbl_start.config(text="Start: " + self.start_dt.strftime("%m/%d/%Y %I:%M:%S %p"))
            self._update_summary()
        except ValueError as e:
            messagebox.showerror("Invalid Start Time", str(e))

    def apply_end(self):
        try:
            self.end_dt = self._get_dt(self.end_cal, self.end_time)
            self.lbl_end.config(text="End: " + self.end_dt.strftime("%m/%d/%Y %I:%M:%S %p"))
            self._update_summary()
        except ValueError as e:
            messagebox.showerror("Invalid End Time", str(e))

    def _get_dt(self, cal, time_widgets):
        d = datetime.strptime(cal.get_date(), '%m/%d/%Y').date()
        
        # Validate inputs before processing
        try:
            h = int(time_widgets[0].get())
            m = int(time_widgets[1].get())
            s = int(time_widgets[2].get())
        except ValueError:
            raise ValueError("Please enter valid numbers for hour, minute, and second")
            
        ap = time_widgets[3].get()
        if ap not in ("AM", "PM"): 
            raise ValueError("Please select AM or PM")
            
        # Validate ranges
        if not (1 <= h <= 12):
            raise ValueError("Hour must be between 1 and 12")
        if not (0 <= m <= 59):
            raise ValueError("Minutes must be between 0 and 59")
        if not (0 <= s <= 59):
            raise ValueError("Seconds must be between 0 and 59")
            
        h24 = h % 12 + (12 if ap == "PM" else 0)
        return datetime(d.year, d.month, d.day, h24, m, s)

    def _update_summary(self):
        if hasattr(self, 'start_dt') and hasattr(self, 'end_dt'):
            delta = self.end_dt - self.start_dt
            if delta.total_seconds() > 0:
                days, rem = divmod(int(delta.total_seconds()), 86400)
                hrs, rem = divmod(rem, 3600)
                mins, secs = divmod(rem, 60)
                txt = f"{days}D {hrs:02d}:{mins:02d}:{secs:02d}"
                self.lbl_duration.config(text="Duration: " + txt)
                self.btn_countdown.config(state=tk.NORMAL)
            else:
                self.lbl_duration.config(text="Duration: Invalid (End must be after Start)")
                self.btn_countdown.config(state=tk.DISABLED)

    def reset_defaults(self):
        now = datetime.now()
        later = now + timedelta(hours=1)  # Default to 1 hour instead of 5 minutes
        
        self.start_cal.selection_set(now.date())
        self.end_cal.selection_set(later.date())
        
        for spin, dt in ((self.start_time, now), (self.end_time, later)):
            h = dt.hour % 12 or 12
            am = "PM" if dt.hour >= 12 else "AM"
            spin[0].set(f"{h:02d}")
            spin[1].set(f"{dt.minute:02d}")
            spin[2].set(f"{dt.second:02d}")
            spin[3].set(am)

    def launch_background_countdown(self):
        exe = sys.executable
        if os.name == 'nt' and exe.lower().endswith('python.exe'):
            exe = exe[:-10] + 'pythonw.exe'
        desc = self.timer_description.replace('"', '\\"')
        args = [exe, __file__, '--background', self.start_dt.isoformat(), self.end_dt.isoformat(), desc]
        
        # Enhanced subprocess creation to completely hide console window
        kwargs = {
            'close_fds': True,
            'stdin': subprocess.DEVNULL,
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.DEVNULL
        }
        
        if os.name == 'nt':
            # Windows specific flags to hide console completely
            kwargs['creationflags'] = (
                subprocess.DETACHED_PROCESS | 
                subprocess.CREATE_NO_WINDOW |
                subprocess.CREATE_NEW_PROCESS_GROUP
            )
            # Additional flag to prevent console inheritance
            kwargs['startupinfo'] = subprocess.STARTUPINFO()
            kwargs['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'].wShowWindow = subprocess.SW_HIDE
        else:
            # Unix/Linux - detach from parent process
            kwargs['preexec_fn'] = os.setsid
        
        subprocess.Popen(args, **kwargs)
        sys.exit(0)

    def relaunch_main_app(self):
        exe = sys.executable
        args = [exe, __file__]
        
        # Same enhanced subprocess creation for consistency
        kwargs = {
            'close_fds': True,
            'stdin': subprocess.DEVNULL,
            'stdout': subprocess.DEVNULL,
            'stderr': subprocess.DEVNULL
        }
        
        if os.name == 'nt':
            kwargs['creationflags'] = (
                subprocess.DETACHED_PROCESS | 
                subprocess.CREATE_NO_WINDOW |
                subprocess.CREATE_NEW_PROCESS_GROUP
            )
            kwargs['startupinfo'] = subprocess.STARTUPINFO()
            kwargs['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'].wShowWindow = subprocess.SW_HIDE
        else:
            kwargs['preexec_fn'] = os.setsid
        
        subprocess.Popen(args, **kwargs)

    def _open_countdown(self, end_time):
        self.root.withdraw()
        total = (end_time - datetime.now()).total_seconds()
        
        if total <= 0:
            self._show_expired_message()
            return
            
        # Create countdown window with better design
        win = tk.Toplevel()
        win.title("Countdown Timer")
        win.geometry("600x400")
        win.resizable(False, False)
        
        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (600 // 2)
        y = (win.winfo_screenheight() // 2) - (400 // 2)
        win.geometry(f"600x400+{x}+{y}")
        
        # Main container
        main_container = ttk.Frame(win, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Description section
        desc_frame = ttk.LabelFrame(main_container, text="Timer Description", padding="15")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Handle description display better
        display_desc = self.timer_description if self.timer_description else "Countdown in progress..."
        
        desc_text = tk.Text(desc_frame, height=4, width=60, wrap=tk.WORD, 
                           font=("Segoe UI", 11), relief=tk.FLAT, bg='#f8f9fa')
        desc_text.insert(tk.END, display_desc)
        desc_text.config(state=tk.DISABLED)
        desc_text.pack(fill=tk.X)
        
        # Countdown display
        countdown_frame = ttk.Frame(main_container)
        countdown_frame.pack(expand=True, fill=tk.BOTH)
        
        lbl = ttk.Label(countdown_frame, text="", font=("Consolas", 28, "bold"), 
                       foreground="#2c3e50")
        lbl.pack(expand=True)
        
        # Progress bar
        pb = ttk.Progressbar(countdown_frame, orient="horizontal", length=500, 
                            mode="determinate", style="Accent.Horizontal.TProgressbar")
        pb.pack(pady=(0, 20))
        pb['maximum'] = total
        
        # Control buttons frame - better positioned at bottom
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # New Timer button - bigger and better positioned
        new_timer_btn = ttk.Button(controls_frame, text="➕ Create New Timer", 
                  command=self.relaunch_main_app, width=20)
        new_timer_btn.pack(side=tk.LEFT)
        
        # Close button
        ttk.Button(controls_frame, text="❌ Close Timer", 
                  command=lambda: sys.exit(0), width=15).pack(side=tk.RIGHT)
        
        self._update_ct(win, lbl, pb, end_time, total)
        win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        win.mainloop()

    def _show_expired_message(self):
        msg_win = tk.Toplevel()
        msg_win.title("Timer Expired")
        msg_win.geometry("300x150")
        msg_win.resizable(False, False)
        
        # Center the window
        msg_win.update_idletasks()
        x = (msg_win.winfo_screenwidth() // 2) - (300 // 2)
        y = (msg_win.winfo_screenheight() // 2) - (200 // 2)
        msg_win.geometry(f"300x200+{x}+{y}")
        
        ttk.Label(msg_win, text="⏰ Timer Already Expired", 
                 font=("Segoe UI", 14)).pack(pady=20)
        ttk.Label(msg_win, text="The countdown time has already passed.", 
                 font=("Segoe UI", 10)).pack(pady=(0, 15))
        ttk.Button(msg_win, text="OK", command=lambda: sys.exit(0)).pack()

    def _update_ct(self, win, lbl, pb, end_time, total):
        rem = (end_time - datetime.now()).total_seconds()
        if rem <= 0:
            self._show_completion_window(win)
            return
            
        days, rem_s = divmod(int(rem), 86400)
        h, rem_s = divmod(rem_s, 3600)
        m, s = divmod(rem_s, 60)
        
        # Better time formatting
        if days > 0:
            time_text = f"{days}D {h:02d}:{m:02d}:{s:02d}"
        else:
            time_text = f"{h:02d}:{m:02d}:{s:02d}"
            
        lbl.config(text=time_text)
        pb['value'] = total - rem
        win.after(1000, lambda: self._update_ct(win, lbl, pb, end_time, total))

    def _show_completion_window(self, parent_win):
        parent_win.withdraw()
        
        end_win = tk.Toplevel()
        end_win.title("🎉 Time's Up!")
        end_win.geometry("400x350")
        end_win.attributes('-topmost', True)
        end_win.grab_set()
        end_win.resizable(False, False)
        
        # Center the window
        end_win.update_idletasks()
        x = (end_win.winfo_screenwidth() // 2) - (400 // 2)
        y = (end_win.winfo_screenheight() // 2) - (350 // 2)
        end_win.geometry(f"400x350+{x}+{y}")
        
        main_frame = ttk.Frame(end_win, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="🎉 Countdown Complete! 🎉", 
                font=("Segoe UI", 16, "bold"), fg="#27ae60").pack(pady=(10, 5))
        
        # Show description if available
        if self.timer_description and self.timer_description != "Countdown Complete!":
            desc_frame = ttk.LabelFrame(main_frame, text="Timer Description", padding="10")
            desc_frame.pack(fill=tk.X, pady=(10, 15))
            tk.Label(desc_frame, text=self.timer_description, wraplength=350, 
                    font=("Segoe UI", 10)).pack()
        
        lbl_end = tk.Label(main_frame, text=END_ART, font=("Courier", 12), 
                          justify=tk.CENTER, fg="#2c3e50")
        lbl_end.pack(padx=20, pady=15)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="New Timer", 
                  command=self.relaunch_main_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=lambda: sys.exit(0)).pack(side=tk.LEFT, padx=5)

if __name__ == '__main__':
    if '--background' in sys.argv:
        idx = sys.argv.index('--background')
        start_iso = sys.argv[idx + 1]
        end_iso = sys.argv[idx + 2]
        description = " ".join(sys.argv[idx + 3:]) if len(sys.argv) > idx + 3 else "Countdown Running!"
        
        try:
            start_dt = datetime.fromisoformat(start_iso)
            end_dt = datetime.fromisoformat(end_iso)
        except:
            sys.exit(1)

        class QuickCountdown(CountdownApp):
            def __init__(self, root, end_dt, desc):
                self.timer_description = desc
                self.root = root
                self._open_countdown(end_dt)

        root = tk.Tk()
        QuickCountdown(root, end_dt, description)

    else:
        root = tk.Tk()
        CountdownApp(root)
        root.mainloop()
