import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import sys
import os
import subprocess

# ASCII art for end screen
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
        if direct:
            self._open_countdown(end_dt)
        else:
            self.root.title("Countdown Timer")
            self.root.geometry("450x550")
            self.root.resizable(False, False)
            self.build_ui()
            self.reset_defaults()

    def build_ui(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Start tab
        self.start_tab = ttk.Frame(nb)
        nb.add(self.start_tab, text="Start")
        self.start_cal = Calendar(self.start_tab, date_pattern='MM/dd/yyyy')
        self.start_cal.pack(pady=10)
        self.start_time = self._build_time_select(self.start_tab)
        ttk.Button(self.start_tab, text="Apply Start", command=self.apply_start).pack(pady=5)
        # End tab
        self.end_tab = ttk.Frame(nb)
        nb.add(self.end_tab, text="End")
        self.end_cal = Calendar(self.end_tab, date_pattern='MM/dd/yyyy')
        self.end_cal.pack(pady=10)
        self.end_time = self._build_time_select(self.end_tab)
        ttk.Button(self.end_tab, text="Apply End", command=self.apply_end).pack(pady=5)
        # Summary tab
        self.summary_tab = ttk.Frame(nb)
        nb.add(self.summary_tab, text="Summary")
        self.lbl_start = ttk.Label(self.summary_tab, text="Start: N/A")
        self.lbl_start.pack(pady=5)
        self.lbl_end = ttk.Label(self.summary_tab, text="End: N/A")
        self.lbl_end.pack(pady=5)
        self.lbl_duration = ttk.Label(self.summary_tab, text="Duration: N/A")
        self.lbl_duration.pack(pady=5)
        self.btn_countdown = ttk.Button(
            self.summary_tab, text="Start Countdown", state=tk.DISABLED,
            command=self.launch_background_countdown
        )
        self.btn_countdown.pack(pady=20)

    def _build_time_select(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(pady=5)
        spin_h = ttk.Spinbox(frame, from_=1, to=12, width=4, format="%02.0f")
        spin_m = ttk.Spinbox(frame, from_=0, to=59, width=4, format="%02.0f")
        spin_s = ttk.Spinbox(frame, from_=0, to=59, width=4, format="%02.0f")
        combo = ttk.Combobox(frame, values=["AM", "PM"], width=4, state="readonly")
        for w in (spin_h, spin_m, spin_s, combo): w.pack(side=tk.LEFT, padx=5)
        return (spin_h, spin_m, spin_s, combo)

    def apply_start(self):
        try:
            self.start_dt = self._get_dt(self.start_cal, self.start_time)
            self.lbl_start.config(text="Start: " + self.start_dt.strftime("%m/%d/%Y %I:%M:%S %p"))
            self._update_summary()
        except ValueError as e:
            messagebox.showerror("Invalid start", str(e))

    def apply_end(self):
        try:
            self.end_dt = self._get_dt(self.end_cal, self.end_time)
            self.lbl_end.config(text="End: " + self.end_dt.strftime("%m/%d/%Y %I:%M:%S %p"))
            self._update_summary()
        except ValueError as e:
            messagebox.showerror("Invalid end", str(e))

    def _get_dt(self, cal, time_widgets):
        d = datetime.strptime(cal.get_date(), '%m/%d/%Y').date()
        h = int(time_widgets[0].get())
        m = int(time_widgets[1].get())
        s = int(time_widgets[2].get())
        ap = time_widgets[3].get()
        if ap not in ("AM", "PM"): raise ValueError("Choose AM or PM")
        h24 = h % 12 + (12 if ap == "PM" else 0)
        return datetime(d.year, d.month, d.day, h24, m, s)

    def _update_summary(self):
        if hasattr(self, 'start_dt') and hasattr(self, 'end_dt'):
            delta = self.end_dt - self.start_dt
            if delta.total_seconds() > 0:
                days, rem = divmod(int(delta.total_seconds()), 86400)
                hrs, rem = divmod(rem,3600)
                mins, secs = divmod(rem,60)
                txt = f"{days}D {hrs:02d}:{mins:02d}:{secs:02d}"  # uppercase D
                self.lbl_duration.config(text="Duration: " + txt)
                self.btn_countdown.config(state=tk.NORMAL)
            else:
                self.lbl_duration.config(text="Duration: Invalid")
                self.btn_countdown.config(state=tk.DISABLED)

    def reset_defaults(self):
        now = datetime.now(); later = now + timedelta(minutes=5)
        self.start_cal.selection_set(now.date()); self.end_cal.selection_set(later.date())
        for spin, dt in ((self.start_time, now),(self.end_time, later)):
            h = dt.hour % 12 or 12; am = "PM" if dt.hour>=12 else "AM"
            spin[0].set(f"{h:02d}"); spin[1].set(f"{dt.minute:02d}")
            spin[2].set(f"{dt.second:02d}"); spin[3].set(am)

    def launch_background_countdown(self):
        exe = sys.executable
        if os.name=='nt' and exe.lower().endswith('python.exe'):
            exe = exe[:-10] + 'pythonw.exe'
        args = [exe, __file__, '--background', self.start_dt.isoformat(), self.end_dt.isoformat()]
        kwargs = {};
        if os.name=='nt': kwargs['creationflags'] = subprocess.DETACHED_PROCESS
        subprocess.Popen(args, close_fds=True, **kwargs); sys.exit(0)

    def _open_countdown(self, end_time):
        self.root.withdraw()
        total = (end_time - datetime.now()).total_seconds()
        if total <= 0:
            msg_win = tk.Toplevel(); msg_win.title("CountDown")
            ttk.Label(msg_win, text="Countdown already ended.", font=(None, 18)).pack(padx=20, pady=20)
            ttk.Button(msg_win, text="OK", command=lambda: sys.exit(0)).pack(pady=10)
            return
        win = tk.Toplevel(); win.title("Time Left")
        lbl = ttk.Label(win, text="", font=(None, 24)); lbl.pack(pady=20)
        pb = ttk.Progressbar(win, orient="horizontal", length=400, mode="determinate"); pb.pack(pady=10)
        pb['maximum'] = total; self._update_ct(win, lbl, pb, end_time, total)
        win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0)); win.mainloop()

    def _update_ct(self, win, lbl, pb, end_time, total):
        rem = (end_time - datetime.now()).total_seconds()
        if rem <= 0:
            win.withdraw()
            end_win = tk.Toplevel(); end_win.title("Time's Up!")
            lbl_end = tk.Label(end_win, text=END_ART, font=("Courier", 14), justify=tk.CENTER)
            lbl_end.pack(padx=20, pady=20)
            ttk.Button(end_win, text="Close", command=lambda: sys.exit(0)).pack(pady=10)
            return
        days, rem_s = divmod(int(rem),86400)
        h, rem_s = divmod(rem_s,3600); m, s = divmod(rem_s,60)
        lbl.config(text=f"{days}D {h:02d}:{m:02d}:{s:02d}")  # uppercase D
        pb['value'] = total - rem; win.after(1000, lambda: self._update_ct(win, lbl, pb, end_time, total))

if __name__ == '__main__':
    if '--background' in sys.argv:
        idx = sys.argv.index('--background')
        end_iso = sys.argv[idx+2]
        try: end_dt = datetime.fromisoformat(end_iso)
        except: sys.exit(1)
        root = tk.Tk(); CountdownApp(root, direct=True, end_dt=end_dt)
    else:
        root = tk.Tk(); CountdownApp(root); root.mainloop()
