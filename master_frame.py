import ctypes
import logging
import platform
import queue
import time
import tkinter as tk
import traceback
from tkinter import messagebox

import win32api
import win32con
import win32gui

from init import *
from libs.pymem import exception as pymem_exception
from memory_reader import reader, reader_utils
from modules import Options, Profile, StatsTracker, About, Drops, MFRunTimer, Grail
from utils import tk_dynamic as tkd, tk_utils, github_releases, other_utils, config


class MasterFrame(config.Config):
    def __init__(self):
        # Create root
        self.root = tkd.Tk()
        self.root.report_callback_exception = self.report_callback_exception

        # Build/load config file
        super().__init__()

        # Create error logger
        lh = logging.FileHandler(filename='mf_timer.log', mode='w', delay=True)
        logging.basicConfig(handlers=[lh],
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=getattr(logging, self.logging_level, 'WARNING'))

        # Check OS
        self.os_platform = platform.system()
        if self.os_platform != 'Windows':
            err = "MF Run Counter only runs on Windows"
            messagebox.showerror('OS Error', err)
            raise SystemError(err)

        # A trick to disable windows DPI scaling - the app doesn't work well with scaling, unfortunately
        if platform.release() == '10' and self.disable_scaling:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)

        # Initiate variables for memory reading
        self.is_user_admin = reader_utils.is_user_admin()
        self.advanced_error_thrown = False
        self.d2_reader = None

        # Create hotkey queue and initiate process for monitoring the queue
        self.queue = queue.Queue(maxsize=1)
        self.process_queue()

        # Check for version update
        #self.dl_count = github_releases.check_newest_version(release_repo) if self.check_for_new_version else ''

        # Load profile info
        self.make_profile_folder()
        self.profiles = [x[:-5] for x in os.listdir('Profiles') if x.endswith('.json') and x != 'grail.json']
        if self.active_profile not in self.profiles:
            self.active_profile = (self.profiles + [''])[0]
        self.profiles = self.sorted_profiles()

        # Modify root window
        self.title = 'MF run counter'
        self.root.title(self.title)
        self.clickable = True
        self.root.resizable(False, False)
        self.root.geometry('+%d+%d' % self.window_start_pos)
        self.root.config(borderwidth=2, height=365, width=240, relief='raised')
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.protocol("WM_DELETE_WINDOW", self.Quit)
        self.root.iconbitmap(media_path + 'icon.ico')
        # self.root.pack_propagate(False)
        self.root.bind("<Delete>", self.delete_selection)
        self.root.unbind_all('<Alt_L>')  # Pressing ALT_L paused UI updates when in focus

        # Build banner image
        d2banner = media_path + 'd2icon.png'
        img = tk.PhotoImage(master=self.root, file=d2banner)
        self.img_panel = tkd.ImgLabel(self.root, image=img, borderwidth=0)
        self.img_panel.pack()

        # Add buttons to main widget
        self.btn_frame = tkd.Frame(self.root)
        tkd.Button(self.btn_frame, text='Delete selection', command=self.delete_selection).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(2, 1), pady=1)
        tkd.Button(self.btn_frame, text='Archive session', command=self.ArchiveReset).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 1), pady=1)

        # Build tabs
        self.caret_frame = tkd.Frame(self.root)
        self.drops_frame = tkd.Frame(self.caret_frame)
        self.adv_stats_frame = tkd.Frame(self.caret_frame)

        self.tabcontrol = tkd.Notebook(self.root)
        self.tabcontrol.pack(expand=False, fill=tk.BOTH)
        self.profile_tab = Profile(self, parent=self.tabcontrol)
        self.timer_tab = MFRunTimer(self, parent=self.tabcontrol)
        self.drops_tab = Drops(self, parent=self.drops_frame)
        self.profile_tab.update_descriptive_statistics()  # FIXME: Total number of runs isn't read correctly unless we load descriptive statistics before packing the timer tab...
        self.options_tab = Options(self, self.timer_tab, self.drops_tab, parent=self.tabcontrol)
        self.grail_tab = Grail(self, parent=self.tabcontrol)
        self.about_tab = About(self, parent=self.tabcontrol)

        self.tabcontrol.add(self.timer_tab, text='Timer')
        self.tabcontrol.add(self.options_tab, text='Options')
        self.tabcontrol.add(self.profile_tab, text='Profile')
        self.tabcontrol.add(self.grail_tab, text='Grail')
        self.tabcontrol.add(self.about_tab, text='About')

        self.root.bind("<<NotebookTabChanged>>", lambda _: self.notebook_tab_change())
        self.toggle_tab_keys_global(initial_run=True)  # Register binds for changing tabs

        self.toggle_drops_frame(show=self.show_drops_frame)
        self.drops_caret = tkd.CaretButton(self.drops_frame, active=self.show_drops_frame, command=self.toggle_drops_frame, text='Drops', compound=tk.RIGHT, height=13)
        self.drops_caret.propagate(False)
        self.drops_caret.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=(2, 1), pady=(0, 1))

        tracker_is_active = self.advanced_tracker_open and self.automode == 2 and self.is_user_admin
        self.advanced_stats_tracker = StatsTracker(self, self.adv_stats_frame)
        self.advanced_stats_caret = tkd.CaretButton(self.adv_stats_frame, active=tracker_is_active, text='Advanced stats', compound=tk.RIGHT, height=13, command=self.toggle_advanced_stats_frame)
        self.advanced_stats_caret.propagate(False)
        self.advanced_stats_caret.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=(2, 1), pady=(0, 1))

        # Load save state and start autosave process
        active_state = self.load_state_file()
        self.LoadActiveState(active_state)
        self.root.after(30000, self._autosave_state)

        # Apply styling options
        self.theme.apply_theme_style()
        self.theme.update_colors()

        # Automode and advanced stats loop
        self.am_lab = tk.Text(self.root, height=1, width=13, wrap=tk.NONE, bg="black", font=('Segoe UI', 9), cursor='', borderwidth=0)
        self.am_lab.tag_configure("am", foreground="white", background="black")
        self.am_lab.tag_configure("on", foreground="lawn green", background="black")
        self.am_lab.tag_configure("off", foreground="red", background="black")
        self.am_lab.place(x=1, y=0.4)
        self.toggle_automode()
        self.toggle_advanced_stats_frame(show=tracker_is_active)

        # Used if "auto archive session" is activated
        self.profile_tab.auto_reset_session()

        # Start the program
        self.root.mainloop()

    def delete_selection(self, event=None):
        if self.timer_tab.m.curselection():
            self.timer_tab.delete_selected_run()
        elif self.root.focus_get().winfo_name() == 'droplist':
            self.drops_tab.delete_selected_drops()

    def load_memory_reader(self, show_err=True):
        err = None
        d2_game_open = reader_utils.process_exists(reader.D2_GAME_EXE)
        d2_se_open = reader_utils.process_exists(reader.D2_SE_EXE)
        if not self.is_user_admin:
            err = ('Elevated access rights', 'You must run the app as ADMIN to initialize memory reader for advanced automode.\n\nDisabling advanced automode.')
            self.d2_reader = None
        elif self.automode != 2:
            err = ('Automode option', 'Automode has not been set to "Advanced" - Will not initiate memory reader')
            self.d2_reader = None
        elif reader_utils.number_of_processes_with_names([reader.D2_GAME_EXE, reader.D2_SE_EXE], logging_level=self.logging_level) > 1:
            err = ('Number of processes', 'Several D2 processes have been opened, this bugs out the memory reader.\n\nDisabling advanced automode.')
            self.d2_reader = None
        elif not d2_game_open and not d2_se_open:
            self.d2_reader = None
        else:
            process_name = reader.D2_SE_EXE if d2_se_open else reader.D2_GAME_EXE
            try:
                self.d2_reader = reader.D2Reader(process_name=process_name)
                if self.d2_reader.dlls_loaded:
                    self.d2_reader.map_ptrs()
                    if not self.d2_reader.patch_supported:
                        err = ('D2 version error', 'Advanced automode currently only supports D2 patch versions 1.13c, 1.13d, 1.14b, 1.14c and 1.14d, your version is "%s".\n\nDisabling automode.' % self.d2_reader.d2_ver)
                else:
                    self.d2_reader = None

            except pymem_exception.CouldNotOpenProcess:
                err = ('Open process error', 'Memory reader failed to get handle of Game process, try restarting your computer.\n\nDisabling advanced automode')
                self.d2_reader = False
            except other_utils.pymem_err_list as e:
                logging.debug(f'Load reader error: {e}')
                self.d2_reader = None

        if err is not None and (not self.advanced_error_thrown or show_err):
            self.advanced_error_thrown = True
            messagebox.showerror(*err)
            logging.debug(err[1])
        else:
            self.advanced_error_thrown = False

    def sorted_profiles(self):
        def sort_key(x):
            file = f'Profiles/{x}.json'
            if not os.path.isfile(file):
                return float('inf')
            else:
                state = other_utils.json_load_err(file)
                return state.get('extra_data', dict()).get('Last update', os.stat(file).st_mtime)
        return sorted(self.profiles, key=sort_key, reverse=True)

    def toggle_automode(self):
        """
        Enables or disables automode. Shows a small label on top of the banner image with the text "Automode" when
        automode is activated. Takes an optional argument "char_name" which is used by the profile manager when changing
        between profiles, such that the automode loop listens to changes in the correct save file.
        """
        if self.automode:
            self.am_lab.configure(state=tk.NORMAL)
            self.am_lab.delete(1.0, tk.END)
            self.am_lab.insert(tk.END, "Automode: ", "am")
            self.am_lab.insert(tk.END, "ON", "on")
            self.am_lab.config(width=14)
            self.am_lab.configure(state=tk.DISABLED)
        else:
            self.am_lab.configure(state=tk.NORMAL)
            self.am_lab.delete(1.0, tk.END)
            self.am_lab.insert(tk.END, "Automode: ", "am")
            self.am_lab.insert(tk.END, "OFF", "off")
            self.am_lab.config(width=15)
            self.am_lab.configure(state=tk.DISABLED)
        self.timer_tab.toggle_automode()

    def toggle_tab_keys_global(self, initial_run=False):
        """
        Change whether tab switching keybind (ctrl-shift-pgup/pgdn) works only when the app has focus, or also when
        the app doesn't have focus. Added this feature, as some users might have this keybind natively bound to sth else
        """
        if self.tab_switch_keys_global:
            self.root.unbind_all('<Control-Shift-Next>')
            self.root.unbind_all('<Control-Shift-Prior>')
            self.options_tab.tab2.hk.register(['control', 'shift', 'next'], callback=lambda event: self.queue.put(self.tabcontrol.next_tab))
            self.options_tab.tab2.hk.register(['control', 'shift', 'prior'], callback=lambda event: self.queue.put(self.tabcontrol.prev_tab))
        else:
            if not initial_run:
                self.options_tab.tab2.hk.unregister(['control', 'shift', 'next'])
                self.options_tab.tab2.hk.unregister(['control', 'shift', 'prior'])
            self.root.bind_all('<Control-Shift-Next>', lambda event: self.tabcontrol.next_tab())
            self.root.bind_all('<Control-Shift-Prior>', lambda event: self.tabcontrol.prev_tab())

    def toggle_drops_frame(self, show=None):
        if show is None:
            show = self.drops_caret.active
        drops_height = 175
        if show:
            self.root.update()
            self.root.config(height=self.root.winfo_height()+drops_height)
            self.drops_tab.pack(pady=(0, 2))
        else:
            if hasattr(self, 'drops_tab') and self.drops_tab.winfo_ismapped():
                self.drops_tab.forget()
                self.root.config(height=self.root.winfo_height()-drops_height)
        self.show_drops_frame = show
        self.img_panel.focus_force()

    def toggle_advanced_stats_frame(self, show=None):
        if show is None:
            show = self.advanced_stats_caret.active
        if self.automode != 2:
            if show:
                messagebox.showerror('Error', 'You need to activate "Advanced automode" in Options->Automode to see advanced stats')
            show = False
            self.advanced_stats_caret.toggle_image(active=False)
        if (self.show_xp_tracker and not hasattr(self.advanced_stats_tracker, 'after_updater')) or self.advanced_stats_tracker.xp_lf1.winfo_ismapped():
            tracker_height = 311
        else:
            tracker_height = 132

        if self.show_xp_tracker and not self.advanced_stats_tracker.xp_lf1.winfo_ismapped():
            self.advanced_stats_tracker.xp_lf1.pack(expand=False, fill=tk.X, padx=1, pady=8)
            self.advanced_stats_tracker.xp_lf2.pack(expand=False, fill=tk.X, padx=1)
        if not self.show_xp_tracker and self.advanced_stats_tracker.xp_lf1.winfo_ismapped():
            self.advanced_stats_tracker.xp_lf1.forget()
            self.advanced_stats_tracker.xp_lf2.forget()

        if show:
            self.root.update()
            self.root.config(height=self.root.winfo_height()+tracker_height)
            self.advanced_stats_tracker.pack()
            self.advanced_stats_tracker.update_loop()
        else:
            if hasattr(self.advanced_stats_tracker, 'after_updater'):
                self.advanced_stats_tracker.forget()
                self.root.config(height=self.root.winfo_height()-tracker_height)
                self.advanced_stats_tracker.after_cancel(self.advanced_stats_tracker.after_updater)
                delattr(self.advanced_stats_tracker, 'after_updater')

    def process_queue(self):
        """
        The system hotkeys are registered in child threads, and thus tkinter needs a queue to process hotkey calls to
        achieve a threadsafe system
        """
        try:
            self.queue.get(False)()
        except queue.Empty:
            pass
        self.root.after(50, lambda: self.process_queue())

    def set_clickthrough(self):
        """
        Allow for making mouse clicks pass through the window, in case you want to use it as an overlay in your game
        Also makes the window transparent to visualize this effect.
        Calling the function again reverts the window to normal state.
        """
        hwnd = win32gui.FindWindow(None, self.title)
        if self.clickable:
            # Get window style and perform a 'bitwise or' operation to make the style layered and transparent, achieving
            # the clickthrough property
            l_ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            l_ex_style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, l_ex_style)

            # Set the window to be transparent and appear always on top
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 190, win32con.LWA_ALPHA)  # transparent
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickable = False
        else:
            # Calling the function again sets the extended style of the window to zero, reverting to a standard window
            win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 0)
            if not self.always_on_top:
                # Remove the always on top property again, in case always on top was set to false in options
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, self.root.winfo_x(), self.root.winfo_y(), 0, 0, 0)
            self.clickable = True

    def report_callback_exception(self, *args):
        """
        Handles errors occuring in the application, showing a messagebox with the occured error that user can send back
        for bug fixing
        """
        err = traceback.format_exception(*args)
        messagebox.showerror('Exception occured', 'Progress since last autosave is lost...\n\n' + ''.join(err))
        logging.exception(args)
        os._exit(0)

    def notebook_tab_change(self):
        """
        When tab is switched to profile, the descriptive statistics are updated.
        """
        x = self.tabcontrol.select()
        if x.endswith('profile'):
            self.profile_tab.update_descriptive_statistics()
        # A 'hack' to ensure that dropdown menus don't take focus immediately when you switch tabs by focusing the
        # banner image instead :)
        self.img_panel.focus_force()

    @staticmethod
    def make_profile_folder():
        if not os.path.isdir('Profiles'):
            os.makedirs('Profiles')

    def load_state_file(self):
        """
        Loads the save file for the active profile. Ensures directory exists, and if not it is created. Ensures the
        file exists, and if not an empty dictionary is returned.
        """
        self.make_profile_folder()
        file = f'Profiles/{self.active_profile}.json'
        if not os.path.isfile(file):
            state = dict()
        else:
            state = other_utils.json_load_err(file)
        return state

    def _autosave_state(self):
        """
        Function to run the autosave loop that saves the profile every 30 seconds
        """
        self.SaveActiveState()
        self.root.after(30000, self._autosave_state)

    def ResetSession(self):
        """
        Resets session for the timer module and drops from the drops module
        """
        self.timer_tab.reset_session()
        self.drops_tab.reset_session()
        self.advanced_stats_tracker.reset_session()

    def ArchiveReset(self, confirm_msg='Would you like to archive and reset session?', stamp_from_epoch=None):
        """
        If any laps or drops have been recorded, this function saves the current session to the profile archive, and
        resets all info in the active session. In case no runs/drops are recorded, the session timer is simply reset
        """
        if not self.timer_tab.laps and not self.drops_tab.drops:
            self.ResetSession()
            return

        xc = self.root.winfo_rootx() - self.root.winfo_width()//12
        yc = self.root.winfo_rooty() + self.root.winfo_height()//3
        if tk_utils.MessageBox(confirm_msg, b1='Yes', b2='No', coords=[xc, yc], master=self).returning:
            # Stop any active run and load current session info from timer and drop module.
            self.timer_tab.stop()
            active = self.timer_tab.save_state()
            self.profile_tab.tot_laps += len(active['laps'])
            active.update(self.drops_tab.save_state())

            # Update session dropdown for the profile
            if stamp_from_epoch is None:
                stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            else:
                stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stamp_from_epoch))
            self.profile_tab.available_archive.insert(2, stamp)
            self.profile_tab.archive_dropdown['values'] = self.profile_tab.available_archive

            # Update profile .json with the session
            state = self.load_state_file()
            state['active_state'] = dict()
            state[stamp] = active
            state.setdefault('extra_data', dict())['Last update'] = time.time()

            file = f'Profiles/{self.active_profile}.json'
            other_utils.atomic_json_dump(file, state)

            # When session has been successfully saved, the session is reset
            self.ResetSession()

    def LoadActiveState(self, state):
        """
        Loads the input state into the timer and drop modules. This is called at start-up when loading the profile .json
        and when you change the active profile in the profiles tab.
        """
        active_state = state.get('active_state', dict())
        self.timer_tab.load_from_state(active_state)
        self.drops_tab.load_from_state(active_state)

    def SaveActiveState(self):
        """
        Loads the .json for the profile, and replaces the 'active_state' key with the current active state, whereafter
        it is saved to file.
        """
        logging.debug('Saved active state')
        cache = self.load_state_file()
        timer_state = self.timer_tab.save_state()
        drops_state = self.drops_tab.save_state()
        if cache.get('active_state', dict()).get('laps', []) != timer_state.get('laps', []) or cache.get('active_state', dict()).get('drops', dict()) != drops_state.get('drops', dict()):
            is_updated = True
        else:
            is_updated = False
        cache['active_state'] = {**timer_state, **drops_state}
        if is_updated or 'Last update' not in cache['extra_data']:
            cache['extra_data']['Last update'] = time.time()
        file = f'Profiles/{self.active_profile}.json'
        other_utils.atomic_json_dump(file, cache)
        self.grail_tab.save_grail()

    def Quit(self):
        """
        Stops the active run, updates config, saves current state to profile .json, and finally exits the application
        """
        if self.timer_tab.is_running and not (self.timer_tab.automode_active and self.automode == 1):
            self.timer_tab.stop()
        self.SaveActiveState()
        self.update_config(self)
        sys.exit()
