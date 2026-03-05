import os
import time
import random
import math
import datetime
import platform
import tkinter as tk

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TkBase = TkinterDnD.Tk
except ImportError:
    TkBase = tk.Tk
    DND_FILES = None

def rot_x(p, a): return (p[0], p[1]*math.cos(a) - p[2]*math.sin(a), p[1]*math.sin(a) + p[2]*math.cos(a))
def rot_y(p, a): return (p[0]*math.cos(a) + p[2]*math.sin(a), p[1], -p[0]*math.sin(a) + p[2]*math.cos(a))
def rot_z(p, a): return (p[0]*math.cos(a) - p[1]*math.sin(a), p[0]*math.sin(a) + p[1]*math.cos(a), p[2])

def shrink_polygon(coords, factor=0.82):
    cx = sum(coords[0::2]) / 4
    cy = sum(coords[1::2]) / 4
    new_coords = []
    for i in range(4):
        x = coords[i*2]
        y = coords[i*2+1]
        new_coords.extend([cx + (x - cx) * factor, cy + (y - cy) * factor])
    return new_coords

class Sticker:
    def __init__(self, corners, outline, fill, cx, cy, cz):
        self.current_corners = corners
        self.outline = outline
        self.fill = fill
        self.cx = cx
        self.cy = cy
        self.cz = cz

class RubeUI:
    def __init__(self, face_path=None, size=(380, 450)):
        # THE FIX: Upgraded Root to allow Drag and Drop processing
        self.root = TkBase()
        self.root.title("RUBE")
        self.root.geometry(f"{size[0]}x{size[1]}")
        self.root.overrideredirect(True) 
        
        if platform.system() == "Windows":
            self.bg_color = "#010101" 
            self.root.configure(bg=self.bg_color)
            self.root.wm_attributes('-transparentcolor', self.bg_color)
            self.root.wm_attributes('-topmost', True)
        else:
            self.bg_color = 'systemTransparent'
            self.root.wm_attributes('-transparent', True)
            self.root.configure(bg=self.bg_color)
            if platform.system() == "Darwin":
                self.root.tk.call('tk', 'scaling', 2.0)

        self.size = size
        self.center_y = 0.42

        self.canvas = tk.Canvas(
            self.root,
            width=size[0],
            height=size[1],
            bg=self.bg_color,
            highlightthickness=0
        )
        self.canvas.place(relx=0.5, rely=self.center_y, anchor="center")

        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.do_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.speaking = False
        self.processing = False
        
        self.subtitle_id = self.canvas.create_text(
            size[0] // 2,
            size[1] - 60, 
            text="",
            fill="#00ffff", 
            font=("Consolas", 12, "bold"),
            justify="center",
            width=350,
            tags="subtitle"
        )
        self.subtitle_timer = None
        self.on_text_submit = None 

        self._init_terminal()
        self._build_cube()
        self.root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
        self._animate()

    def _init_terminal(self):
        self.terminal = tk.Toplevel(self.root)
        self.terminal.title("RUBE Terminal")
        self.terminal.geometry("400x380")
        self.terminal.configure(bg="#000000")
        self.terminal.protocol("WM_DELETE_WINDOW", self.terminal.withdraw)
        
        # THE FIX: Activating the file catcher
        if DND_FILES:
            self.terminal.drop_target_register(DND_FILES)
            self.terminal.dnd_bind('<<Drop>>', self._handle_file_drop)
        
        self.header_frame = tk.Frame(self.terminal, bg="#000000", height=30)
        self.header_frame.pack(fill=tk.X, padx=15, pady=(15,0))
        
        now = datetime.datetime.now()
        self.date_label = tk.Label(self.header_frame, text=now.strftime("%d %b %Y | %I:%M:%S %p").upper(), font=("Menlo", 11, "bold"), fg="#00ffff", bg="#000000")
        self.date_label.pack(side=tk.RIGHT)
        self._update_time()

        self.log_frame = tk.Frame(self.terminal, bg="#000000")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        tk.Label(self.log_frame, text="LOGS", font=("Menlo", 11, "bold"), fg="#ff00ff", bg="#000000").pack(anchor=tk.W)
        
        self.log_text = tk.Text(self.log_frame, height=10, font=("Menlo", 10), bg="#1a1a1a", fg="#ffffff", wrap=tk.WORD, state=tk.DISABLED, highlightthickness=1, highlightbackground="#00ffff", bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        self.input_frame = tk.Frame(self.terminal, bg="#000000", height=50)
        self.input_frame.pack(fill=tk.X, padx=15, pady=(0,15))
        
        self.entry = tk.Entry(self.input_frame, font=("Menlo", 11), bg="#000000", fg="#ffffff", insertbackground="#ff00ff", highlightthickness=1, highlightbackground="#1a1a1a", highlightcolor="#ff00ff", bd=0)
        self.entry.pack(fill=tk.X, pady=(0,5))
        self.entry.bind("<Return>", self._handle_submission)
        
        self.terminal.withdraw()

    def _handle_file_drop(self, event):
        """Extracts the file path when a user drops media into the terminal."""
        file_path = event.data
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        self.entry.insert(tk.END, f'"{file_path}" ')

    def start_move(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = False

    def do_move(self, event):
        if abs(event.x - self._drag_start_x) > 5 or abs(event.y - self._drag_start_y) > 5:
            self._is_dragging = True
            
        deltax = event.x - self._drag_start_x
        deltay = event.y - self._drag_start_y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        if not getattr(self, '_is_dragging', False):
            self.toggle_input(event)

    def trigger_hotkey(self):
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.lift()
        if self.terminal.state() != "normal":
            self.toggle_input()

    def _build_cube(self):
        self.stickers = []
        r = 0.42   
        gap = 0.09 

        colors = {
            'front': ('#00ffff', '#001a26'), 
            'back': ('#ff00ff', '#260026'),  
            'right': ('#39ff14', '#002600'), 
            'left': ('#ff4500', '#260d00'),  
            'top': ('#ffff00', '#262600'),   
            'bottom': ('#b026ff', '#1a0026') 
        }

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    if z == 1: self.stickers.append(Sticker([(x-r, y-r, z+r+gap), (x+r, y-r, z+r+gap), (x+r, y+r, z+r+gap), (x-r, y+r, z+r+gap)], colors['front'][0], colors['front'][1], x, y, z))
                    if z == -1: self.stickers.append(Sticker([(x-r, y-r, z-r-gap), (x+r, y-r, z-r-gap), (x+r, y+r, z-r-gap), (x-r, y+r, z-r-gap)], colors['back'][0], colors['back'][1], x, y, z))
                    if x == 1: self.stickers.append(Sticker([(x+r+gap, y-r, z-r), (x+r, y-r, z+r), (x+r+gap, y+r, z+r), (x+r+gap, y+r, z-r)], colors['right'][0], colors['right'][1], x, y, z))
                    if x == -1: self.stickers.append(Sticker([(x-r-gap, y-r, z-r), (x-r-gap, y-r, z+r), (x-r-gap, y+r, z+r), (x-r-gap, y+r, z-r)], colors['left'][0], colors['left'][1], x, y, z))
                    if y == -1: self.stickers.append(Sticker([(x-r, y-r-gap, z-r), (x+r, y-r-gap, z-r), (x+r, y-r-gap, z+r), (x-r, y-r-gap, z+r)], colors['top'][0], colors['top'][1], x, y, z))
                    if y == 1: self.stickers.append(Sticker([(x-r, y+r+gap, z-r), (x+r, y+r+gap, z-r), (x+r, y+r+gap, z+r), (x-r, y+r+gap, z+r)], colors['bottom'][0], colors['bottom'][1], x, y, z))

        self.global_x = 0.5
        self.global_y = 0.5
        self.animating_slice = False
        self.slice_axis = 'x'
        self.slice_layer = 1
        self.slice_angle = 0.0
        self.slice_speed = 0.05
        self.slice_dir = 1

    def toggle_input(self, event=None):
        if self.terminal.state() == "normal":
            self.terminal.withdraw()
        else:
            x = self.root.winfo_x() + self.size[0] + 10
            y = self.root.winfo_y()
            self.terminal.geometry(f"+{x}+{y}")
            self.terminal.deiconify()
            self.entry.focus_set()

    def _update_time(self):
        now = datetime.datetime.now()
        self.date_label.config(text=now.strftime("%d %b %Y | %I:%M:%S %p").upper())
        self.root.after(1000, self._update_time)

    def _handle_submission(self, event):
        text = self.entry.get().strip()
        if text and self.on_text_submit:
            self.on_text_submit(text)
        self.entry.delete(0, tk.END)
        self.terminal.withdraw()

    def update_subtitle_sync(self, full_text: str, progress: float):
        if not full_text:
            self.canvas.itemconfig(self.subtitle_id, text="")
            return
            
        if self.subtitle_timer:
            self.root.after_cancel(self.subtitle_timer)
            self.subtitle_timer = None
            
        chars_to_show = int(len(full_text) * progress)
        current_display = full_text[:chars_to_show]
        
        chunks = []
        current_chunk = ""
        for char in current_display:
            current_chunk += char
            if len(current_chunk) > 65 and char in [" ", ".", "?", "!", ",", "\n"]:
                chunks.append(current_chunk)
                current_chunk = ""
        
        final_display = current_chunk.strip()
        self.canvas.itemconfig(self.subtitle_id, text=final_display)

    def schedule_subtitle_clear(self):
        if self.subtitle_timer:
            self.root.after_cancel(self.subtitle_timer)
        self.subtitle_timer = self.root.after(4000, self._clear_subtitle)

    def _clear_subtitle(self):
        self.canvas.itemconfig(self.subtitle_id, text="")

    def write_log(self, text: str):
        self.root.after(0, self._write_log_main, text)
        
    def _write_log_main(self, message):
        self.log_text.config(state=tk.NORMAL)
        if message.startswith("RUBE:"): self.log_text.insert(tk.END, message + "\n", "rube")
        elif message.startswith("You:"): self.log_text.insert(tk.END, message + "\n", "you")
        else: self.log_text.insert(tk.END, message + "\n")
        self.log_text.tag_config("rube", foreground="#ff00ff")
        self.log_text.tag_config("you", foreground="#00ffff")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_speaking(self): self.speaking = True
    def stop_speaking(self): self.speaking = False
    def start_processing(self): self.processing = True
    def stop_processing(self): self.processing = False

    def trigger_random_slice(self):
        self.animating_slice = True
        self.slice_axis = random.choice(['x', 'y', 'z'])
        self.slice_layer = random.choice([-1, 0, 1])
        self.slice_angle = 0.0
        self.slice_dir = random.choice([-1, 1])

    def _animate(self):
        now = time.time()
        w, h = self.size
        self.canvas.delete("cube")

        self.global_y += 0.005 
        self.global_x = math.sin(now * 0.3) * 0.2 + 0.5 

        if self.processing:
            self.slice_speed = 0.12 
            if not self.animating_slice:
                self.trigger_random_slice()
        elif self.speaking:
            self.slice_speed = 0.06 
            if not self.animating_slice and random.random() < 0.05:
                self.trigger_random_slice()
        else:
            self.slice_speed = 0.02 
            if not self.animating_slice and random.random() < 0.01:
                self.trigger_random_slice()

        if self.animating_slice:
            self.slice_angle += self.slice_speed * self.slice_dir
            if abs(self.slice_angle) >= math.pi / 2:
                final_angle = (math.pi / 2) * self.slice_dir
                for s in self.stickers:
                    is_active = False
                    if self.slice_axis == 'x' and s.cx == self.slice_layer: is_active = True
                    if self.slice_axis == 'y' and s.cy == self.slice_layer: is_active = True
                    if self.slice_axis == 'z' and s.cz == self.slice_layer: is_active = True

                    if is_active:
                        nc = []
                        for c in s.current_corners:
                            if self.slice_axis == 'x': pt = rot_x(c, final_angle)
                            if self.slice_axis == 'y': pt = rot_y(c, final_angle)
                            if self.slice_axis == 'z': pt = rot_z(c, final_angle)
                            nc.append((round(pt[0], 4), round(pt[1], 4), round(pt[2], 4)))
                        s.current_corners = nc
                        
                        center = (s.cx, s.cy, s.cz)
                        if self.slice_axis == 'x': c_pt = rot_x(center, final_angle)
                        if self.slice_axis == 'y': c_pt = rot_y(center, final_angle)
                        if self.slice_axis == 'z': c_pt = rot_z(center, final_angle)
                        s.cx, s.cy, s.cz = round(c_pt[0]), round(c_pt[1]), round(c_pt[2])
                
                self.animating_slice = False
                self.slice_angle = 0.0

        polygons_to_draw = []
        fov = 275
        viewer_dist = 6.5

        if self.speaking:
            fov += math.sin(now * 15) * 15

        for s in self.stickers:
            is_active = False
            if self.animating_slice:
                if self.slice_axis == 'x' and s.cx == self.slice_layer: is_active = True
                if self.slice_axis == 'y' and s.cy == self.slice_layer: is_active = True
                if self.slice_axis == 'z' and s.cz == self.slice_layer: is_active = True

            proj_corners = []
            z_sum = 0
            for c in s.current_corners:
                pt = c
                if is_active:
                    if self.slice_axis == 'x': pt = rot_x(pt, self.slice_angle)
                    if self.slice_axis == 'y': pt = rot_y(pt, self.slice_angle)
                    if self.slice_axis == 'z': pt = rot_z(pt, self.slice_angle)
                
                pt = rot_x(pt, self.global_x)
                pt = rot_y(pt, self.global_y)

                z_sum += pt[2]

                factor = fov / (viewer_dist + pt[2])
                x_screen = pt[0] * factor + w / 2
                y_screen = pt[1] * factor + h / 2 - 60 
                
                proj_corners.extend([x_screen, y_screen])
            
            avg_z = z_sum / 4
            
            outline_color = s.outline
            fill_color = s.fill
            if self.speaking and random.random() < 0.08:
                fill_color = s.outline 

            polygons_to_draw.append((avg_z, proj_corners, outline_color, fill_color))

        polygons_to_draw.sort(key=lambda item: item[0], reverse=True)

        for poly in polygons_to_draw:
            coords = poly[1]
            out_color = poly[2]
            fill_color = poly[3]
            
            self.canvas.create_polygon(coords, outline=out_color, fill=fill_color, width=3, tags="cube")
            inner_coords = shrink_polygon(coords, 0.82)
            self.canvas.create_polygon(inner_coords, outline="#ccffff", fill="", width=1, tags="cube")
            
            for i in range(4):
                x, y = coords[i*2], coords[i*2+1]
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#ffffff", outline=out_color, width=1, tags="cube")

        self.canvas.tag_raise("subtitle")
        self.root.after(33, self._animate)