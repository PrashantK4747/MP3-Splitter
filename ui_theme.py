"""
UI Theme and Animation System for MP3 Splitter App
Provides modern styling, colors, and interactive elements for enhanced user experience.
"""

import tkinter as tk
from tkinter import ttk
import math
import time

# ============================================================================
# COLOR PALETTE - Modern, Professional Theme
# ============================================================================

# Primary Colors
PRIMARY_ORANGE = "#F97316"        # Accent color for highlights
PRIMARY_BLUE = "#2563EB"          # Main brand color
PRIMARY_DARK = "#1E40AF"          # Darker shade for hover
PRIMARY_LIGHT = "#3B82F6"         # Lighter shade for active

# Secondary Colors
SECONDARY_RED = "#DC2626"         # For split lines and warnings
SECONDARY_GREEN = "#059669"       # For success states
SECONDARY_YELLOW = "#D97706"      # For warnings
SECONDARY_PURPLE = "#7C3AED"      # For highlights

# Background Colors
BG_PRIMARY = "#FFFFFF"            # Main background
BG_SECONDARY = "#F8FAFC"          # Secondary background
BG_DARK = "#1F2937"               # Dark background for panels
BG_LIGHT = "#F1F5F9"              # Light background for cards

# Text Colors
TEXT_PRIMARY = "#1F2937"          # Main text
TEXT_SECONDARY = "#6B7280"        # Secondary text
TEXT_LIGHT = "#FFFFFF"            # Light text on dark backgrounds
TEXT_MUTED = "#9CA3AF"            # Muted text

# Waveform Colors
WAVEFORM_COLOR = "#3B82F6"        # Main waveform color
WAVEFORM_HIGHLIGHT = "#1D4ED8"    # Highlighted waveform
PLAYHEAD_COLOR = "#000000"        # Black playhead
SPLIT_LINE_COLOR = "#DC2626"      # Red split lines
SPLIT_LINE_ACTIVE = "#EF4444"     # Active split line

# Status Colors
SUCCESS_COLOR = "#059669"
ERROR_COLOR = "#DC2626"
WARNING_COLOR = "#D97706"
INFO_COLOR = "#2563EB"

# ============================================================================
# FONT CONFIGURATIONS
# ============================================================================

FONTS = {
    'header': ('Segoe UI', 18, 'bold'),
    'subheader': ('Segoe UI', 18, 'bold'),
    'body': ('Segoe UI', 12),
    'body_bold': ('Segoe UI', 12, 'bold'),
    'caption': ('Segoe UI', 10),
    'button': ('Segoe UI', 12, 'bold'),
    'time': ('Consolas', 12, 'bold'),
}

# ============================================================================
# STYLE CONFIGURATIONS
# ============================================================================

def apply_modern_theme(style: ttk.Style):
    """Apply modern theme to the ttk style object."""
    
    # Configure the main theme
    style.theme_use('clam')
    
    # Frame styles
    style.configure('TFrame', background=BG_PRIMARY)
    style.configure('Card.TFrame', background=BG_SECONDARY, relief='flat', borderwidth=1)
    style.configure('Panel.TFrame', background=BG_DARK)
    
    # Label styles
    style.configure('TLabel', 
                   background=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['body'])
    
    style.configure('Header.TLabel', 
                   background=BG_PRIMARY, 
                   foreground=PRIMARY_ORANGE, 
                   font=FONTS['header'])
    
    style.configure('Subheader.TLabel', 
                   background=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['subheader'])
    
    style.configure('Time.TLabel', 
                   background=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['time'])
    
    style.configure('Status.TLabel', 
                   background=BG_SECONDARY, 
                   foreground=TEXT_SECONDARY, 
                   font=FONTS['caption'])
    
    # Button styles
    style.configure('Primary.TButton', 
                   background=PRIMARY_BLUE, 
                   foreground=TEXT_LIGHT, 
                   font=FONTS['button'],
                   padding=(15, 8),
                   relief='flat',
                   borderwidth=0)
    
    style.configure('Secondary.TButton', 
                   background=BG_SECONDARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['button'],
                   padding=(12, 6),
                   relief='flat',
                   borderwidth=1)
    
    style.configure('Danger.TButton', 
                   background=SECONDARY_RED, 
                   foreground=TEXT_LIGHT, 
                   font=FONTS['button'],
                   padding=(12, 6),
                   relief='flat',
                   borderwidth=0)
    
    style.configure('Success.TButton', 
                   background=SECONDARY_GREEN, 
                   foreground=TEXT_LIGHT, 
                   font=FONTS['button'],
                   padding=(12, 6),
                   relief='flat',
                   borderwidth=0)
    
    # Button hover effects
    style.map('Primary.TButton',
              background=[('active', PRIMARY_DARK), ('pressed', PRIMARY_LIGHT)],
              foreground=[('active', TEXT_LIGHT), ('pressed', TEXT_LIGHT)])
    
    style.map('Secondary.TButton',
              background=[('active', BG_LIGHT), ('pressed', BG_DARK)],
              foreground=[('active', TEXT_PRIMARY), ('pressed', TEXT_LIGHT)])
    
    style.map('Danger.TButton',
              background=[('active', '#B91C1C'), ('pressed', '#991B1B')],
              foreground=[('active', TEXT_LIGHT), ('pressed', TEXT_LIGHT)])
    
    style.map('Success.TButton',
              background=[('active', '#047857'), ('pressed', '#065F46')],
              foreground=[('active', TEXT_LIGHT), ('pressed', TEXT_LIGHT)])
    
    # Entry styles
    style.configure('TEntry', 
                   fieldbackground=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['body'],
                   borderwidth=2,
                   relief='solid')
    
    style.map('TEntry',
              fieldbackground=[('focus', BG_SECONDARY)],
              bordercolor=[('focus', PRIMARY_BLUE)])
    
    # Progress bar styles
    style.configure('TProgressbar', 
                   background=PRIMARY_BLUE, 
                   troughcolor=BG_SECONDARY,
                   borderwidth=0,
                   lightcolor=PRIMARY_BLUE,
                   darkcolor=PRIMARY_BLUE)
    
    # Treeview styles
    style.configure('Treeview', 
                   background=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY, 
                   fieldbackground=BG_PRIMARY,
                   font=FONTS['body'])
    
    style.configure('Treeview.Heading', 
                   background=BG_SECONDARY, 
                   foreground=TEXT_PRIMARY, 
                   font=FONTS['body_bold'])
    
    style.map('Treeview',
              background=[('selected', PRIMARY_BLUE)],
              foreground=[('selected', TEXT_LIGHT)])
    
    # LabelFrame styles
    style.configure('TLabelframe', 
                   background=BG_PRIMARY, 
                   foreground=TEXT_PRIMARY,
                   font=FONTS['body_bold'])
    
    style.configure('TLabelframe.Label', 
                   background=BG_PRIMARY, 
                   foreground=PRIMARY_BLUE,
                   font=FONTS['body_bold'])

# ============================================================================
# ANIMATION HELPERS
# ============================================================================

class AnimationManager:
    """Manages smooth animations and transitions."""
    
    def __init__(self, root):
        self.root = root
        self.animations = {}
    
    def fade_in(self, widget, duration=300, callback=None):
        """Fade in a widget with smooth opacity transition."""
        widget.attributes('-alpha', 0.0) if hasattr(widget, 'attributes') else None
        
        def animate(alpha=0.0):
            if alpha < 1.0:
                if hasattr(widget, 'attributes'):
                    widget.attributes('-alpha', alpha)
                alpha += 0.1
                self.root.after(30, lambda: animate(alpha))
            else:
                if hasattr(widget, 'attributes'):
                    widget.attributes('-alpha', 1.0)
                if callback:
                    callback()
        
        animate()
    
    def pulse_button(self, button, color1=PRIMARY_BLUE, color2=PRIMARY_LIGHT, duration=500):
        """Create a pulsing effect on a button."""
        # Check if it's a ttk button or tk button
        if isinstance(button, ttk.Button):
            # For ttk buttons, we can't easily change background color
            # So we'll create a visual pulse effect by briefly changing the style
            original_style = button.cget('style')
            
            def pulse(count=0):
                if count < 3:  # Pulse 3 times
                    # Create temporary highlight effect
                    button.state(['pressed'] if count % 2 == 0 else ['!pressed'])
                    self.root.after(duration//6, lambda: pulse(count + 1))
                else:
                    button.state(['!pressed'])
            
            pulse()
        else:
            # For regular tk buttons
            original_bg = button.cget('bg')
            
            def pulse(count=0):
                if count < 3:  # Pulse 3 times
                    color = color1 if count % 2 == 0 else color2
                    button.configure(bg=color)
                    self.root.after(duration//6, lambda: pulse(count + 1))
                else:
                    button.configure(bg=original_bg)
            
            pulse()
    
    def slide_in(self, widget, direction='left', duration=300):
        """Slide in a widget from a direction."""
        original_x = widget.winfo_x()
        original_y = widget.winfo_y()
        
        if direction == 'left':
            widget.place(x=-widget.winfo_width(), y=original_y)
        elif direction == 'right':
            widget.place(x=self.root.winfo_width(), y=original_y)
        elif direction == 'top':
            widget.place(x=original_x, y=-widget.winfo_height())
        elif direction == 'bottom':
            widget.place(x=original_x, y=self.root.winfo_height())
        
        def animate(progress=0.0):
            if progress < 1.0:
                if direction == 'left':
                    x = -widget.winfo_width() + (original_x + widget.winfo_width()) * progress
                    widget.place(x=x, y=original_y)
                elif direction == 'right':
                    x = self.root.winfo_width() - (self.root.winfo_width() - original_x) * progress
                    widget.place(x=x, y=original_y)
                elif direction == 'top':
                    y = -widget.winfo_height() + (original_y + widget.winfo_height()) * progress
                    widget.place(x=original_x, y=y)
                elif direction == 'bottom':
                    y = self.root.winfo_height() - (self.root.winfo_height() - original_y) * progress
                    widget.place(x=original_x, y=y)
                
                progress += 0.05
                self.root.after(15, lambda: animate(progress))
            else:
                widget.place(x=original_x, y=original_y)
        
        animate()

# ============================================================================
# INTERACTIVE ELEMENTS
# ============================================================================

class InteractiveButton(tk.Button):
    """Enhanced button with hover effects and animations."""
    
    def __init__(self, parent, **kwargs):
        self.normal_bg = kwargs.get('bg', PRIMARY_BLUE)
        self.hover_bg = kwargs.get('hover_bg', PRIMARY_DARK)
        self.pressed_bg = kwargs.get('pressed_bg', PRIMARY_LIGHT)
        self.normal_fg = kwargs.get('fg', TEXT_LIGHT)
        self.hover_fg = kwargs.get('hover_fg', TEXT_LIGHT)
        
        super().__init__(parent, **kwargs)
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def on_enter(self, event):
        """Handle mouse enter event."""
        self.configure(bg=self.hover_bg, fg=self.hover_fg)
    
    def on_leave(self, event):
        """Handle mouse leave event."""
        self.configure(bg=self.normal_bg, fg=self.normal_fg)
    
    def on_press(self, event):
        """Handle button press event."""
        self.configure(bg=self.pressed_bg)
    
    def on_release(self, event):
        """Handle button release event."""
        self.configure(bg=self.hover_bg)

class StatusBar(tk.Frame):
    """Enhanced status bar with animations and color coding."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=BG_SECONDARY, relief='sunken', bd=1)
        
        self.status_label = tk.Label(self, 
                                   text="Ready", 
                                   bg=BG_SECONDARY, 
                                   fg=TEXT_SECONDARY,
                                   font=FONTS['caption'],
                                   anchor='w')
        self.status_label.pack(side='left', fill='x', padx=5, pady=2)
        
        self.progress = ttk.Progressbar(self, 
                                       mode='determinate', 
                                       style='TProgressbar')
        self.progress.pack(side='right', fill='x', padx=5, pady=2, expand=True)
    
    def update_status(self, message, status_type='info'):
        """Update status with color coding and animation."""
        colors = {
            'info': TEXT_SECONDARY,
            'success': SUCCESS_COLOR,
            'warning': WARNING_COLOR,
            'error': ERROR_COLOR
        }
        
        self.status_label.configure(text=message, fg=colors.get(status_type, TEXT_SECONDARY))
        
        # Flash effect for important messages
        if status_type in ['success', 'warning', 'error']:
            self.flash_status()
    
    def flash_status(self):
        """Create a flash effect on the status bar."""
        original_bg = self.status_label.cget('bg')
        
        def flash(count=0):
            if count < 3:
                color = BG_LIGHT if count % 2 == 0 else original_bg
                self.status_label.configure(bg=color)
                self.after(200, lambda: flash(count + 1))
            else:
                self.status_label.configure(bg=original_bg)
        
        flash()

# ============================================================================
# WAVEFORM ENHANCEMENTS
# ============================================================================

def get_waveform_colors():
    """Get color scheme for waveform display."""
    return {
        'waveform': WAVEFORM_COLOR,
        'waveform_highlight': WAVEFORM_HIGHLIGHT,
        'playhead': PLAYHEAD_COLOR,
        'split_line': SPLIT_LINE_COLOR,
        'split_line_active': SPLIT_LINE_ACTIVE,
        'background': BG_PRIMARY,
        'grid': BG_LIGHT
    }

def create_gradient_colors(start_color, end_color, steps=10):
    """Create a gradient between two colors."""
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    colors = []
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        colors.append(rgb_to_hex((r, g, b)))
    
    return colors

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_tooltip(widget, text):
    """Create a tooltip for a widget."""
    def show_tooltip(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = tk.Label(tooltip, text=text, 
                        bg=BG_DARK, fg=TEXT_LIGHT, 
                        font=FONTS['caption'],
                        relief='solid', borderwidth=1)
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
        
        widget.bind('<Leave>', lambda e: hide_tooltip())
        tooltip.bind('<Leave>', lambda e: hide_tooltip())
    
    widget.bind('<Enter>', show_tooltip)

def add_hover_effect(widget, hover_bg, normal_bg):
    """Add simple hover effect to any widget."""
    def on_enter(event):
        widget.configure(bg=hover_bg)
    
    def on_leave(event):
        widget.configure(bg=normal_bg)
    
    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)

# ============================================================================
# THEME PRESETS
# ============================================================================

def get_theme_preset(preset_name='default'):
    """Get predefined theme configurations."""
    presets = {
        'default': {
            'primary': PRIMARY_BLUE,
            'secondary': SECONDARY_RED,
            'background': BG_PRIMARY,
            'text': TEXT_PRIMARY
        },
        'dark': {
            'primary': '#3B82F6',
            'secondary': '#EF4444',
            'background': '#1F2937',
            'text': '#F9FAFB'
        },
        'ocean': {
            'primary': '#0EA5E9',
            'secondary': '#F59E0B',
            'background': '#F0F9FF',
            'text': '#0C4A6E'
        },
        'forest': {
            'primary': '#059669',
            'secondary': '#DC2626',
            'background': '#F0FDF4',
            'text': '#064E3B'
        }
    }
    
    return presets.get(preset_name, presets['default'])

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_theme(root):
    """Initialize the complete theme system."""
    style = ttk.Style(root)
    apply_modern_theme(style)
    
    # Configure root window
    root.configure(bg=BG_PRIMARY)
    
    # Create animation manager
    anim_manager = AnimationManager(root)
    
    return style, anim_manager
