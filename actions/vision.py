import time
import base64
import threading
import cv2
import glob
import os
from io import BytesIO
from llm import get_llm_multimodal_output
from tts import edge_speak

def get_latest_video():
    """Hunts the PC for the most recent video file."""
    video_dir = os.path.join(os.path.expanduser("~"), "Videos", "Captures")
    if not os.path.exists(video_dir):
        return None
        
    try:
        files = glob.glob(os.path.join(video_dir, '*.mp4')) + glob.glob(os.path.join(video_dir, '*.mkv'))
        if not files: return None
        return max(files, key=os.path.getmtime)
    except Exception as e:
        print(f"⚠️ Media retrieval error: {e}")
        return None

def analyze_multimodal_view(parameters, response, player, session_memory):
    """The central routing hub for RUBE's optical inputs."""
    user_prompt = parameters.get("prompt", "Describe what you see.").strip()
    target = parameters.get("target", "camera").strip().lower()
    file_path = parameters.get("file_path", "").strip()
    
    print(f"👁️ RUBE Vision Matrix Active: Target='{target}', Prompt='{user_prompt}', File='{file_path}'")
    
    if file_path or target == "file":
        threading.Thread(target=_analyze_file, args=(file_path, user_prompt, player), daemon=True).start()
    elif target == "screen":
        threading.Thread(target=_analyze_screen, args=(user_prompt, player), daemon=True).start()
    elif target in ["latest_video", "video", "clip"]:
        threading.Thread(target=_analyze_video, args=(user_prompt, player, None), daemon=True).start()
    else:
        threading.Thread(target=_analyze_camera, args=(user_prompt, player), daemon=True).start()

def _analyze_file(file_path, user_prompt, player):
    print(f"📂 Accessing dropped file: {file_path}")
    file_path = file_path.replace('"', '').strip()
    
    if not os.path.exists(file_path):
        msg = f"Boss, I cannot locate the file at that path."
        edge_speak(msg, player)
        return
        
    ext = file_path.lower().split('.')[-1]
    
    if ext in ['mp4', 'mkv', 'avi', 'mov', 'webm']:
        _analyze_video(user_prompt, player, specific_path=file_path)
    elif ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp']:
        try:
            from PIL import Image
            img = Image.open(file_path)
            
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=75)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            visual_summary = get_llm_multimodal_output([img_str], user_prompt)
            edge_speak(visual_summary, player)
        except Exception as e:
            print(f"⚠️ IMAGE ERROR: {e}")
            msg = "I encountered a matrix error while trying to parse the image file."
            edge_speak(msg, player)
    else:
        msg = "Boss, that specific file format is currently incompatible with my visual cortex."
        edge_speak(msg, player)

def _analyze_screen(user_prompt, player):
    print("📸 Scanning user desktop...")
    time.sleep(1.0) 
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG", quality=80)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        visual_summary = get_llm_multimodal_output([img_str], user_prompt)
        edge_speak(visual_summary, player)
    except Exception as e:
        print(f"⚠️ SCREENSHOT ERROR: {e}")
        msg = "I encountered an error trying to capture your screen, boss."
        edge_speak(msg, player)

def _analyze_camera(user_prompt, player):
    print("📷 Accessing webcam feed...")
    time.sleep(1.2) 
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            msg = "Boss, I cannot activate the visual matrix. The webcam feed appears disconnected."
            edge_speak(msg, player)
            return
            
        ret, frame = cam.read()
        cam.release() 
        
        if not ret:
            msg = "Boss, I captured a corrupt visual frame."
            edge_speak(msg, player)
            return
            
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        visual_summary = get_llm_multimodal_output([image_base64], user_prompt)
        edge_speak(visual_summary, player)
    except Exception as e:
        print(f"⚠️ CAMERA ERROR: {e}")
        msg = "My camera module crashed during execution, boss."
        edge_speak(msg, player)

def _analyze_video(user_prompt, player, specific_path=None):
    print("🎞️ Ripping video frames for storyboard analysis...")
    video_path = specific_path if specific_path else get_latest_video()
    
    if not video_path:
        msg = "Boss, I could not find any recent videos to analyze."
        edge_speak(msg, player)
        return
        
    try:
        cam = cv2.VideoCapture(video_path)
        total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames_to_grab = 6
        step = max(1, total_frames // frames_to_grab)
        
        base64_frames = []
        for i in range(frames_to_grab):
            cam.set(cv2.CAP_PROP_POS_FRAMES, i * step)
            ret, frame = cam.read()
            if ret:
                frame = cv2.resize(frame, (1280, 720))
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                base64_frames.append(base64.b64encode(buffer).decode('utf-8'))
                
        cam.release()
        print(f"✅ Extracted {len(base64_frames)} frames from {os.path.basename(video_path)}.")
        
        prompt_override = f"I have extracted 6 sequential frames from a video. Based on the progression of these images, {user_prompt}"
        visual_summary = get_llm_multimodal_output(base64_frames, prompt_override)
        
        edge_speak(visual_summary, player)
    except Exception as e:
        print(f"⚠️ VIDEO PROCESSING ERROR: {e}")
        msg = "My visual matrix crashed while trying to parse the video file."
        edge_speak(msg, player)