'''
MIT License

Copyright (c) 2024, Oregon Health & Science Univeristy

Contributor(s): Jason Ware

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Please consider citing!
doi.org/10.5281/zenodo.10511355
'''

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageDisplayApp:
    def __init__(self, root):
     			 			
        self.lockresize = False
        self.lockscroll = False

        self.root = root
        self.root.title("Transparency")

        ''' 
        This chunk allows the background of the window to be transparent by setting
        the window color to blue, and setting blue to be transparent. The same must be applied
        to the canvas (which holds the image) through wm_attributes
        '''
        self.root.config(bg="blue", bd=0, highlightthickness=0)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "blue")
        self.root.attributes("-alpha", 1)
        self.root.wm_attributes("-transparentcolor", "blue")

        self.helpMenuText = (
                            "________TRANSPARENCY_________\n"
                            "Press 1-9 to set transparency (1=10%, 9=90%)\n",
                            "Press '0' to reset transparency\n\n",
                            "_______IMAGE RESIZING________\n"
                            "Drag from the top left corner to resize image\n",
                            "Press 'l' to toggle resizing lock\n\n",
                            "_________SCROLLING__________\n"
                            "Scroll using mouse wheel\n",
                            "Press 'k' to toggle scroll lock\n\n"
                            "_________QUESTIONS?__________\n",
                            "visit ware-research on github\n"
                            "https://github.com/ware-research")

        menubar = tk.Menu(root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help", command=self.show_help)
        
        #Note the setting of background to the "transparent" blue
        self.canvas = tk.Canvas(root, bg="blue", bd=0, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.canvas.bind("<Configure>", self.resize_image)
        self.root.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.opacity_var = tk.DoubleVar()
        self.opacity_var.set(1.0)
        self.update_opacity()
        
        '''
        image must be opened at a tk image object. Calling self.open_image() outside of the 
        after() function results in image displayed as a non-tk image, which disables
        opacity and resizing functions
        '''
        self.root.after(500, self.open_image)

    def open_image(self):
     			 			
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])

        try:
            image = Image.open(file_path)
            self.image = image
            self.root.after(0, self.update_opacity)
        except Exception as e:
            print(f"Error loading image: {e}")

    def update_opacity(self):
     			 			
        opacity = self.opacity_var.get()
        if hasattr(self, "image"):
            image = self.image.copy()
            image.putalpha(int(255 * opacity))
            self.root.attributes("-alpha", opacity)
            photo_image = ImageTk.PhotoImage(image)
            self.canvas.config(width=image.width, height=image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)
            self.canvas.image = photo_image

            '''
            The resize_image function forces the transparent background to update and correct the
            image size. Calling resize_image after opacity change forces the transparency to 
            update, regardless of if the resize lock is on. The image size will not change. 
            '''
            self.resize_image(None) 

    def resize_image(self, event):
     			 			
        '''
        First, check if an image has been loaded, then check if resize has been locked.
        Then, if this resize is locked, it causes the image to be "resized" to the same size, 
        which forces the transparent background to update. 
        '''  
        if hasattr(self, "image"):
            image = self.image.copy()

            if self.lockresize == False:
                self.new_width = self.root.winfo_width()
                self.new_height = int(self.new_width / (image.width / image.height))

            new_width = self.new_width
            new_height = self.new_height

            self.canvas.config(scrollregion=(0, 0, new_width, new_height))

            image = image.resize((new_width, new_height))
            photo_image = ImageTk.PhotoImage(image)
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)
            self.canvas.image = photo_image

    def on_key_press(self, event):
     			 			
        key = event.char
        if key.isdigit() and 0 < int(key) <= 9:
            opacity = int(key) / 10.0
            self.opacity_var.set(opacity)
            self.update_opacity()
        elif key.isdigit() and int(key) == 0:
            opacity = 1
            self.opacity_var.set(opacity)
            self.update_opacity()
        elif key.lower() == "l":
            self.lockresize = not self.lockresize
        elif key.lower() == "k":
            self.lockscroll = not self.lockscroll

    def on_mouse_wheel(self, event):
     			 			
        if hasattr(self, "image") and not self.lockscroll:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_help(self):
     			 			
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")

        text_widget = tk.Text(help_window, wrap=tk.WORD, height=15, width=50)
        text_widget.pack(padx=10, pady=10)

        for line in self.helpMenuText:
            text_widget.insert(tk.END, line)

        text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
     			 			
    root = tk.Tk()
    root.minsize(40, 40)
    app = ImageDisplayApp(root)
    root.mainloop()
