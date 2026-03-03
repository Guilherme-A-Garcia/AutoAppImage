import os
import sys
import subprocess
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def main():
    app = Controller()
    app.root.mainloop()
    
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
        self.rowconfigure(3, weight=1)
        
        self.geometry("500x650")
        self.title("AutoAppImage")
        
        self.main_label = ctk.CTkLabel(self, text="AutoAppImage", font=("", 30))
        self.main_label.grid(row=0, columnspan=3, sticky="nsew", pady=10)
        
        self.main_label_separator = ctk.CTkFrame(self, height=1, fg_color="gray", bg_color="gray")
        self.main_label_separator.grid(row=1, columnspan=3, sticky="ew", pady=(0,5))
        
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.grid(row=2, columnspan=3, sticky="nsew")
        
        self.directory_label = ctk.CTkLabel(self.entry_frame, text="Enter your project directory:", font=("", 16))
        self.directory_label.pack(anchor="center", padx=20)
        
        self.directory_entry_var = ctk.StringVar(value='')
        self.directory_entry = ctk.CTkEntry(self.entry_frame, textvariable=self.directory_entry_var)
        self.directory_entry.pack(anchor="center", padx=30, fill='x')
        
        self.directory_search = ctk.CTkButton(self.entry_frame, text="🔎 Search directory", font=("", 15), command=self.get_directory)
        self.directory_search.pack(anchor="center", pady=(2,10))
        
        self.dependencies_label = ctk.CTkLabel(self.entry_frame, text="Enter your project's imports (separated by commas):", font=("", 16))
        self.dependencies_label.pack(anchor="center", padx=20)
        self.dependencies_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Leave empty if third-party dependencies aren't needed.", placeholder_text_color="gray")
        self.dependencies_entry.pack(anchor="center", padx=30, fill='x')

        self.build_button = ctk.CTkButton(self, text="Build AppImage", font=("", 20), command=self.build_appimage)
        self.build_button.grid(row=3, columnspan=3, sticky="ew", padx=100)

    def get_directory(self):
        self.new_directory = ctk.filedialog.askdirectory(title="Directory selection")
        if not self.new_directory:
            return
        
        if os.path.exists(self.new_directory):
            self.directory = self.new_directory
            self.directory_entry_var.set(self.directory)
        else:
            err_msg(master=self, text="Error: Invalid path.")
            return

    def is_dependent(self):
        if self.dependencies_entry.get():
            return True
        else:
            return False

    def get_imports(self):
        # I hate list comprehension but oh well
        self.cleaned = [dep.strip() for dep in self.dependencies_entry.get().split(",") if dep.strip()]
        return self.cleaned

    def build_appimage(self):
        fields = (self.directory_entry,)
        for field in fields:
            if not field.get():
                err_msg(master=self, text="Error: Please fill all required entries.")
                return
        
        self.project_directory = self.directory_entry.get().strip()  # CWD var <-----------
        if not os.path.exists(self.project_directory):
            err_msg(master=self, text="Error: The project directory you provided is invalid.")
            return

        if self.is_dependent():
            self.imports = self.get_imports()

        self.new_venv_name = 'build-venv'
        self.venv_directory = os.path.join(self.project_directory, self.new_venv_name)
        self.venv_creation = ['python', '-m', 'venv', self.venv_directory]

        if os.path.exists(self.new_venv_name):
            self.new_venv_name = 'appimage-build-venv'
            self.venv_creation[-1] = self.new_venv_name
        
        self.venv_python = os.path.join(self.venv_directory, 'bin', 'python')
        self.venv_pip = os.path.join(self.venv_directory, 'bin', 'pip')
        
        self.install_libraries = [self.venv_pip, 'install', 'nuitka', *self.imports]
        
        self.nuitka_parts = [self.venv_python, '-m', 'nuitka', '--standalone', '--remove-output', '--output-dir=dist']
        
        if self.is_dependent():
            self.enabled_plugins = set()
            for dependency in self.imports:
                for plugin_name, plugin_value in self.nuitka_plugins.items():
                    if dependency in plugin_value:
                        self.enabled_plugins.add(plugin_name)
            
            for plugin in self.enabled_plugins:
                self.nuitka_parts.append(f'--enable-plugin={plugin}')
                
        # make optional enable-plugin field
        
# Current step: Build with a compiler as a standalone folder(in this case: nuitka):
# python3 -m nuitka --standalone --remove-output --enable-plugin=plugin-name --include-package-data=optional-data --include-package-data=customtkinter --linux-onefile-icon=optional-icon.png --include-data-files=icon.png=optional-icon.format=optional-icon.format --output-dir=dist --output-filename="AppName" app_name.py
# (--include-package-data is important for a bunch of libraries)
        
if __name__ == "__main__":
    main()  
