import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from datetime import datetime
import humanize
from PIL import Image, ImageTk
import mimetypes
import imghdr

class DuplicateFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder")
        self.root.geometry("1400x800")
        
        # Apply a theme
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
            
        self.folders = set()
        self.duplicate_groups = {}
        self.preview_size = (200, 200)
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for folder selection
        left_panel = ttk.Frame(self.main_container)
        self.main_container.add(left_panel, weight=1)
        
        # Folder Selection Frame
        folder_frame = ttk.LabelFrame(left_panel, text="Folder Selection", padding=10)
        folder_frame.pack(fill='x', padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(folder_frame)
        button_frame.pack(fill='x', pady=5)
        
        # Add Folder Button
        self.add_btn = ttk.Button(button_frame, text="Add Folder", command=self.add_folder)
        self.add_btn.pack(side='left', padx=5)
        
        # Clear Folders Button
        self.clear_btn = ttk.Button(button_frame, text="Clear Folders", command=self.clear_folders)
        self.clear_btn.pack(side='left', padx=5)
        
        # Folder List
        folder_list_frame = ttk.Frame(folder_frame)
        folder_list_frame.pack(fill='both', expand=True)
        
        # Scrollbar for folder list
        scrollbar = ttk.Scrollbar(folder_list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.folder_list = tk.Listbox(folder_list_frame, selectmode=tk.EXTENDED)
        self.folder_list.pack(fill='both', expand=True)
        self.folder_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.folder_list.yview)

        # Right side container
        right_container = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        self.main_container.add(right_container, weight=3)

        # Upper panel for duplicate groups
        upper_panel = ttk.LabelFrame(right_container, text="Duplicate Groups", padding=10)
        right_container.add(upper_panel, weight=1)

        # Groups Treeview
        columns = ('Group', 'Count', 'Size', 'Type')
        self.groups_tree = ttk.Treeview(upper_panel, columns=columns, show='headings')
        
        for col in columns:
            self.groups_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.groups_tree, c))
            self.groups_tree.column(col, width=100)

        groups_scrollbar = ttk.Scrollbar(upper_panel, orient=tk.VERTICAL, command=self.groups_tree.yview)
        self.groups_tree.configure(yscrollcommand=groups_scrollbar.set)
        
        self.groups_tree.grid(row=0, column=0, sticky='nsew')
        groups_scrollbar.grid(row=0, column=1, sticky='ns')
        
        upper_panel.grid_columnconfigure(0, weight=1)
        upper_panel.grid_rowconfigure(0, weight=1)

        # Lower panel for file details
        lower_panel = ttk.LabelFrame(right_container, text="File Details", padding=10)
        right_container.add(lower_panel, weight=2)

        # Create a horizontal PanedWindow for preview and details
        details_pane = ttk.PanedWindow(lower_panel, orient=tk.HORIZONTAL)
        details_pane.pack(fill=tk.BOTH, expand=True)

        # Left side - File list
        file_list_frame = ttk.Frame(details_pane)
        details_pane.add(file_list_frame, weight=2)

        # Detailed file list
        columns = ('Path', 'Size', 'Modified Date')
        self.file_tree = ttk.Treeview(file_list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.file_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.file_tree, c))
            self.file_tree.column(col, width=100)
        self.file_tree.column('Path', width=300)

        file_scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_scrollx = ttk.Scrollbar(file_list_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set, xscrollcommand=file_scrollx.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        file_scrollbar.grid(row=0, column=1, sticky='ns')
        file_scrollx.grid(row=1, column=0, sticky='ew')
        
        file_list_frame.grid_columnconfigure(0, weight=1)
        file_list_frame.grid_rowconfigure(0, weight=1)

        # Right side - Preview panel
        preview_frame = ttk.LabelFrame(details_pane, text="Preview", padding=10)
        details_pane.add(preview_frame, weight=1)

        # Preview widgets
        self.preview_label = ttk.Label(preview_frame, text="No preview available")
        self.preview_label.pack(expand=True)

        # File info
        self.info_text = tk.Text(preview_frame, height=8, width=30, wrap=tk.WORD)
        self.info_text.pack(fill='x', pady=5)

        # Action buttons
        button_frame = ttk.Frame(preview_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Open File", command=self.open_file).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Open Folder", command=self.open_folder).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_file).pack(side='left', padx=2)

        # Bottom frame for controls
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill='x', padx=5, pady=5)
        
        # Progress Bar
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(bottom_frame, textvariable=self.progress_var)
        self.progress_label.pack(side='left', pady=5)
        
        self.progress = ttk.Progressbar(bottom_frame, mode='determinate')
        self.progress.pack(side='left', fill='x', expand=True, padx=10, pady=5)
        
        # Scan Button
        self.scan_btn = ttk.Button(bottom_frame, text="Scan for Duplicates", command=self.start_scan)
        self.scan_btn.pack(side='right', pady=5)

        # Bind events
        self.groups_tree.bind('<<TreeviewSelect>>', self.on_group_select)
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
    def sort_treeview(self, tree, col):
        items = [(tree.set(item, col), item) for item in tree.get_children('')]
        
        # Convert size strings to numbers for proper sorting
        if col == 'Size':
            items = [(humanize.naturalsize(item[0]) if isinstance(item[0], (int, float)) else item[0], item[1]) 
                    for item in items]
            
        items.sort()
        for index, (val, item) in enumerate(items):
            tree.move(item, '', index)
            
    def on_group_select(self, event):
        selected_items = self.groups_tree.selection()
        if not selected_items:
            return
            
        # Clear file list
        self.file_tree.delete(*self.file_tree.get_children())
        
        # Get group number
        group_num = self.groups_tree.item(selected_items[0])['values'][0]
        
        # Display files for this group
        for file_path in self.duplicate_groups[group_num]:
            stats = os.stat(file_path)
            size = humanize.naturalsize(stats.st_size)
            modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            self.file_tree.insert('', 'end', values=(file_path, size, modified))

    def on_file_select(self, event):
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
            
        file_path = self.file_tree.item(selected_items[0])['values'][0]
        self.show_preview(file_path)

    def show_preview(self, file_path):
        # Clear previous preview
        self.preview_label.config(image='')
        self.info_text.delete(1.0, tk.END)
        
        # Show file info
        stats = os.stat(file_path)
        info = f"Path: {file_path}\n"
        info += f"Size: {humanize.naturalsize(stats.st_size)}\n"
        info += f"Modified: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
        info += f"Type: {mimetypes.guess_type(file_path)[0] or 'Unknown'}\n"
        
        self.info_text.insert(tk.END, info)
        
        # Try to show image preview
        try:
            if imghdr.what(file_path):
                img = Image.open(file_path)
                img.thumbnail(self.preview_size)
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo  # Keep a reference
            else:
                self.preview_label.config(text="No preview available")
        except:
            self.preview_label.config(text="Preview failed")

    def open_file(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        file_path = self.file_tree.item(selected_items[0])['values'][0]
        os.startfile(file_path)
        
    def open_folder(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        file_path = self.file_tree.item(selected_items[0])['values'][0]
        folder_path = os.path.dirname(file_path)
        os.startfile(folder_path)
        
    def delete_file(self):
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        file_path = self.file_tree.item(selected_items[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{file_path}"):
            try:
                os.remove(file_path)
                self.file_tree.delete(selected_items[0])
                messagebox.showinfo("Success", "File deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file:\n{str(e)}")
                
    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.folders:
            self.folders.add(folder)
            self.folder_list.insert(tk.END, folder)
            
    def clear_folders(self):
        self.folders.clear()
        self.folder_list.delete(0, tk.END)
        
    def calculate_file_hash(self, file_path, algorithm='md5'):
        hash_function = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as file:
                while chunk := file.read(8192):
                    hash_function.update(chunk)
            return hash_function.hexdigest()
        except IOError:
            return None
            
    def find_duplicates(self):
        hash_to_files = {}
        total_files = 0
        processed_files = 0
        
        # Count total files
        for folder in self.folders:
            for _, _, files in os.walk(folder):
                total_files += len(files)
        
        self.progress['maximum'] = total_files
        
        for folder in self.folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    processed_files += 1
                    self.progress_var.set(f"Processing file {processed_files} of {total_files}")
                    self.progress['value'] = processed_files
                    self.root.update_idletasks()
                    
                    file_path = os.path.join(root, file)
                    file_hash = self.calculate_file_hash(file_path)
                    
                    if file_hash:
                        if file_hash not in hash_to_files:
                            hash_to_files[file_hash] = []
                        hash_to_files[file_hash].append(file_path)
        
        return {h: files for h, files in hash_to_files.items() if len(files) > 1}
    
    def start_scan(self):
        if len(self.folders) < 1:
            messagebox.showwarning("Warning", "Please select at least one folder to scan.")
            return
            
        self.groups_tree.delete(*self.groups_tree.get_children())
        self.file_tree.delete(*self.file_tree.get_children())
        self.progress['value'] = 0
        self.scan_btn.state(['disabled'])
        
        def scan_thread():
            duplicates = self.find_duplicates()
            self.root.after(0, self.show_results, duplicates)
            
        Thread(target=scan_thread, daemon=True).start()
        
    def show_results(self, duplicates):
        self.scan_btn.state(['!disabled'])
        self.progress_var.set("")
        self.progress['value'] = 0
        
        # Clear previous results
        self.groups_tree.delete(*self.groups_tree.get_children())
        self.file_tree.delete(*self.file_tree.get_children())
        
        # Store duplicate groups for reference
        self.duplicate_groups = {}
        
        group_number = 1
        for files in duplicates.values():
            if len(files) > 1:  # Only show actual duplicates
                self.duplicate_groups[group_number] = files
                
                # Get group info
                sample_file = files[0]
                total_size = sum(os.path.getsize(f) for f in files)
                file_type = mimetypes.guess_type(sample_file)[0] or 'Unknown'
                
                # Add to groups tree
                self.groups_tree.insert('', 'end', values=(
                    group_number,
                    len(files),
                    humanize.naturalsize(total_size),
                    file_type
                ))
                
                group_number += 1
        
        if group_number == 1:
            messagebox.showinfo("Results", "No duplicate files were found.")

def main():
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()