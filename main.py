import os
import sys
from PIL import Image
import subprocess
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
        self.rowconfigure(3, weight=1)
        
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
        
        self.build_button = ctk.CTkButton(self, text="Build AppImage", font=("", 20), command=self.build_appimage)
        self.build_button.grid(row=3, columnspan=3, sticky="ew", padx=100, pady=20)

    def get_extra_dependencies(self):
        self.pre_extra_directory = ctk.filedialog.askdirectory(title="Extra dependency path selection")
        if not self.pre_extra_directory:
            return

        if os.path.exists(self.pre_extra_directory):
            self.extra_optional_entry_var.set(self.extra_optional_entry_var.get() + self.pre_extra_directory)
        else:
            err_msg(master=self, text="Error: Invalid path")
            return

    def dir_has_appimagetool(self, dir):
        for file in os.listdir(dir):
            if file.startswith("appimagetool"):
                return True
        return False

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
        if self.dependencies_entry.get():
            return True
        else:
            return False
        
    def is_optional_dependent(self):
        if self.optional_data_entry.get():
            return True
        else:
            return False
        
    def has_icon(self):
        if self.icon_entry_var.get() != '':
            return True
        else:
            return False
    
    def has_extra_optional(self):
        if self.extra_optional_entry_var.get() != '':
            return True
        else:
            return False
    
    def has_name(self):
        if self.name_entry_var.get() != '':
            return True
        else:
            return False
    
    def get_imports(self, widget):
        # I hate list comprehension but oh well
        self.cleaned = [dep.strip() for dep in widget.get().split(",") if dep.strip()]
        return self.cleaned

    def build_appimage(self):
        fields = (self.directory_entry,)
        for field in fields:
            if not field.get():
                err_msg(master=self, text="Error: Please fill all required entries.")
                return
        
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
        self.file_name = os.path.basename(self.file_directory)
        
        self.venv_python = os.path.join(self.venv_directory, 'bin', 'python')
        self.venv_pip = os.path.join(self.venv_directory, 'bin', 'pip')
        
        self.venv_creation = [self.venv_python, '-m', 'venv', self.venv_directory]
        
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
        
        if self.is_optional_dependent():
            self.enabled_dependencies = set()
            for dependency in self.optional_dependencies:
                self.enabled_dependencies.add(dependency)
            
            for dependency in self.enabled_dependencies:
                self.nuitka_parts.append(f'--include-package-data={dependency}')
        
        if self.has_extra_optional():
            self.extra_deps = set()
            for dep in self.extra_optional_dependencies:
                self.extra_deps.add(dep)

            for dep in self.extra_deps:
                self.nuitka_parts.append(f'--include-data-files={dep}')
        
        if self.has_icon():
            self.nuitka_parts.append(f'--linux-onefile-icon={self.icon_directory}')
            self.nuitka_parts.append(f'--include-data-files={os.path.dirname(self.icon_directory)}={os.path.basename(self.icon_directory)}')
        
        if self.has_name():
            self.nuitka_parts.append(f'--output-filename="{self.name_entry_var.get()}"')
        else:
            self.processed_file_name = os.path.splitext(self.file_name)[0]
            self.nuitka_parts.append(f'--output-filename="{self.processed_file_name}"')
        
        self.nuitka_parts.append(self.file_name)
        
        print(self.nuitka_parts)
        
        # if not self.dir_has_appimagetool(self.project_directory) when creating subprocess
        self.appimagetool_link = 'https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage'
        self.download_appimagetool = ['wget', self.appimagetool_link]
        # os.chmod(file, os.stat(file).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        self.AppDir1 = ['mkdir', 'p', 'AppDir/usr/bin']
        self.AppDir2 = ['mkdir', 'p', f'AppDir/usr/share/icons/hicolor/{self.icon_size}/apps']
        self.AppDir3 = ['mkdir', 'p', 'AppDir/usr/share/applications']
        
        if self.has_name():
            self.dist_to_AppDir = ['cp', '-r', f'dist/{self.name_entry_var.get()}.dist/*', 'AppDir/usr/bin/']
        else:
            self.dist_to_AppDir = ['cp', '-r', f'dist/{self.processed_file_name}.dist/*', 'AppDir/usr/bin/']
            
        # Next up: Create a .desktop file inside AppDir with the following:
        # [Desktop Entry]
        # Type=Application
        # Name=AppName
        # Exec=AppName
        # Icon=AppName
        # Categories=Utility;
        # Comment=enter a comment
        # Terminal=false
        # StartupWMClass=AppName

if __name__ == "__main__":
    main()  
