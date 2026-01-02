# RonVideo2Pic

Video Frame Browser & Exporter / 视频逐帧浏览与导出工具

**Author:** Ron  
**Homepage:** [Ron.Quest](https://ron.quest)

---

## Features / 功能

- Import any video format (MP4, AVI, MKV, MOV, WebM, etc.)
- Frame-by-frame manual browsing with precise control
- Multiple playback speeds (0.1x ~ 2x)
- Export current frame as image (PNG/JPG/BMP)
- Batch select and export frames
- Export GIF with platform presets (WeChat sticker, QQ emoji, etc.)
- Bilingual UI (Chinese / English)

---

- 支持导入任意格式视频 (MP4, AVI, MKV, MOV, WebM 等)
- 逐帧手动浏览，精确控制
- 多种播放速度 (0.1x ~ 2x)
- 导出当前帧为图片 (PNG/JPG/BMP)
- 批量选中帧并导出
- 导出 GIF 动图，内置平台预设 (微信表情包、QQ 表情等)
- 中英双语界面

---

## Requirements / 系统要求

- Windows 10/11
- Python 3.8+
- FFmpeg (bundled in `ffmpeg/` folder)

---

## Installation / 安装

### 1. Install Python dependencies / 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. FFmpeg

FFmpeg is bundled in the `ffmpeg/` folder. No additional setup required.

FFmpeg 已包含在 `ffmpeg/` 目录中，无需额外配置。

---

## Usage / 使用方法

### Start / 启动

Double-click `run.bat` or run: / 双击 `run.bat` 或运行:

```bash
python video2pic.py
```

### Keyboard Shortcuts / 快捷键

| Shortcut / 快捷键 | Function / 功能 |
|-------------------|-----------------|
| `Left` / `Right` | Previous / Next frame / 上一帧 / 下一帧 |
| `Space` | Select/deselect frame / 选中/取消选中帧 |
| `Enter` | Play/Pause / 播放/暂停 |
| `Home` / `End` | First/Last frame / 首帧/末帧 |
| `Ctrl+O` | Open video / 打开视频 |
| `Ctrl+S` | Export current frame / 导出当前帧 |
| `Ctrl+G` | Export GIF / 导出 GIF |

### Export GIF / 导出 GIF

1. Use `Space` key to select frames / 使用空格键选中帧
2. Click `Export GIF` button / 点击"导出 GIF"按钮
3. Choose preset or customize parameters: / 选择预设或自定义参数:
   - **WeChat / 微信表情包**: 240px, 10 FPS
   - **QQ**: 200px, 8 FPS
   - **General / 通用**: 320px, 12 FPS
4. Save file / 保存文件

---

## Project Structure / 目录结构

```
RonVideo2Pic/
├── video2pic.py      # Main program / 主程序
├── requirements.txt  # Python dependencies / Python 依赖
├── run.bat           # Launcher / 启动脚本
├── ffmpeg/           # FFmpeg binaries / FFmpeg 程序
│   ├── ffmpeg.exe
│   ├── ffprobe.exe
│   └── *.dll
└── README.md         # Documentation / 说明文档
```

---

## License

MIT License
