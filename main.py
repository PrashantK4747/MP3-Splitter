import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# pydub is a required library: pip install pydub
from pydub import AudioSegment
from pydub.silence import split_on_silence

# --- Set ffmpeg path to local bin directory ---
from pydub.utils import which
FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "bin", "ffmpeg.exe")
AudioSegment.converter = FFMPEG_PATH if os.path.exists(FFMPEG_PATH) else which("ffmpeg")

# Import UI theme system
import ui_theme
from ui_theme import (
    PRIMARY_ORANGE, initialize_theme, AnimationManager, InteractiveButton, StatusBar,
    create_tooltip, add_hover_effect, get_waveform_colors,
    PRIMARY_BLUE, SECONDARY_RED, SUCCESS_COLOR, ERROR_COLOR,
    WARNING_COLOR, SECONDARY_GREEN, SPLIT_LINE_ACTIVE
)

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pygame

class MP3SplitterApp:
    """
    A desktop application for splitting MP3 files based on silence or manual points.
    Features:
    - Load and display MP3 waveform
    - Play, pause, and stop audio with a moving playhead
    - Auto split on silence or manual split points
    - Export split segments as a ZIP file
    - Responsive UI using Tkinter and matplotlib
    """
    def __init__(self, root):
        """Initialize the main window, UI elements, and state variables."""
        self.root = root
        self.root.title("MP3_Splitter")
        
        # CENTER THE WINDOW ON SCREEN
        self.center_window(1200, 800)
        
        self.root.resizable(True, True)  # Allow maximize and resizing
        
        # Make root window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialize modern theme and animation system
        self.style, self.anim_manager = ui_theme.initialize_theme(root)

        # --- Member variables to store paths and state ---
        self.source_file_path = tk.StringVar()

        # --- Main Frame with proper centering ---
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure main_frame for responsive layout
        main_frame.grid_rowconfigure(4, weight=1)  # Waveform row expands
        main_frame.grid_columnconfigure(1, weight=1)  # Middle column expands
        main_frame.grid_columnconfigure(2, weight=1)  # Entry column expands

        # --- UI Elements ---
        # Header with enhanced styling
        header_label = ttk.Label(main_frame, text="MP3_Splitter", style='Header.TLabel', font=("Helvetica", 32, "bold"), foreground=PRIMARY_ORANGE)
        header_label.grid(row=0, column=0, columnspan=4, pady=(0, 30))
        # Add subtle animation to header
        self.anim_manager.fade_in(header_label, duration=500)

        # 1. Source File Selection with enhanced styling
        ttk.Label(main_frame, text="Source MP3 File:", style='Subheader.TLabel').grid(row=1, column=0, sticky='w', pady=10)
        file_entry = ttk.Entry(main_frame, textvariable=self.source_file_path, width=60, state='readonly')
        file_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=10)
        
        browse_button = ttk.Button(main_frame, text="Browse...", command=self.select_source_file, style='Primary.TButton')
        browse_button.grid(row=1, column=3, sticky='w')
        create_tooltip(browse_button, "Select an MP3 file to split")

        # 2. Settings Frame (splitting parameters) with enhanced styling
        settings_frame = ttk.LabelFrame(main_frame, text="Splitting Parameters", padding=20)
        settings_frame.grid(row=3, column=0, columnspan=4, pady=30, sticky='ew')
        
        # Configure settings_frame columns
        settings_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(settings_frame, text="Min Silence Length (mm:ss):", style='Body.TLabel').grid(row=0, column=0, sticky='w', pady=10)
        self.min_silence_entry = ttk.Entry(settings_frame, width=15)
        self.min_silence_entry.insert(0, "00:00")  # Default 00 seconds
        self.min_silence_entry.grid(row=0, column=1, sticky='w', padx=10)
        create_tooltip(self.min_silence_entry, "Enter minimum silence length in mm:ss format")
        
        # Bind splitting to entry events for auto split
        self.min_silence_entry.bind('<FocusOut>', lambda e: self.auto_split_on_param_change())
        self.min_silence_entry.bind('<Return>', lambda e: self.auto_split_on_param_change())
        
        # Add Enter button for manual split with enhanced styling
        self.enter_split_button = ttk.Button(settings_frame, text="Split", command=self.add_manual_split_from_entry, style='Success.TButton')
        self.enter_split_button.grid(row=0, column=2, sticky='w', padx=10)
        create_tooltip(self.enter_split_button, "Add a split point at the specified time")
        
        # Add Refresh button for splitting parameters with enhanced styling
        self.refresh_split_param_button = ttk.Button(settings_frame, text="Refresh", command=self.refresh_split_parameters, style='Secondary.TButton')
        self.refresh_split_param_button.grid(row=0, column=3, sticky='w', padx=10)
        create_tooltip(self.refresh_split_param_button, "Reset all split parameters and points")

        # --- Waveform and Playback Frame ---
        waveform_frame = ttk.Frame(main_frame, style='Card.TFrame')
        waveform_frame.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=(20, 20))
        
        # Configure waveform_frame for expansion
        waveform_frame.grid_rowconfigure(0, weight=1)
        waveform_frame.grid_columnconfigure(0, weight=1)
        
        self.figure, self.ax = plt.subplots(figsize=(12, 4))  # Increased figure size
        self.ax.set_axis_off()
        self.canvas = FigureCanvasTkAgg(self.figure, master=waveform_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # Playback time label with enhanced styling
        self.time_label = ttk.Label(waveform_frame, text="00:00 / 00:00", style='Time.TLabel')
        self.time_label.grid(row=1, column=0, pady=(5, 0))
        
        # Playback controls with enhanced styling - centered
        controls_frame = ttk.Frame(waveform_frame)
        controls_frame.grid(row=2, column=0, pady=10)
        
        # Refresh button to clear split lines with enhanced styling
        self.refresh_button = ttk.Button(waveform_frame, text='Refresh', command=self.refresh_split_lines, style='Secondary.TButton')
        self.refresh_button.grid(row=3, column=0, pady=5)
        create_tooltip(self.refresh_button, "Clear all split lines and reset playback")
        
        # Playback buttons with enhanced styling
        self.play_button = ttk.Button(controls_frame, text='Play', command=self.play_audio, style='Primary.TButton')
        self.play_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.play_button, "Play or resume audio playback")
        
        self.pause_button = ttk.Button(controls_frame, text='Pause', command=self.pause_audio, style='Secondary.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.pause_button, "Pause audio playback")
        
        self.stop_button = ttk.Button(controls_frame, text='Stop', command=self.stop_audio, style='Danger.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.stop_button, "Stop audio playback")
        
        # Manual split button with enhanced styling
        self.manual_split_button = ttk.Button(waveform_frame, text='Split (Manual)', command=self.add_manual_splits, style='Success.TButton')
        self.manual_split_button.grid(row=4, column=0, pady=5)
        create_tooltip(self.manual_split_button, "Add manual split points by clicking on the waveform")
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        self.is_paused = False
        self.current_audio_path = None
        self.audio_duration_ms = 0
        self.split_points = []  # Store split points in ms
        self.split_lines = []   # Store matplotlib line objects
        self.canvas.mpl_connect('button_press_event', self.on_waveform_click)
        self.playhead_line = None  # For moving playhead

        # --- Right-side panel for timestamps ---
        right_panel = ttk.Frame(main_frame, style='Panel.TFrame')
        right_panel.grid(row=0, column=4, rowspan=9, sticky='ns', padx=(30,0), pady=10)
        
        ttk.Label(right_panel, text="Split Segment", style='Header.TLabel').pack(anchor='n', pady=(0,15))
        
        self.timestamp_tree = ttk.Treeview(right_panel, columns=("track", "start", "end"), show="headings", height=30)
        self.timestamp_tree.heading("track", text="Track #")
        self.timestamp_tree.heading("start", text="Start Time")
        self.timestamp_tree.heading("end", text="End Time")
        self.timestamp_tree.column("track", width=70, anchor='center')
        self.timestamp_tree.column("start", width=90, anchor='center')
        self.timestamp_tree.column("end", width=90, anchor='center')
        self.timestamp_tree.pack(fill=tk.BOTH, expand=True)
        
        # Download as ZIP button with enhanced styling
        self.download_zip_button = ttk.Button(right_panel, text="Download as ZIP", command=self.download_segments_zip, style='Primary.TButton')
        self.download_zip_button.pack(side=tk.BOTTOM, pady=15)
        create_tooltip(self.download_zip_button, "Export all split segments as a ZIP file")

        # 4. Enhanced Status Bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.grid(row=6, column=0, columnspan=4, sticky='ew', pady=(15, 0))
        
        # 5. Progress Bar (integrated into status bar)
        self.progress_bar = self.status_bar.progress

    def center_window(self, width, height):
        """Center the window on the screen."""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position coordinates
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set window geometry
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def select_source_file(self):
        """Open a dialog to select the source MP3 file and update the waveform and split segments."""
        file_path = filedialog.askopenfilename(
            title="Select MP3 File",
            filetypes=(("MP3 Files", "*.mp3"), ("All files", "*.*"))
        )
        if file_path:
            self.source_file_path.set(file_path)
            self.status_bar.update_status(f"Selected file: {os.path.basename(file_path)}", 'success')
            self.plot_waveform(file_path)
            self.current_audio_path = file_path
            self.auto_split_on_param_change()
            # Add success animation
            self.anim_manager.pulse_button(self.play_button, SUCCESS_COLOR, SECONDARY_GREEN)

    def update_status(self, message, status_type='info'):
        """Update the status bar text with enhanced styling."""
        self.status_bar.update_status(message, status_type)

    def plot_waveform(self, file_path):
        """Load the MP3 file, extract samples, and plot the waveform with enhanced colors."""
        try:
            audio = AudioSegment.from_mp3(file_path)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)
            
            self.ax.clear()
            # Use enhanced waveform colors
            colors = get_waveform_colors()
            self.ax.plot(samples, color=colors['waveform'], linewidth=0.5)
            self.ax.set_axis_off()
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.audio_duration_ms = len(audio)
            self.split_points = []
            self.clear_split_lines()
            # Update time label to show total duration
            self.time_label.config(text=f"00:00 / {self.ms_to_mmss(self.audio_duration_ms)}")
            
            # Add success animation
            self.anim_manager.pulse_button(self.play_button, SUCCESS_COLOR, SECONDARY_GREEN)
            
        except Exception as e:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Error loading waveform:\n{e}", ha='center', va='center', color=ERROR_COLOR)
            self.ax.set_axis_off()
            self.canvas.draw()
            self.audio_duration_ms = 0
            self.split_points = []
            self.clear_split_lines()
            self.time_label.config(text="00:00 / 00:00")
            self.status_bar.update_status(f"Error loading file: {e}", 'error')

    def on_waveform_click(self, event):
        """Handle mouse click on the waveform to add a manual split point (red line)."""
        if event.inaxes != self.ax or self.audio_duration_ms == 0:
            return
        # Convert x coordinate to ms
        xdata = event.xdata
        total_samples = self.ax.lines[0].get_xdata()[-1] if self.ax.lines else 1
        ms = int((xdata / total_samples) * self.audio_duration_ms)
        ms = max(0, min(ms, self.audio_duration_ms))
        # Add split point and vertical line with enhanced colors
        self.split_points.append(ms)
        colors = get_waveform_colors()
        line = self.ax.axvline(x=xdata, color=colors['split_line'], linestyle='--', linewidth=2)
        self.split_lines.append(line)
        self.canvas.draw()
        # Update split segments panel
        self.update_manual_split_segments()
        # Add visual feedback
        self.anim_manager.pulse_button(self.manual_split_button, SECONDARY_RED, SPLIT_LINE_ACTIVE)

    def clear_split_lines(self):
        """Remove all manual split lines from the waveform."""
        for line in getattr(self, 'split_lines', []):
            try:
                line.remove()
            except Exception:
                pass
        self.split_lines = []

    def add_manual_splits(self):
        """Add manual split points to the split segments panel."""
        # Clear the timestamp tree before adding
        for item in self.timestamp_tree.get_children():
            self.timestamp_tree.delete(item)
        # Sort and deduplicate split points, add 0 and end if not present
        points = sorted(set([0] + self.split_points + ([self.audio_duration_ms] if self.audio_duration_ms else [])))
        # Remove points outside duration
        points = [p for p in points if 0 <= p <= self.audio_duration_ms]
        # Show as segments (start, end)
        for i in range(len(points)-1):
            start = points[i]
            end = points[i+1]
            self.timestamp_tree.insert('', 'end', values=(i+1, self.ms_to_mmss(start), self.ms_to_mmss(end)))
        
        # Add success feedback
        self.status_bar.update_status(f"Added {len(self.split_points)} manual split points", 'success')

    def play_audio(self):
        """Play or resume the audio and start the playhead animation."""
        if self.current_audio_path:
            try:
                if self.is_paused:
                    # Resume from pause
                    pygame.mixer.music.unpause()
                    self.is_paused = False
                    self.start_playhead()
                    self.status_bar.update_status("Resumed playback", 'info')
                else:
                    # Start new playback
                    pygame.mixer.music.load(self.current_audio_path)
                    pygame.mixer.music.play()
                    self.start_playhead()
                    self.status_bar.update_status("Started playback", 'success')
            except Exception as e:
                messagebox.showerror("Playback Error", f"Could not play audio:\n{e}")
                self.status_bar.update_status(f"Playback error: {e}", 'error')

    def pause_audio(self):
        """Pause the audio playback and keep the playhead at the current position."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_bar.update_status("Paused playback", 'warning')
            # Don't remove the playhead - let it stay at current position
        elif self.is_paused:
            # If already paused, resume playback
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.start_playhead()
            self.status_bar.update_status("Resumed playback", 'info')

    def stop_audio(self):
        """Stop the audio playback and remove the playhead."""
        pygame.mixer.music.stop()
        self.is_paused = False
        self.remove_playhead()
        # Reset time label
        self.time_label.config(text=f"00:00 / {self.ms_to_mmss(self.audio_duration_ms)}")
        self.status_bar.update_status("Stopped playback", 'info')

    def start_playhead(self):
        """Start the playhead animation if not paused."""
        if not self.is_paused:
            self.update_playhead()

    def update_playhead(self):
        """Update the playhead line position according to playback and update the time label."""
        if not pygame.mixer.music.get_busy() and not self.is_paused:
            self.remove_playhead()
            # Reset time label to 0 when stopped
            self.time_label.config(text=f"00:00 / {self.ms_to_mmss(self.audio_duration_ms)}")
            return
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            pos_ms = 0
        if self.audio_duration_ms == 0:
            return
        # Map ms to xdata
        total_samples = self.ax.lines[0].get_xdata()[-1] if self.ax.lines else 1
        x = (pos_ms / self.audio_duration_ms) * total_samples
        # Draw or move playhead with enhanced colors
        colors = get_waveform_colors()
        if self.playhead_line is None:
            self.playhead_line = self.ax.axvline(x=x, color=colors['playhead'], linewidth=2)
        else:
            self.playhead_line.set_xdata([x, x])
        self.canvas.draw()
        # Update time label
        self.time_label.config(text=f"{self.ms_to_mmss(pos_ms)} / {self.ms_to_mmss(self.audio_duration_ms)}")
        # Only continue updating if not paused
        if not self.is_paused:
            self.canvas.get_tk_widget().after(50, self.update_playhead)

    def remove_playhead(self):
        """Remove the playhead line from the waveform."""
        if self.playhead_line is not None:
            try:
                self.playhead_line.remove()
            except Exception:
                pass
            self.playhead_line = None
        self.canvas.draw()

    def start_splitting_thread(self):
        """Validate input and start the splitting process in a separate thread."""
        source_file = self.source_file_path.get()
        if not source_file:  # Only check for source_file now
            messagebox.showerror("Error", "Please select a source file.")
            return
        try:
            min_silence_str = self.min_silence_entry.get().strip()
            if ':' in min_silence_str:
                parts = min_silence_str.split(':')
                if len(parts) == 2:
                    mins, secs = parts
                elif len(parts) == 1:
                    mins, secs = '0', parts[0]
                else:
                    raise ValueError
                min_silence_len = (int(mins) * 60 + int(secs)) * 1000
            else:
                min_silence_len = int(min_silence_str) * 1000  # fallback: treat as seconds
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for the splitting parameters (mm:ss for silence length).")
            return
        # Disable the button to prevent multiple clicks
        self.split_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        # Clear the timestamp tree before splitting
        for item in self.timestamp_tree.get_children():
            self.timestamp_tree.delete(item)
        # Run the splitting task in a new thread
        threading.Thread(
            target=self.run_split_task,
            args=(source_file, min_silence_len),
            daemon=True
        ).start()

    def run_split_task(self, file_path, min_silence_len):
        """Split the MP3 file on silence and update the split segments panel."""
        try:
            self.update_status("Loading audio file... this may take a moment.", 'info')
            audio = AudioSegment.from_mp3(file_path)
            self.update_status(f"Splitting on silence (min: {min_silence_len}ms)...", 'info')
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=-40,  # Use default threshold
                keep_silence=200,
                seek_step=1
            )
            if not chunks:
                self.update_status("No silence found to split on. Try adjusting parameters.", 'warning')
                messagebox.showwarning("No Tracks Found", "Could not find any tracks based on the current silence parameters. Please try a shorter silence length.")
                self.split_button.config(state=tk.NORMAL)
                return
            total_chunks = len(chunks)
            self.progress_bar['maximum'] = total_chunks
            # --- Calculate and display timestamps ---
            timestamps = []
            current_pos = 0
            for i, chunk in enumerate(chunks):
                start_ms = current_pos
                end_ms = current_pos + len(chunk)
                timestamps.append((i+1, start_ms, end_ms))
                current_pos = end_ms
            # Update the Treeview in the main thread
            def update_tree():
                for track, start, end in timestamps:
                    self.timestamp_tree.insert('', 'end', values=(track, self.ms_to_mmss(start), self.ms_to_mmss(end)))
            self.root.after(0, update_tree)
            self.update_status(f"Splitting complete! Found {total_chunks} tracks.", 'success')
            messagebox.showinfo("Success", f"Splitting complete!\n\nFound {total_chunks} tracks.")
        except Exception as e:
            error_message = f"An error occurred: {e}"
            self.update_status(error_message, 'error')
            messagebox.showerror("Critical Error", f"{error_message}\n\nTroubleshooting:\n1. Ensure the file is a valid MP3.\n2. CRITICAL: Ensure FFmpeg is installed and in your system's PATH.")
        finally:
            # Re-enable the button once the process is finished or fails
            self.split_button.config(state=tk.NORMAL)
            self.progress_bar['value'] = 0

    def auto_split_on_param_change(self):
        """Automatically split the MP3 file based on current parameters and update the split segments panel."""
        source_file = self.source_file_path.get()
        if not source_file:
            return
        try:
            min_silence_str = self.min_silence_entry.get().strip()
            if ':' in min_silence_str:
                parts = min_silence_str.split(':')
                if len(parts) == 2:
                    mins, secs = parts
                elif len(parts) == 1:
                    mins, secs = '0', parts[0]
                else:
                    raise ValueError
                min_silence_len = (int(mins) * 60 + int(secs)) * 1000
            else:
                min_silence_len = int(min_silence_str) * 1000  # fallback: treat as seconds
        except ValueError:
            self.update_status("Invalid splitting parameter. Please use mm:ss format.", 'error')
            return
        # Clear the timestamp tree before splitting
        for item in self.timestamp_tree.get_children():
            self.timestamp_tree.delete(item)
        # Run splitting in a thread to avoid UI freeze
        threading.Thread(
            target=self.run_auto_split_task,
            args=(source_file, min_silence_len),
            daemon=True
        ).start()

    def run_auto_split_task(self, file_path, min_silence_len):
        """Threaded task to auto split and update the split segments panel."""
        try:
            self.update_status("Splitting on silence (auto)...", 'info')
            audio = AudioSegment.from_mp3(file_path)
            chunks = split_on_silence(
                audio,
                min_silence_len=min_silence_len,
                silence_thresh=-40,  # Use default threshold
                keep_silence=200,
                seek_step=1
            )
            if not chunks:
                self.update_status("No silence found to split on. Try adjusting parameters.", 'warning')
                return
            # --- Calculate and display timestamps ---
            timestamps = []
            current_pos = 0
            for i, chunk in enumerate(chunks):
                start_ms = current_pos
                end_ms = current_pos + len(chunk)
                timestamps.append((i+1, start_ms, end_ms))
                current_pos = end_ms
            def update_tree():
                for track, start, end in timestamps:
                    self.timestamp_tree.insert('', 'end', values=(track, self.ms_to_mmss(start), self.ms_to_mmss(end)))
                self.update_status(f"Auto split complete! Found {len(timestamps)} tracks.", 'success')
            self.root.after(0, update_tree)
        except Exception as e:
            self.update_status(f"Auto split error: {e}", 'error')

    def ms_to_mmss(self, ms):
        """Convert milliseconds to mm:ss string format."""
        seconds = ms // 1000
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def download_segments_zip(self):
        """Export all split segments as MP3s, package them into a ZIP, and prompt the user to save the ZIP file."""
        import tempfile, shutil, zipfile
        # Get segments from Treeview
        segments = []
        for item in self.timestamp_tree.get_children():
            values = self.timestamp_tree.item(item, 'values')
            if len(values) == 3:
                track, start, end = values
                segments.append((int(track), start, end))
        if not segments or not self.current_audio_path:
            messagebox.showerror("Error", "No segments to export or no audio loaded.")
            return
        # Ask user for ZIP save location
        zip_path = filedialog.asksaveasfilename(defaultextension='.zip', filetypes=[('ZIP files', '*.zip')], title='Save ZIP file')
        if not zip_path:
            return
        # Load audio
        audio = AudioSegment.from_mp3(self.current_audio_path)
        # Export segments to temp dir
        temp_dir = tempfile.mkdtemp()
        mp3_paths = []
        for track, start_str, end_str in segments:
            start_ms = self.mmss_to_ms(start_str)
            end_ms = self.mmss_to_ms(end_str)
            segment = audio[start_ms:end_ms]
            out_path = os.path.join(temp_dir, f'track_{track:02d}.mp3')
            segment.export(out_path, format='mp3', bitrate='192k')
            mp3_paths.append(out_path)
        # Create ZIP
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for mp3 in mp3_paths:
                zipf.write(mp3, os.path.basename(mp3))
        # Clean up
        shutil.rmtree(temp_dir)
        messagebox.showinfo("Success", f"Exported {len(mp3_paths)} segments to ZIP:\n{zip_path}")
        self.status_bar.update_status(f"Exported {len(mp3_paths)} segments to ZIP", 'success')
        # Add success animation
        self.anim_manager.pulse_button(self.download_zip_button, SUCCESS_COLOR, SECONDARY_GREEN)

    def mmss_to_ms(self, mmss):
        """Convert mm:ss or ss string to milliseconds."""
        parts = mmss.split(':')
        if len(parts) == 2:
            mins, secs = parts
        elif len(parts) == 1:
            mins, secs = '0', parts[0]
        else:
            mins, secs = '0', '0'
        return (int(mins) * 60 + int(secs)) * 1000

    def refresh_split_lines(self):
        """Clear all red split lines, reset split points, stop audio, and reset playhead and time label."""
        # Stop any playing audio
        pygame.mixer.music.stop()
        self.is_paused = False
        # Remove black playhead line
        self.remove_playhead()
        # Clear red split lines and reset split points
        self.split_points = []
        self.clear_split_lines()
        # Redraw the canvas
        self.canvas.draw()
        # Reset time label
        self.time_label.config(text=f"00:00 / {self.ms_to_mmss(self.audio_duration_ms)}")
        self.reset_split_segments_panel()
        self.status_bar.update_status("Reset all split points and playback", 'info')

    def add_manual_split_from_entry(self):
        """Add a manual split point from the min silence entry time."""
        time_str = self.min_silence_entry.get().strip()
        if not self.audio_duration_ms:
            self.update_status("No audio loaded.", 'error')
            return
        try:
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 2:
                    mins, secs = parts
                elif len(parts) == 1:
                    mins, secs = '0', parts[0]
                else:
                    raise ValueError
                ms = (int(mins) * 60 + int(secs)) * 1000
            else:
                ms = int(time_str) * 1000
        except ValueError:
            self.update_status("Invalid time format. Use mm:ss or seconds.", 'error')
            return
        ms = max(0, min(ms, self.audio_duration_ms))
        # Add split point and vertical line if not already present
        if ms not in self.split_points:
            self.split_points.append(ms)
            total_samples = self.ax.lines[0].get_xdata()[-1] if self.ax.lines else 1
            x = (ms / self.audio_duration_ms) * total_samples
            colors = get_waveform_colors()
            line = self.ax.axvline(x=x, color=colors['split_line'], linestyle='--', linewidth=2)
            self.split_lines.append(line)
            self.canvas.draw()
        # Update split segments panel
        self.update_manual_split_segments()
        self.status_bar.update_status(f"Added split point at {self.ms_to_mmss(ms)}", 'success')

    def update_manual_split_segments(self):
        """Update the split segments panel based on manual split points."""
        # Clear the timestamp tree before adding
        for item in self.timestamp_tree.get_children():
            self.timestamp_tree.delete(item)
        # Sort and deduplicate split points, add 0 and end if not present
        points = sorted(set([0] + self.split_points + ([self.audio_duration_ms] if self.audio_duration_ms else [])))
        # Remove points outside duration
        points = [p for p in points if 0 <= p <= self.audio_duration_ms]
        # Show as segments (start, end)
        for i in range(len(points)-1):
            start = points[i]
            end = points[i+1]
            self.timestamp_tree.insert('', 'end', values=(i+1, self.ms_to_mmss(start), self.ms_to_mmss(end)))

    def refresh_split_parameters(self):
        """Reset splitting parameters and manual split points to initial state."""
        self.min_silence_entry.delete(0, tk.END)
        self.min_silence_entry.insert(0, "00:00")
        self.split_points = []
        self.clear_split_lines()
        self.reset_split_segments_panel()
        self.canvas.draw()
        self.status_bar.update_status("Reset all parameters", 'info')

    def reset_split_segments_panel(self):
        """Reset the split segments panel to initial state: only full segment if audio loaded, else empty."""
        for item in self.timestamp_tree.get_children():
            self.timestamp_tree.delete(item)
        if self.audio_duration_ms:
            self.timestamp_tree.insert('', 'end', values=(1, self.ms_to_mmss(0), self.ms_to_mmss(self.audio_duration_ms)))

if __name__ == '__main__':
    # --- Check for FFmpeg before starting the GUI ---
    # This is a good practice to give an early warning if dependencies are missing.
    try:
        # A simple check to see if pydub can find ffmpeg
        AudioSegment.from_mp3 # This line will raise an exception if ffmpeg is not found
    except Exception as e:
         print("--- STARTUP ERROR ---")
         print("Could not find FFmpeg. This program requires FFmpeg to work.")
         print("Please download it from https://ffmpeg.org/download.html")
         print("Then, add its 'bin' folder to your system's PATH environment variable.")
         print("-----------------------\n")
         # Show a pop-up error as well
         root = tk.Tk()
         root.withdraw() # Hide the main window
         messagebox.showerror(
             "FFmpeg Not Found",
             "This program requires FFmpeg to function.\n\nPlease download it from ffmpeg.org and add it to your system's PATH."
         )
         # Exit if the critical dependency is missing.
         exit()

    # --- Start the Application ---
    app_root = tk.Tk()
    app = MP3SplitterApp(app_root)
    app_root.mainloop()