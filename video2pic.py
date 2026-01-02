"""
RonVideo2Pic - Video Frame Browser & Exporter
Author: Ron
Homepage: Ron.Quest

Features:
- Import any video format
- Frame-by-frame / slow motion playback
- Export frames as images
- Export multiple frames as GIF (WeChat sticker compatible)
"""

import os
import sys
import subprocess
import tempfile
import shutil
import locale
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json


# ============================================================
# Internationalization / 国际化
# ============================================================

LANG_ZH = {
    'app_title': 'RonVideo2Pic - 视频帧浏览与导出',
    'open_video': '打开视频',
    'export_current': '导出当前帧',
    'select_frame': '选中当前帧 [空格]',
    'export_selected': '导出选中帧',
    'export_gif': '导出 GIF',
    'author_info': 'Author: Ron | Ron.Quest',
    'hint_text': '拖放视频文件或点击 [打开视频]',
    'selected_frames': '已选帧列表',
    'remove': '移除选中',
    'clear_all': '清空列表',
    'prev_frame': '<< 上一帧',
    'next_frame': '下一帧 >>',
    'play': '播放',
    'pause': '暂停',
    'speed': '播放速度:',
    'ready': '就绪 - 请打开视频文件',
    'loading': '正在加载视频...',
    'loaded': '已加载: ',
    'exported': '已导出: ',
    'exported_n': '已导出 {n} 张图片到 ',
    'generating_gif': '正在生成 GIF...',
    'gif_saved': 'GIF 已保存: ',
    'gif_failed': 'GIF 生成失败',
    'no_video': '请先打开视频文件',
    'no_frames': '请先选中要导出的帧',
    'no_frames_gif': '请先选中要导出的帧 (使用空格键选中)',
    'load_failed': '无法加载视频文件，请确保 FFmpeg 可用',
    'video_files': '视频文件',
    'all_files': '所有文件',
    'save_frame': '保存帧图片',
    'select_folder': '选择导出目录',
    'save_gif': '保存 GIF',
    'gif_settings': 'GIF 导出设置',
    'gif_params': 'GIF 导出参数',
    'frame_count': '选中帧数: ',
    'fps': '帧率 (FPS):',
    'width': '宽度 (像素):',
    'preset': '平台预设:',
    'wechat': '微信表情包',
    'qq': 'QQ 表情',
    'general': '通用',
    'loop': '循环次数:',
    'loop_hint': '(0=无限循环)',
    'cancel': '取消',
    'export': '导出',
    'lang_switch': 'English',
    'marked': '[已选中]',
    'frame_fmt': '帧 {f:5d}  |  {t:.2f}s',
}

LANG_EN = {
    'app_title': 'RonVideo2Pic - Video Frame Browser & Exporter',
    'open_video': 'Open Video',
    'export_current': 'Export Frame',
    'select_frame': 'Select Frame [Space]',
    'export_selected': 'Export Selected',
    'export_gif': 'Export GIF',
    'author_info': 'Author: Ron | Ron.Quest',
    'hint_text': 'Drop video file or click [Open Video]',
    'selected_frames': 'Selected Frames',
    'remove': 'Remove',
    'clear_all': 'Clear All',
    'prev_frame': '<< Prev',
    'next_frame': 'Next >>',
    'play': 'Play',
    'pause': 'Pause',
    'speed': 'Speed:',
    'ready': 'Ready - Please open a video file',
    'loading': 'Loading video...',
    'loaded': 'Loaded: ',
    'exported': 'Exported: ',
    'exported_n': 'Exported {n} images to ',
    'generating_gif': 'Generating GIF...',
    'gif_saved': 'GIF saved: ',
    'gif_failed': 'GIF generation failed',
    'no_video': 'Please open a video file first',
    'no_frames': 'Please select frames to export first',
    'no_frames_gif': 'Please select frames first (use Space key)',
    'load_failed': 'Failed to load video, please ensure FFmpeg is available',
    'video_files': 'Video Files',
    'all_files': 'All Files',
    'save_frame': 'Save Frame Image',
    'select_folder': 'Select Export Folder',
    'save_gif': 'Save GIF',
    'gif_settings': 'GIF Export Settings',
    'gif_params': 'GIF Export Parameters',
    'frame_count': 'Selected frames: ',
    'fps': 'FPS:',
    'width': 'Width (px):',
    'preset': 'Presets:',
    'wechat': 'WeChat',
    'qq': 'QQ',
    'general': 'General',
    'loop': 'Loop count:',
    'loop_hint': '(0=infinite)',
    'cancel': 'Cancel',
    'export': 'Export',
    'lang_switch': '中文',
    'marked': '[Selected]',
    'frame_fmt': 'Frame {f:5d}  |  {t:.2f}s',
}


def detect_language():
    """Detect system language"""
    try:
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith('zh'):
            return 'zh'
    except:
        pass
    return 'en'


class I18n:
    """Internationalization helper"""

    def __init__(self):
        self.lang = detect_language()
        self.strings = LANG_ZH if self.lang == 'zh' else LANG_EN

    def get(self, key):
        return self.strings.get(key, key)

    def toggle(self):
        if self.lang == 'zh':
            self.lang = 'en'
            self.strings = LANG_EN
        else:
            self.lang = 'zh'
            self.strings = LANG_ZH


# Global i18n instance
i18n = I18n()


# ============================================================
# FFmpeg Helper
# ============================================================

class FFmpegHelper:
    """FFmpeg helper for video decoding"""

    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()

    def _find_ffmpeg(self):
        """Find ffmpeg executable - prioritize local bundled version"""
        # Priority 1: bundled ffmpeg in ffmpeg/ subfolder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(base_dir, 'ffmpeg', 'ffmpeg.exe')
        if os.path.exists(local_path):
            return local_path

        # Priority 2: ffmpeg in same directory
        same_dir = os.path.join(base_dir, 'ffmpeg.exe')
        if os.path.exists(same_dir):
            return same_dir

        # Priority 3: system PATH
        result = shutil.which('ffmpeg')
        if result:
            return result

        return 'ffmpeg'

    def _find_ffprobe(self):
        """Find ffprobe executable - prioritize local bundled version"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(base_dir, 'ffmpeg', 'ffprobe.exe')
        if os.path.exists(local_path):
            return local_path

        same_dir = os.path.join(base_dir, 'ffprobe.exe')
        if os.path.exists(same_dir):
            return same_dir

        result = shutil.which('ffprobe')
        if result:
            return result

        return 'ffprobe'

    def get_video_info(self, video_path):
        """Get video information"""
        cmd = [
            self.ffprobe_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            info = json.loads(result.stdout)

            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    width = stream.get('width', 0)
                    height = stream.get('height', 0)

                    # Parse frame rate
                    fps_str = stream.get('r_frame_rate', '30/1')
                    if '/' in fps_str:
                        num, den = map(float, fps_str.split('/'))
                        fps = num / den if den != 0 else 30
                    else:
                        fps = float(fps_str)

                    # Parse total frames
                    nb_frames = stream.get('nb_frames')
                    if nb_frames:
                        total_frames = int(nb_frames)
                    else:
                        duration = float(info.get('format', {}).get('duration', 0))
                        total_frames = int(duration * fps) if duration > 0 else 0

                    return {
                        'width': width,
                        'height': height,
                        'fps': fps,
                        'total_frames': total_frames,
                        'duration': float(info.get('format', {}).get('duration', 0))
                    }
        except Exception as e:
            print(f"Failed to get video info: {e}")
        return None

    def extract_frame(self, video_path, frame_number, fps, output_path):
        """Extract specific frame"""
        timestamp = frame_number / fps
        cmd = [
            self.ffmpeg_path,
            '-y',
            '-ss', str(timestamp),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True,
                          creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Failed to extract frame: {e}")
            return False

    def create_gif(self, image_paths, output_path, fps=10, width=None, loop=0, optimize=True):
        """Create GIF animation"""
        if not image_paths:
            return False

        images = []
        for path in image_paths:
            img = Image.open(path)
            if width and img.width != width:
                ratio = width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((width, new_height), Image.Resampling.LANCZOS)
            if img.mode != 'P':
                img = img.convert('RGBA')
            images.append(img)

        if not images:
            return False

        duration = int(1000 / fps)

        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop,
            optimize=optimize
        )
        return os.path.exists(output_path)


# ============================================================
# Video Player Core
# ============================================================

class VideoPlayer:
    """Video player core"""

    def __init__(self):
        self.ffmpeg = FFmpegHelper()
        self.video_path = None
        self.video_info = None
        self.current_frame = 0
        self.temp_dir = None
        self.frame_cache = {}
        self.cache_size = 50
        self.selected_frames = set()

    def load_video(self, path):
        """Load video file"""
        self.video_path = path
        self.video_info = self.ffmpeg.get_video_info(path)
        self.current_frame = 0
        self.frame_cache.clear()
        self.selected_frames.clear()

        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp(prefix='ronvideo_')

        return self.video_info is not None

    def get_frame_image(self, frame_number):
        """Get image for specific frame"""
        if not self.video_info:
            return None

        if frame_number in self.frame_cache:
            return self.frame_cache[frame_number]

        temp_path = os.path.join(self.temp_dir, f'temp_{frame_number}.png')
        if self.ffmpeg.extract_frame(self.video_path, frame_number,
                                      self.video_info['fps'], temp_path):
            img = Image.open(temp_path)

            if len(self.frame_cache) >= self.cache_size:
                oldest = min(self.frame_cache.keys())
                del self.frame_cache[oldest]

            self.frame_cache[frame_number] = img.copy()
            return self.frame_cache[frame_number]

        return None

    def cleanup(self):
        """Clean up temp files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)


# ============================================================
# Main Application
# ============================================================

class RonVideo2PicApp:
    """Main application"""

    def __init__(self, root):
        self.root = root
        self.root.title(i18n.get('app_title'))
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.setup_style()

        self.player = VideoPlayer()
        self.playing = False
        self.play_speed = 1.0
        self.photo_image = None

        self.create_ui()
        self.bind_shortcuts()

    def setup_style(self):
        """Setup UI style"""
        style = ttk.Style()

        self.colors = {
            'bg': '#1a1a2e',
            'bg_light': '#16213e',
            'accent': '#0f3460',
            'highlight': '#e94560',
            'text': '#eaeaea',
            'text_dim': '#8b8b8b'
        }

        self.root.configure(bg=self.colors['bg'])

        style.theme_use('clam')

        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       padding=(10, 5))
        style.map('TButton',
                 background=[('active', self.colors['highlight'])])

        style.configure('Accent.TButton',
                       background=self.colors['highlight'],
                       foreground='white')

        style.configure('TScale', background=self.colors['bg'], troughcolor=self.colors['bg_light'])

        style.configure('TCheckbutton',
                       background=self.colors['bg'],
                       foreground=self.colors['text'])

        style.configure('TSpinbox',
                       fieldbackground=self.colors['bg_light'],
                       foreground=self.colors['text'])

    def create_ui(self):
        """Create user interface"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar(main_frame)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.create_preview_area(content_frame)
        self.create_sidebar(content_frame)
        self.create_controls(main_frame)
        self.create_statusbar(main_frame)

    def create_toolbar(self, parent):
        """Create top toolbar"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        self.btn_open = ttk.Button(toolbar, text=i18n.get('open_video'), command=self.open_video)
        self.btn_open.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_export_frame = ttk.Button(toolbar, text=i18n.get('export_current'), command=self.export_current_frame)
        self.btn_export_frame.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_select = ttk.Button(toolbar, text=i18n.get('select_frame'), command=self.toggle_current_frame)
        self.btn_select.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_export_selected = ttk.Button(toolbar, text=i18n.get('export_selected'), command=self.export_selected_frames)
        self.btn_export_selected.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_gif = ttk.Button(toolbar, text=i18n.get('export_gif'), command=self.export_gif, style='Accent.TButton')
        self.btn_gif.pack(side=tk.LEFT)

        # Language switch
        self.btn_lang = ttk.Button(toolbar, text=i18n.get('lang_switch'), command=self.toggle_language, width=8)
        self.btn_lang.pack(side=tk.RIGHT, padx=(10, 0))

        self.author_label = ttk.Label(toolbar, text=i18n.get('author_info'),
                                foreground=self.colors['text_dim'])
        self.author_label.pack(side=tk.RIGHT)

    def create_preview_area(self, parent):
        """Create video preview area"""
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(preview_frame, bg=self.colors['bg_light'],
                               highlightthickness=1, highlightbackground=self.colors['accent'])
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_text(400, 300, text=i18n.get('hint_text'),
                               fill=self.colors['text_dim'], font=('Microsoft YaHei', 14),
                               tags='hint')

        self.canvas.bind('<Button-1>', self.on_canvas_click)

    def create_sidebar(self, parent):
        """Create sidebar"""
        sidebar = ttk.Frame(parent, width=200)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        sidebar.pack_propagate(False)

        self.sidebar_title = ttk.Label(sidebar, text=i18n.get('selected_frames'), font=('Microsoft YaHei', 11, 'bold'))
        self.sidebar_title.pack(pady=(0, 10))

        list_frame = ttk.Frame(sidebar)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame_listbox = tk.Listbox(list_frame, bg=self.colors['bg_light'],
                                        fg=self.colors['text'],
                                        selectbackground=self.colors['highlight'],
                                        font=('Consolas', 10),
                                        yscrollcommand=scrollbar.set)
        self.frame_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.frame_listbox.yview)

        self.frame_listbox.bind('<Double-1>', self.goto_selected_frame)

        btn_frame = ttk.Frame(sidebar)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_remove = ttk.Button(btn_frame, text=i18n.get('remove'), command=self.remove_selected_frame)
        self.btn_remove.pack(fill=tk.X, pady=2)

        self.btn_clear = ttk.Button(btn_frame, text=i18n.get('clear_all'), command=self.clear_selected_frames)
        self.btn_clear.pack(fill=tk.X, pady=2)

    def create_controls(self, parent):
        """Create bottom controls"""
        controls = ttk.Frame(parent)
        controls.pack(fill=tk.X, pady=10)

        slider_frame = ttk.Frame(controls)
        slider_frame.pack(fill=tk.X, pady=(0, 10))

        self.frame_var = tk.IntVar(value=0)
        self.frame_slider = ttk.Scale(slider_frame, from_=0, to=100,
                                      variable=self.frame_var, orient=tk.HORIZONTAL,
                                      command=self.on_slider_change)
        self.frame_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.frame_label = ttk.Label(slider_frame, text="0 / 0", width=15)
        self.frame_label.pack(side=tk.RIGHT, padx=(10, 0))

        play_frame = ttk.Frame(controls)
        play_frame.pack()

        self.btn_prev = ttk.Button(play_frame, text=i18n.get('prev_frame'), command=self.prev_frame)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        btn_prev10 = ttk.Button(play_frame, text="<< 10", command=lambda: self.jump_frames(-10))
        btn_prev10.pack(side=tk.LEFT, padx=5)

        self.play_btn_text = tk.StringVar(value=i18n.get('play'))
        self.btn_play = ttk.Button(play_frame, textvariable=self.play_btn_text,
                             command=self.toggle_play, style='Accent.TButton')
        self.btn_play.pack(side=tk.LEFT, padx=5)

        btn_next10 = ttk.Button(play_frame, text="10 >>", command=lambda: self.jump_frames(10))
        btn_next10.pack(side=tk.LEFT, padx=5)

        self.btn_next = ttk.Button(play_frame, text=i18n.get('next_frame'), command=self.next_frame)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        speed_frame = ttk.Frame(controls)
        speed_frame.pack(pady=(10, 0))

        self.speed_label = ttk.Label(speed_frame, text=i18n.get('speed'))
        self.speed_label.pack(side=tk.LEFT)

        self.speed_var = tk.StringVar(value="1.0x")
        speeds = ["0.1x", "0.25x", "0.5x", "1.0x", "2.0x"]
        for spd in speeds:
            btn = ttk.Button(speed_frame, text=spd, width=6,
                           command=lambda s=spd: self.set_speed(s))
            btn.pack(side=tk.LEFT, padx=2)

    def create_statusbar(self, parent):
        """Create status bar"""
        statusbar = ttk.Frame(parent)
        statusbar.pack(fill=tk.X)

        self.status_var = tk.StringVar(value=i18n.get('ready'))
        self.status_label = ttk.Label(statusbar, textvariable=self.status_var,
                                foreground=self.colors['text_dim'])
        self.status_label.pack(side=tk.LEFT)

        self.info_var = tk.StringVar(value="")
        self.info_label = ttk.Label(statusbar, textvariable=self.info_var,
                              foreground=self.colors['text_dim'])
        self.info_label.pack(side=tk.RIGHT)

    def toggle_language(self):
        """Toggle language between Chinese and English"""
        i18n.toggle()
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Refresh all UI text after language change"""
        self.root.title(i18n.get('app_title'))
        self.btn_open.config(text=i18n.get('open_video'))
        self.btn_export_frame.config(text=i18n.get('export_current'))
        self.btn_select.config(text=i18n.get('select_frame'))
        self.btn_export_selected.config(text=i18n.get('export_selected'))
        self.btn_gif.config(text=i18n.get('export_gif'))
        self.btn_lang.config(text=i18n.get('lang_switch'))
        self.sidebar_title.config(text=i18n.get('selected_frames'))
        self.btn_remove.config(text=i18n.get('remove'))
        self.btn_clear.config(text=i18n.get('clear_all'))
        self.btn_prev.config(text=i18n.get('prev_frame'))
        self.btn_next.config(text=i18n.get('next_frame'))
        self.speed_label.config(text=i18n.get('speed'))

        if self.playing:
            self.play_btn_text.set(i18n.get('pause'))
        else:
            self.play_btn_text.set(i18n.get('play'))

        if not self.player.video_path:
            self.status_var.set(i18n.get('ready'))
            self.canvas.delete('hint')
            self.canvas.create_text(400, 300, text=i18n.get('hint_text'),
                                   fill=self.colors['text_dim'], font=('Microsoft YaHei', 14),
                                   tags='hint')

        self.update_frame_list()

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Left>', lambda e: self.prev_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())
        self.root.bind('<space>', lambda e: self.toggle_current_frame())
        self.root.bind('<Return>', lambda e: self.toggle_play())
        self.root.bind('<Home>', lambda e: self.goto_frame(0))
        self.root.bind('<End>', lambda e: self.goto_frame(self.get_total_frames() - 1))
        self.root.bind('<Control-o>', lambda e: self.open_video())
        self.root.bind('<Control-s>', lambda e: self.export_current_frame())
        self.root.bind('<Control-g>', lambda e: self.export_gif())

    def open_video(self):
        """Open video file"""
        filetypes = [
            (i18n.get('video_files'), "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp"),
            (i18n.get('all_files'), "*.*")
        ]
        path = filedialog.askopenfilename(title=i18n.get('open_video'), filetypes=filetypes)
        if path:
            self.load_video(path)

    def load_video(self, path):
        """Load video"""
        self.status_var.set(i18n.get('loading'))
        self.root.update()

        if self.player.load_video(path):
            info = self.player.video_info
            total = info['total_frames']

            self.frame_slider.configure(to=max(1, total - 1))
            self.frame_var.set(0)

            self.info_var.set(f"{info['width']}x{info['height']} | {info['fps']:.2f} FPS | {total} frames")
            self.status_var.set(i18n.get('loaded') + os.path.basename(path))

            self.canvas.delete('hint')

            self.display_frame(0)
        else:
            messagebox.showerror("Error", i18n.get('load_failed'))

    def display_frame(self, frame_number):
        """Display specific frame"""
        if not self.player.video_info:
            return

        total = self.player.video_info['total_frames']
        frame_number = max(0, min(frame_number, total - 1))

        img = self.player.get_frame_image(frame_number)
        if img:
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()

            if canvas_w > 1 and canvas_h > 1:
                ratio = min(canvas_w / img.width, canvas_h / img.height)
                new_w = int(img.width * ratio)
                new_h = int(img.height * ratio)
                img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                img_resized = img

            self.photo_image = ImageTk.PhotoImage(img_resized)

            self.canvas.delete('all')
            self.canvas.create_image(canvas_w // 2, canvas_h // 2,
                                    image=self.photo_image, anchor=tk.CENTER)

            if frame_number in self.player.selected_frames:
                self.canvas.create_text(10, 10, text=i18n.get('marked'),
                                        fill=self.colors['highlight'],
                                        anchor=tk.NW, font=('Microsoft YaHei', 10, 'bold'))

        self.player.current_frame = frame_number
        self.frame_label.config(text=f"{frame_number + 1} / {total}")

        self.frame_slider.set(frame_number)

    def on_slider_change(self, value):
        """Slider change callback"""
        frame = int(float(value))
        if frame != self.player.current_frame:
            self.display_frame(frame)

    def on_canvas_click(self, event):
        """Canvas click handler"""
        if not self.player.video_path:
            self.open_video()

    def prev_frame(self):
        """Previous frame"""
        self.display_frame(self.player.current_frame - 1)

    def next_frame(self):
        """Next frame"""
        self.display_frame(self.player.current_frame + 1)

    def jump_frames(self, delta):
        """Jump multiple frames"""
        self.display_frame(self.player.current_frame + delta)

    def goto_frame(self, frame):
        """Go to specific frame"""
        self.display_frame(frame)

    def get_total_frames(self):
        """Get total frame count"""
        if self.player.video_info:
            return self.player.video_info['total_frames']
        return 0

    def toggle_play(self):
        """Play/Pause toggle"""
        if not self.player.video_info:
            return

        self.playing = not self.playing
        self.play_btn_text.set(i18n.get('pause') if self.playing else i18n.get('play'))

        if self.playing:
            self.play_loop()

    def play_loop(self):
        """Playback loop"""
        if not self.playing:
            return

        if self.player.current_frame < self.get_total_frames() - 1:
            self.next_frame()

            fps = self.player.video_info['fps']
            delay = int(1000 / (fps * self.play_speed))
            delay = max(10, delay)

            self.root.after(delay, self.play_loop)
        else:
            self.playing = False
            self.play_btn_text.set(i18n.get('play'))

    def set_speed(self, speed_str):
        """Set playback speed"""
        self.play_speed = float(speed_str.replace('x', ''))
        self.speed_var.set(speed_str)

    def toggle_current_frame(self):
        """Toggle current frame selection"""
        if not self.player.video_info:
            return

        frame = self.player.current_frame
        if frame in self.player.selected_frames:
            self.player.selected_frames.remove(frame)
        else:
            self.player.selected_frames.add(frame)

        self.update_frame_list()
        self.display_frame(frame)

    def update_frame_list(self):
        """Update selected frames list"""
        self.frame_listbox.delete(0, tk.END)
        if not self.player.video_info:
            return
        for frame in sorted(self.player.selected_frames):
            time_sec = frame / self.player.video_info['fps']
            text = i18n.get('frame_fmt').format(f=frame + 1, t=time_sec)
            self.frame_listbox.insert(tk.END, text)

    def goto_selected_frame(self, event):
        """Go to frame selected in list"""
        selection = self.frame_listbox.curselection()
        if selection:
            frames = sorted(self.player.selected_frames)
            frame = frames[selection[0]]
            self.display_frame(frame)

    def remove_selected_frame(self):
        """Remove frame from selection"""
        selection = self.frame_listbox.curselection()
        if selection:
            frames = sorted(self.player.selected_frames)
            frame = frames[selection[0]]
            self.player.selected_frames.discard(frame)
            self.update_frame_list()
            self.display_frame(self.player.current_frame)

    def clear_selected_frames(self):
        """Clear all selected frames"""
        self.player.selected_frames.clear()
        self.update_frame_list()
        self.display_frame(self.player.current_frame)

    def export_current_frame(self):
        """Export current frame"""
        if not self.player.video_info:
            messagebox.showwarning("Warning", i18n.get('no_video'))
            return

        path = filedialog.asksaveasfilename(
            title=i18n.get('save_frame'),
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")],
            initialfile=f"frame_{self.player.current_frame + 1:06d}.png"
        )

        if path:
            img = self.player.get_frame_image(self.player.current_frame)
            if img:
                img.save(path)
                self.status_var.set(i18n.get('exported') + os.path.basename(path))

    def export_selected_frames(self):
        """Export selected frames"""
        if not self.player.selected_frames:
            messagebox.showwarning("Warning", i18n.get('no_frames'))
            return

        folder = filedialog.askdirectory(title=i18n.get('select_folder'))
        if folder:
            count = 0
            for frame in sorted(self.player.selected_frames):
                img = self.player.get_frame_image(frame)
                if img:
                    path = os.path.join(folder, f"frame_{frame + 1:06d}.png")
                    img.save(path)
                    count += 1

            self.status_var.set(i18n.get('exported_n').format(n=count) + folder)

    def export_gif(self):
        """Export GIF"""
        if not self.player.selected_frames:
            messagebox.showwarning("Warning", i18n.get('no_frames_gif'))
            return

        dialog = GifExportDialog(self.root, self.colors, len(self.player.selected_frames))
        if dialog.result:
            path = filedialog.asksaveasfilename(
                title=i18n.get('save_gif'),
                defaultextension=".gif",
                filetypes=[("GIF", "*.gif")],
                initialfile="output.gif"
            )

            if path:
                self.status_var.set(i18n.get('generating_gif'))
                self.root.update()

                image_paths = []
                temp_dir = tempfile.mkdtemp(prefix='gif_export_')

                for i, frame in enumerate(sorted(self.player.selected_frames)):
                    img = self.player.get_frame_image(frame)
                    if img:
                        temp_path = os.path.join(temp_dir, f'{i:04d}.png')
                        img.save(temp_path)
                        image_paths.append(temp_path)

                success = self.player.ffmpeg.create_gif(
                    image_paths, path,
                    fps=dialog.result['fps'],
                    width=dialog.result['width'],
                    loop=dialog.result['loop']
                )

                shutil.rmtree(temp_dir, ignore_errors=True)

                if success:
                    size_kb = os.path.getsize(path) / 1024
                    self.status_var.set(f"{i18n.get('gif_saved')}{os.path.basename(path)} ({size_kb:.1f} KB)")
                else:
                    messagebox.showerror("Error", i18n.get('gif_failed'))

    def on_close(self):
        """Close application"""
        self.playing = False
        self.player.cleanup()
        self.root.destroy()


# ============================================================
# GIF Export Dialog
# ============================================================

class GifExportDialog:
    """GIF export settings dialog"""

    def __init__(self, parent, colors, frame_count):
        self.result = None
        self.colors = colors

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(i18n.get('gif_settings'))
        self.dialog.geometry("360x320")
        self.dialog.configure(bg=colors['bg'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.dialog.geometry(f"+{parent.winfo_x() + 200}+{parent.winfo_y() + 150}")

        self.create_widgets(frame_count)

        self.dialog.wait_window()

    def create_widgets(self, frame_count):
        """Create dialog widgets"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(frame, text=i18n.get('gif_params'), font=('Microsoft YaHei', 12, 'bold'))
        title.pack(pady=(0, 20))

        info = ttk.Label(frame, text=i18n.get('frame_count') + str(frame_count),
                        foreground=self.colors['text_dim'])
        info.pack(pady=(0, 15))

        # FPS
        fps_frame = ttk.Frame(frame)
        fps_frame.pack(fill=tk.X, pady=5)
        ttk.Label(fps_frame, text=i18n.get('fps')).pack(side=tk.LEFT)
        self.fps_var = tk.IntVar(value=10)
        fps_spin = ttk.Spinbox(fps_frame, from_=1, to=30, textvariable=self.fps_var, width=8)
        fps_spin.pack(side=tk.RIGHT)

        # Width
        width_frame = ttk.Frame(frame)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text=i18n.get('width')).pack(side=tk.LEFT)
        self.width_var = tk.IntVar(value=240)
        width_spin = ttk.Spinbox(width_frame, from_=50, to=1920, textvariable=self.width_var, width=8)
        width_spin.pack(side=tk.RIGHT)

        # Presets
        preset_frame = ttk.Frame(frame)
        preset_frame.pack(fill=tk.X, pady=10)
        ttk.Label(preset_frame, text=i18n.get('preset')).pack(side=tk.LEFT)

        presets = {
            i18n.get('wechat'): (240, 10),
            i18n.get('qq'): (200, 8),
            i18n.get('general'): (320, 12)
        }

        for name, (w, f) in presets.items():
            btn = ttk.Button(preset_frame, text=name, width=8,
                           command=lambda w=w, f=f: self.apply_preset(w, f))
            btn.pack(side=tk.LEFT, padx=2)

        # Loop
        loop_frame = ttk.Frame(frame)
        loop_frame.pack(fill=tk.X, pady=5)
        ttk.Label(loop_frame, text=i18n.get('loop')).pack(side=tk.LEFT)
        ttk.Label(loop_frame, text=i18n.get('loop_hint'), foreground=self.colors['text_dim']).pack(side=tk.RIGHT)
        self.loop_var = tk.IntVar(value=0)
        loop_spin = ttk.Spinbox(loop_frame, from_=0, to=100, textvariable=self.loop_var, width=8)
        loop_spin.pack(side=tk.RIGHT, padx=5)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_frame, text=i18n.get('cancel'), command=self.dialog.destroy).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text=i18n.get('export'), style='Accent.TButton',
                  command=self.confirm).pack(side=tk.RIGHT)

    def apply_preset(self, width, fps):
        """Apply preset"""
        self.width_var.set(width)
        self.fps_var.set(fps)

    def confirm(self):
        """Confirm export"""
        self.result = {
            'fps': self.fps_var.get(),
            'width': self.width_var.get(),
            'loop': self.loop_var.get()
        }
        self.dialog.destroy()


# ============================================================
# Entry Point
# ============================================================

def main():
    root = tk.Tk()
    app = RonVideo2PicApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == '__main__':
    main()
