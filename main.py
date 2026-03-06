import os
import sys
import stat
import platform
import threading
import subprocess
from PIL import Image
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def main():
    app = Controller()
    app.root.mainloop()

def dynamic_resolution(d_root, d_width, d_height):
    screen_height = d_root.winfo_screenheight()
    screen_width = d_root.winfo_screenwidth()
    x = (screen_width // 2) - (d_width // 2)
    y = (screen_height // 2) - (d_height // 2)
    d_root.geometry(f"{d_width}x{d_height}+{x}+{y}")

def err_msg(master, text):
    msg = CTkMessagebox(master=master, message=text, icon='cancel', title="Error")

def info_msg(master, text):
    msg = CTkMessagebox(master=master, message=text, icon='info', title="Info")

class Controller():
    def __init__(self):
        self.current_window = None
        self.root = ctk.CTk()
        self.root.withdraw()
        
        self.show_main_window()
        
    def close_current(self):
        if self.current_window is not None:
            self.current_window.destroy()
            self.current_window = None

    def show_main_window(self):
        self.close_current()
        self.current_window = MainWindow(self)

class MainWindow(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.file_directory = ''
        self.project_directory = ''
        self.icon_directory = ''
        self.imports = []
        self.nuitka_plugins = {'gevent': ('gevent',), 'glfw': ('glfw',), 'multiprocessing': ('multiprocessing',),
                        'numpy': ('numpy', 'scipy', 'pandas', 'matplotlib'), 'pmw-freezer': ('Pmw',), 'pyqt5': ('PyQt5',),
                        'pyside2': ('PySide2',), 'pyside6': ('PySide6',), 'pyzmq': ('pyzmq',),
                        'tensorflow': ('tensorflow',), 'tk-inter': ('tkinter', 'customtkinter', 'CTkMessagebox', '_tkinter'),}
        
        self.protocol("WM_DELETE_WINDOW", lambda: self.app.root.destroy())
        self.bind("<Button-1>", lambda e: e.widget.focus())
        
        self.resizable(False, False)
        self.columnconfigure((0,1,2), weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=6)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
        
        dynamic_resolution(self, 500, 650)
        self.title("AutoAppImage")
        
        self.main_label = ctk.CTkLabel(self, text="AutoAppImage", font=("", 30))
        self.main_label.grid(row=0, columnspan=3, sticky="nsew", pady=10)
        
        self.main_label_separator = ctk.CTkFrame(self, height=1, fg_color="gray", bg_color="gray")
        self.main_label_separator.grid(row=1, columnspan=3, sticky="ew", pady=(0,5))
        
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=2, columnspan=3, sticky="nsew")
        
        self.name_label = ctk.CTkLabel(self.entry_frame, text="Enter your project's name (optional):", font=("", 16))
        self.name_label.pack(anchor="center", padx=20)
        self.name_entry_var = ctk.StringVar(value='')
        self.name_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.name_entry_var)
        self.name_entry.pack(anchor="center", padx=30, fill='x', pady=(2,10))

        self.directory_label = ctk.CTkLabel(self.entry_frame, text="Enter your main .py file path:", font=("", 16))
        self.directory_label.pack(anchor="center", padx=20)
        self.directory_entry_var = ctk.StringVar(value='')
        self.directory_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.directory_entry_var)
        self.directory_entry.pack(anchor="center", padx=30, fill='x')
        
        self.directory_search = ctk.CTkButton(self.entry_frame, text="🔎 Search file", font=("", 15), command=self.get_directory)
        self.directory_search.pack(anchor="center", pady=(2,10))
        
        self.dependencies_label = ctk.CTkLabel(self.entry_frame, text="Enter your project's imports (separated by commas):", font=("", 16))
        self.dependencies_label.pack(anchor="center", padx=20)
        self.dependencies_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Leave this empty if third-party dependencies aren't needed", placeholder_text_color="gray")
        self.dependencies_entry.pack(anchor="center", padx=30, fill='x', pady=(2,10))
        
        self.optional_data_label = ctk.CTkLabel(self.entry_frame, text="Include optional package data (separated by commas):", font=("", 16))
        self.optional_data_label.pack(anchor="center", padx=20)
        self.optional_data_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Only include dependencies that need data detection (e.g.: customtkinter)", placeholder_text_color="gray")
        self.optional_data_entry.pack(anchor="center", padx=30, fill='x', pady=(2,10))
        
        self.icon_label = ctk.CTkLabel(self.entry_frame, text="Enter the project's icon path (optional, preferably .png):", font=("", 16))
        self.icon_label.pack(anchor="center", padx=20)
        self.icon_entry_var = ctk.StringVar(value='')
        self.icon_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.icon_entry_var)
        self.icon_entry.pack(anchor="center", padx=30, fill='x')
        
        self.icon_search = ctk.CTkButton(self.entry_frame, text="🔎 Search icon", font=("", 15), command=self.get_icon_directory)
        self.icon_search.pack(anchor="center", pady=(2,10))
        
        self.extra_optional_label = ctk.CTkLabel(self.entry_frame, text="Include package data path (optional, separated by commas):", font=("", 16))
        self.extra_optional_label.pack(anchor="center", padx=20)
        self.extra_optional_entry_var = ctk.StringVar(value='')
        self.extra_optional_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.extra_optional_entry_var)
        self.extra_optional_entry.pack(anchor="center", padx=30, fill='x')
        
        self.extra_optional_search = ctk.CTkButton(self.entry_frame, text="🔎 Search folder", font=("", 15), command=self.get_extra_dependencies)
        self.extra_optional_search.pack(anchor="center", pady=(2,10))
        
        self.build_button_separator = ctk.CTkFrame(self.entry_frame, height=1, fg_color="gray", bg_color="gray")
        self.build_button_separator.pack(fill='x', pady=(5,0))
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", height=5, corner_radius=10, mode="indeterminate", border_width=1)
        self.progress_bar.grid(row=3, columnspan=3, sticky='ew', padx=100, pady=10)
        self.disable_progress_bar()
        
        self.build_button = ctk.CTkButton(self, text="Build AppImage", font=("", 20), command=self.build_appimage)
        self.build_button.grid(row=4, columnspan=3, sticky="ew", padx=100, pady=(0,20))
        
        self.widgets = [self.name_entry, self.directory_entry, self.directory_search, self.dependencies_entry, self.optional_data_entry, self.icon_entry, self.icon_search, self.extra_optional_entry, self.extra_optional_search, self.build_button]
    
    def success_msg(self, master, option_1="No", option_2="Yes"):
        msg = CTkMessagebox(master=self, message="AppImage successfully generated!\nWould you like to clean leftovers?", icon='check', title='Success', option_1=option_1, option_2=option_2)
        if msg.get() == option_2:
            self.cleanup()
        return
            
        
    def enable_progress_bar(self):
        self.progress_bar.grid()
        self.progress_bar.start()
    
    def disable_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        
    def disable_widgets(self):
        for widget in self.widgets:
            widget.configure(state='disabled')
        
    def enable_widgets(self):
        for widget in self.widgets:
            widget.configure(state='normal')

    def get_extra_dependencies(self):
        self.pre_extra_directory = ctk.filedialog.askdirectory(title="Extra dependency path selection")
        if not self.pre_extra_directory:
            return

        if os.path.exists(self.pre_extra_directory):
            self.extra_optional_entry_var.set(self.extra_optional_entry_var.get() + self.pre_extra_directory)
        else:
            err_msg(master=self, text="Error: Invalid path")
            return
    
    def dir_has_appimagetool(self, directory):
        return any(file.startswith("appimagetool") for file in os.listdir(directory))
    
    def get_appimagetool_filename(self, directory):
        for file in os.listdir(directory):
            if file.startswith("appimagetool"):
                return file

    def get_directory(self):
        self.pre_directory = ctk.filedialog.askopenfilename(title="Main python file selection", filetypes=(("Python files", "*.py"), ("All files", "*.*")))
        if not self.pre_directory:
            return
        
        if os.path.exists(self.pre_directory):
            self.file_directory = self.pre_directory
            self.directory_entry_var.set(self.file_directory)
        else:
            err_msg(master=self, text="Error: Invalid path.")
            return

    def get_icon_directory(self):
        self.pre_icon_directory = ctk.filedialog.askopenfilename(title="Icon file selection", filetypes=(("PNG files", "*.png"), ("ICO files", "*.ico"), ("All files", "*")))
        if not self.pre_icon_directory:
            return
        
        if os.path.exists(self.pre_icon_directory):
            self.icon_directory = self.pre_icon_directory
            self.icon_entry_var.set(self.icon_directory)
        else:
            err_msg(master=self, text="Error: Invalid icon path.")
            return

    def is_dependent(self):
        return bool(self.dependencies_entry.get())
        
    def is_optional_dependent(self):
        return bool(self.optional_data_entry.get())
        
    def has_icon(self):
        return bool(self.icon_entry_var.get() != '')
    
    def has_extra_optional(self):
        return bool(self.extra_optional_entry_var.get() != '')
    
    def has_name(self):
        return bool(self.name_entry_var.get() != '')
    
    def get_imports(self, widget):
        # I hate list comprehension but oh well
        self.cleaned = [dep.strip() for dep in widget.get().split(",") if dep.strip()]
        return self.cleaned
    
    def cleanup(self):
        if self.project_directory != '':
            if os.path.exists(f'{self.project_directory}/AppDir/'):
                subprocess.run(['rm', '-rf', 'AppDir/'], cwd=self.project_directory)
            
            if os.path.exists(f'{self.project_directory}/build/'):
                subprocess.run(['rm', '-rf', 'build/'], cwd=self.project_directory)
                
            if os.path.exists(f'{self.project_directory}/dist/'):
                subprocess.run(['rm', '-rf', 'dist/'], cwd=self.project_directory)

    def create_desktop_file(self, project_name):
        if os.path.exists(f'{self.project_directory}/AppDir'):
            if not os.path.exists(f'{self.project_directory}/AppDir/{project_name}.desktop'):
                with open(f'{self.project_directory}/AppDir/{project_name}.desktop', 'w') as file:
                    file.write("#[Desktop Entry]\n")
                    file.write("Type=Application\n")
                    file.write(f"Name={project_name}\n")
                    file.write(f"Exec={project_name}\n")
                    file.write(f"Icon={project_name}\n")
                    file.write("Categories=Utility;\n")
                    # file.write("Comment=\n")
                    file.write("Terminal=false\n")
                    file.write(f"StartupWMClass={project_name}\n")
                    file.close()
            else:
                err_msg(master=self, text="Error: a .desktop file already exists! Aborting...")
                self.cleanup()
                return
        else:
            err_msg(master=self, text='Error: AppDir does not exist! Aborting...')
            self.cleanup()
            return

    def build_appimage(self):
        fields = (self.directory_entry,)
        for field in fields:
            if not field.get():
                err_msg(master=self, text="Error: Please fill all required entries.")
                return
        
        self.commands = {
            "venv_creation": [],
            "install_libraries": [],
            "nuitka_parts": [],
            "AppDir1": [],
            "AppDir2": [],
            "AppDir3": [],
            "dist_to_AppDir": [],
            "AppRun": [],
            "cp_icon": [],
            "cp_icon_base": [],
            "dir_icon": [],
            "download_appimagetool": [],
            "make_appimage": [],
        }
        
        self.temp_path = self.directory_entry_var.get().strip()
        self.project_directory = os.path.dirname(self.temp_path) # CWD var <-----------
        if not os.path.exists(self.project_directory):
            err_msg(master=self, text="Error: The project directory you provided is invalid.")
            return

        if self.is_dependent():
            self.imports = self.get_imports(self.dependencies_entry)
        
        if self.is_optional_dependent():
            self.optional_dependencies = self.get_imports(self.optional_data_entry)
        
        if self.has_extra_optional():
            self.extra_optional_dependencies = self.get_imports(self.extra_optional_entry_var)

        if self.has_icon():
            if not os.path.exists(self.icon_directory):
                err_msg(master=self, text="Error: Invalid icon path.")
                return
            else:
                self.icon_image = Image.open(self.icon_directory)
                self.icon_width, self.icon_height = self.icon_image.size
                self.icon_size = f'{self.icon_width}x{self.icon_height}'
        
        self.new_venv_name = 'build-venv'
        if os.path.exists(self.new_venv_name):
            self.new_venv_name = 'appimage-build-venv'
        
        self.venv_directory = os.path.join(self.project_directory, self.new_venv_name)
        self.file_directory = self.directory_entry_var.get().strip()
        self.file_name = os.path.basename(self.file_directory)
        
        self.venv_python = os.path.join(self.venv_directory, 'bin', 'python')
        self.venv_pip = os.path.join(self.venv_directory, 'bin', 'pip')
        
        self.commands["venv_creation"] = [sys.executable, '-m', 'venv', self.venv_directory]
        
        if self.has_name():
            self.final_name = self.name_entry_var.get()
        else:
            self.final_name = os.path.splitext(self.file_name)[0]
        
        if self.is_dependent():
            self.commands["install_libraries"] = [self.venv_pip, 'install', 'nuitka', *self.imports]
        
        self.commands["nuitka_parts"] = [self.venv_python, '-m', 'nuitka', '--standalone', '--remove-output', '--output-dir=dist']
        
        if self.is_dependent():
            self.enabled_plugins = set()
            for dependency in self.imports:
                for plugin_name, plugin_value in self.nuitka_plugins.items():
                    if dependency in plugin_value:
                        self.enabled_plugins.add(plugin_name)
            
            for plugin in self.enabled_plugins:
                self.commands["nuitka_parts"].append(f'--enable-plugin={plugin}')
        
        if self.is_optional_dependent():
            self.enabled_dependencies = set()
            for dependency in self.optional_dependencies:
                self.enabled_dependencies.add(dependency)
            
            for dependency in self.enabled_dependencies:
                self.commands["nuitka_parts"].append(f'--include-package-data={dependency}')
        
        if self.has_extra_optional():
            self.extra_deps = set()
            for dep in self.extra_optional_dependencies:
                self.extra_deps.add(dep)

            for dep in self.extra_deps:
                self.commands["nuitka_parts"].append(f'--include-data-files={dep}')
        
        if self.has_icon():
            self.commands["nuitka_parts"].append(f'--linux-onefile-icon={self.icon_directory}')
            self.commands["nuitka_parts"].append(f'--include-data-files={os.path.dirname(self.icon_directory)}={os.path.basename(self.icon_directory)}')
        
        self.commands["nuitka_parts"].append(f'--output-filename={self.final_name}')
        
        self.commands["nuitka_parts"].append(self.file_name)
        
        self.commands["AppDir1"] = ['mkdir', '-p', 'AppDir/usr/bin']
        if self.has_icon():
            self.commands["AppDir2"] = ['mkdir', '-p', f'AppDir/usr/share/icons/hicolor/{self.icon_size}/apps']
        else:
            self.commands["AppDir2"] = ['mkdir', '-p', f'AppDir/usr/share/icons/hicolor/256x256/apps']
        self.commands["AppDir3"] = ['mkdir', '-p', 'AppDir/usr/share/applications']
        
        self.commands["dist_to_AppDir"] = ['cp', '-r', f'dist/{self.final_name}.dist/*', 'AppDir/usr/bin/']
        self.commands["AppRun"] = ['ln', '-s', f'usr/bin/{self.final_name}', 'AppDir/AppRun']
        
        if self.has_icon():
            self.icon_name = os.path.splitext(os.path.basename(self.icon_directory))
            self.commands["cp_icon"] = ['cp', self.icon_directory, f'AppDir/usr/share/icons/hicolor/{self.icon_size}/apps/{self.final_name}{self.icon_name[1]}']
            self.commands["cp_icon_base"] = ['cp', self.icon_directory, f'AppDir/{self.final_name}{self.icon_name[1]}']
            self.commands["dir_icon"] = ['ln', '-s', f'AppDir/usr/share/icons/hicolor/{self.icon_size}/apps/{self.final_name}{self.icon_name[1]}', 'AppDir/.DirIcon']
        
        self.build_thread(commands=self.commands, directory=self.project_directory, processed_file_name=self.final_name)
        
    def build_thread(self, commands, directory, processed_file_name):
        
        def check_thread():
            if self.thread.is_alive():
                self.after(200, check_thread)
            else:
                self.enable_widgets()
                self.disable_progress_bar()
        
        self.thread = threading.Thread(target=self.build_subprocess, args=(commands, directory, processed_file_name), daemon=True)
        
        self.disable_widgets()
        self.enable_progress_bar()
        self.thread.start()
        
        check_thread()
    
    def build_subprocess(self, commands, directory, processed_file_name):
        self.final_name = processed_file_name
        
        self.arch = platform.machine()
        self.env = os.environ.copy()
        self.env["ARCH"] = self.arch
        
        if self.arch == 'x86_64':
            self.arch = 'x86_64'
        elif self.arch in ('aarch64', 'arm64'):
            self.arch = 'aarch64'
        elif self.arch in ('armv7l', 'armv6l'):
            self.arch = 'armhf'
        elif self.arch in ('i386', 'i686'):
            self.arch = 'i686'
        else:
            self.after(0, lambda: err_msg(master=self, text=f"Unsupported architecture for available AppImageTool binaries: {self.arch}.\nAborting..."))
            return self.cleanup()
            
        self.appimagetool_link = f'https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-{self.arch}.AppImage'
        
        commands["download_appimagetool"] = ['wget', self.appimagetool_link]
        
        self.cmd_order = [
            "venv_creation",
            "install_libraries",
            "nuitka_parts",
            "AppDir1",
            "AppDir2",
            "AppDir3",
            "dist_to_AppDir",
            "AppRun",
            "cp_icon",
            "cp_icon_base",
            "dir_icon",
            "download_appimagetool",
            "make_appimage"]
        
        for cmd in self.cmd_order:
            if cmd in commands and commands[cmd]:
                try:
                    if cmd == "dir_icon":
                        self.process = subprocess.run(commands[cmd], cwd=directory, check=True)
                        self.create_desktop_file(self.final_name)
                        
                    elif cmd == "download_appimagetool":
                        if not self.dir_has_appimagetool(directory=directory):
                            self.process = subprocess.run(commands[cmd], cwd=directory, check=True)
                            self.appimagetool = self.get_appimagetool_filename(directory=directory)
                            self.tool_path = os.path.join(directory, self.appimagetool)
                            os.chmod(self.tool_path, os.stat(self.tool_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        else:
                            self.appimagetool = self.get_appimagetool_filename(directory=directory)
                            self.tool_path = os.path.join(directory, self.appimagetool)
                            os.chmod(self.tool_path, os.stat(self.tool_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    
                    elif cmd == "make_appimage":
                        self.process = subprocess.run([self.appimagetool, 'AppDir', f'{self.final_name}-{self.arch}.AppImage'], cwd=directory, env=self.env, check=True)
                    
                    else:                    
                        self.process = subprocess.run(commands[cmd], cwd=directory, check=True)
                        
                except Exception as e:
                    self.after(0, lambda: err_msg(master=self, text=f'An error has occurred: {e}'))
                    self.cleanup()
                    return
                    
        if self.process.returncode == 0:
            self.after(0, lambda: self.success_msg(master=self))
        else:
            self.after(0, lambda: err_msg(master=self, text=f"The subprocess has failed.\nReturn code: {self.process.returncode}"))
            self.cleanup()
            return

if __name__ == "__main__":
    main()  
