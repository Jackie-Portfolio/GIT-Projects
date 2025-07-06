# Image Cartoonifier 
import cv2
import easygui
import numpy as np
import imageio
import sys
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import *
from PIL import ImageTk, Image

class ImageCartoonifier:
    def __init__(self):
        self.current_image = None
        self.cartoonified_image = None
        self.image_path = None
        self.setup_gui()
    
    def setup_gui(self):
        """Set up the main GUI window"""
        self.top = tk.Tk()
        self.top.geometry('400x400')
        self.top.title('Cartoonify Your Image!')
        self.top.configure(background='#CDCDCD')
        
        # Title label
        title_label = tk.Label(self.top, text="Image Cartoonifier", 
                              font=('calibri', 16, 'bold'),
                              background='#CDCDCD')
        title_label.pack(pady=20)
        
        # Upload button
        upload_btn = tk.Button(self.top, text="Select & Cartoonify Image", 
                              command=self.upload_and_cartoonify,
                              padx=20, pady=10,
                              background='#364156', foreground='white',
                              font=('calibri', 12, 'bold'))
        upload_btn.pack(pady=20)
        
        # Save button
        self.save_btn = tk.Button(self.top, text="Save Cartoon Image", 
                                 command=self.save_image,
                                 padx=20, pady=10,
                                 background='#364156', foreground='white',
                                 font=('calibri', 12, 'bold'),
                                 state='disabled')
        self.save_btn.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(self.top, text="Select an image to get started",
                                    font=('calibri', 10),
                                    background='#CDCDCD')
        self.status_label.pack(pady=10)
    
    def upload_and_cartoonify(self):
        """Open file dialog and process the selected image"""
        try:
            # Open file dialog
            self.image_path = filedialog.askopenfilename(
                title="Select an Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
            )
            
            if not self.image_path:
                return
            
            self.status_label.config(text="Processing image...")
            self.top.update()
            
            # Process the image
            self.cartoonify_image()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.status_label.config(text="Error processing image")
    
    def cartoonify_image(self):
        """Apply cartoon effect to the selected image"""
        try:
            # Read the image
            original_image = cv2.imread(self.image_path)
            if original_image is None:
                messagebox.showerror("Error", "Cannot read the selected image file")
                return
            
            # Convert BGR to RGB for proper color display
            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            
            # Resize for display (maintain aspect ratio)
            height, width = original_image.shape[:2]
            if width > 960 or height > 540:
                if width > height:
                    new_width = 960
                    new_height = int(height * (960 / width))
                else:
                    new_height = 540
                    new_width = int(width * (540 / height))
            else:
                new_width, new_height = width, height
            
            resized_original = cv2.resize(original_image, (new_width, new_height))
            
            # Step 1: Convert to grayscale
            gray_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
            resized_gray = cv2.resize(gray_image, (new_width, new_height))
            
            # Step 2: Apply median blur for smoothing
            smooth_gray = cv2.medianBlur(gray_image, 5)
            resized_smooth = cv2.resize(smooth_gray, (new_width, new_height))
            
            # Step 3: Create edge mask using adaptive threshold
            edges = cv2.adaptiveThreshold(smooth_gray, 255, 
                                        cv2.ADAPTIVE_THRESH_MEAN_C, 
                                        cv2.THRESH_BINARY, 9, 9)
            resized_edges = cv2.resize(edges, (new_width, new_height))
            
            # Step 4: Apply bilateral filter for smooth colors
            color_image = cv2.bilateralFilter(original_image, 9, 300, 300)
            resized_color = cv2.resize(color_image, (new_width, new_height))
            
            # Step 5: Combine edges with color image
            # Convert edges to 3-channel for masking
            edges_3channel = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            cartoon_image = cv2.bitwise_and(color_image, edges_3channel)
            resized_cartoon = cv2.resize(cartoon_image, (new_width, new_height))
            
            # Store the full-size cartoon image for saving
            self.cartoonified_image = cartoon_image
            
            # Display all transformations
            self.display_transformations([
                resized_original, resized_gray, resized_smooth, 
                resized_edges, resized_color, resized_cartoon
            ])
            
            # Enable save button
            self.save_btn.config(state='normal')
            self.status_label.config(text="Cartoonification complete! You can now save the image.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cartoonify image: {str(e)}")
            self.status_label.config(text="Error during cartoonification")
    
    def display_transformations(self, images):
        """Display all transformation steps"""
        titles = ['Original', 'Grayscale', 'Smooth Gray', 'Edges', 'Bilateral Filter', 'Cartoon']
        
        fig, axes = plt.subplots(3, 2, figsize=(12, 10), 
                                subplot_kw={'xticks': [], 'yticks': []},
                                gridspec_kw=dict(hspace=0.3, wspace=0.1))
        
        for i, (ax, img, title) in enumerate(zip(axes.flat, images, titles)):
            if len(img.shape) == 3:  # Color image
                ax.imshow(img)
            else:  # Grayscale image
                ax.imshow(img, cmap='gray')
            ax.set_title(title, fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def save_image(self):
        """Save the cartoonified image"""
        if self.cartoonified_image is None:
            messagebox.showwarning("Warning", "No cartoon image to save")
            return
        
        try:
            # Get save location
            save_path = filedialog.asksaveasfilename(
                title="Save Cartoon Image",
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), 
                          ("All files", "*.*")]
            )
            
            if not save_path:
                return
            
            # Convert RGB back to BGR for OpenCV
            bgr_image = cv2.cvtColor(self.cartoonified_image, cv2.COLOR_RGB2BGR)
            
            # Save the image
            success = cv2.imwrite(save_path, bgr_image)
            
            if success:
                messagebox.showinfo("Success", f"Cartoon image saved successfully!\nLocation: {save_path}")
                self.status_label.config(text="Image saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save the image")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.top.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = ImageCartoonifier()
    app.run()