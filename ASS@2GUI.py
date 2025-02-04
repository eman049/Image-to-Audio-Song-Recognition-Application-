import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
from pydub import AudioSegment
import asyncio
from shazamio import Shazam
import webbrowser
import pyttsx3

class ImageToSongRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image to Song Recognition")
        
        self.image_path = None
        
        self.create_widgets()
        
        # Initialize pyttsx3
        self.engine = pyttsx3.init()
        
    def create_widgets(self):
        # Set background image
        self.master.configure(bg="grey")

        # Add heading
        heading_label = tk.Label(self.master, text="IMAGE TO AUDIO SONG RECOGNITION APP", font=("Arial", 16, "bold"), fg="blue", bg="lightgrey")
        heading_label.pack(pady=15)

        # Left side: Select Image button
        self.select_image_button = tk.Button(self.master, text="Select Image", command=self.select_image, bg="blue", fg="white")
        self.select_image_button.pack(side=tk.LEFT, padx=40, pady=5)

        # Right side: Convert to MP3 button
        self.convert_button = tk.Button(self.master, text="Convert to MP3", command=self.convert_to_mp3, bg="green", fg="white")
        self.convert_button.pack(side=tk.LEFT, padx=40, pady=5)

        # New line: Recognize Song button
        self.recognize_button = tk.Button(self.master, text="Recognize Song", command=self.recognize_song, bg="orange", fg="black")
        self.recognize_button.pack(side=tk.RIGHT, padx=40, pady=5)

        # New line: Play Audio button
        self.play_button = tk.Button(self.master, text="Play Audio", command=self.play_audio, bg="red", fg="white")
        self.play_button.pack(side=tk.RIGHT, padx=40, pady=5)

        # New line: Read Info button
        self.read_button = tk.Button(self.master, text="Read Info", command=self.read_info, bg="purple", fg="white")
        self.read_button.pack(side=tk.BOTTOM, padx=20, pady=5)

        # Result label with wrapping
        self.result_label = tk.Label(self.master, text="", fg="blue", wraplength=500, justify="left", bg="lightgrey")
        self.result_label.pack(pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path
            self.show_image(file_path)

    def show_image(self, file_path):
        image = Image.open(file_path)
        image = image.resize((300, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        if hasattr(self, 'image_label'):
            self.image_label.config(image=photo)
            self.image_label.image = photo
        else:
            self.image_label = tk.Label(self.master, image=photo)
            self.image_label.pack()
            self.image_label.image = photo
    
    def convert_to_mp3(self):
        if self.image_path:
            image = Image.open(self.image_path)
            image = image.convert('L')
            image_data = np.array(image)
            normalized_data = (image_data / 255.0) * 2 - 1
            flattened_data = normalized_data.flatten()
            sample_rate = 44100
            duration = 40
            total_samples = sample_rate * duration
            
            if len(flattened_data) < total_samples:
                flattened_data = np.tile(flattened_data, int(np.ceil(total_samples / len(flattened_data))))
            audio_data = flattened_data[:total_samples]
            
            audio = AudioSegment((audio_data * 32767).astype(np.int16).tobytes(), 
                                 frame_rate=sample_rate,
                                 sample_width=2,
                                 channels=1)
            audio.export('sound.mp3', format='mp3')
            self.result_label.config(text="Image converted to MP3 successfully!", fg="green")
        else:
            self.result_label.config(text="Please select an image first.", fg="red")
    
    async def recognize_song_async(self, file_path):
        shazam = Shazam()
        result = await shazam.recognize(file_path)
        return result
    
    def recognize_song(self):
        if self.image_path:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.recognize_song_async('sound.mp3'))
            
            track_info = result.get('track', {})
            title = track_info.get('title', 'Unknown')
            artist = track_info.get('subtitle', 'Unknown')
            album = track_info.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown')
            release_date = track_info.get('sections', [{}])[0].get('metadata', [{}])[2].get('text', 'Unknown')
            coverart = track_info.get('images', {}).get('coverart', 'No cover art available')
            
            self.result_label.config(text=f"Title: {title}\n"
                                           f"Artist: {artist}\n"
                                           f"Album: {album}\n"
                                           f"Release Date: {release_date}\n"
                                           f"Cover Art: {coverart}", fg="black")
        else:
            self.result_label.config(text="Please select an image and convert it to MP3 first.", fg="red")
    
    def play_audio(self):
        webbrowser.open('sound.mp3')
        
    def read_info(self):
        info_text = self.result_label.cget("text")
        self.engine.say(info_text)
        self.engine.runAndWait()

def main():
    root = tk.Tk()
    app = ImageToSongRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
