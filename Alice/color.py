import cv2
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

video_path_1 = "../../videos/butterfly-cropped.mp4"
video_clip_1 = VideoFileClip(video_path_1)

brightness_factor = 0.9  # Adjust as needed (higher values increase brightness)

color_adjusted_clip = video_clip_1.fx(vfx.colorx, brightness_factor)
final_clip = color_adjusted_clip.fx(vfx.lum_contrast, lum=150, contrast=0.3, contrast_thr=300)

for frame in final_clip.iter_frames(fps=final_clip.fps):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR
    cv2.imshow("Final Clip", frame)
    
    # Check for the 'q' key press to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
