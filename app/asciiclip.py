import os
import tempfile

from multiprocessing import Pool
from typing import Tuple
from moviepy.editor import AudioFileClip, ImageSequenceClip, VideoFileClip
from moviepy.video.fx.blackwhite import blackwhite
from numpy import ndarray
from PIL import Image, ImageDraw, ImageFont
from pytube import YouTube
from tqdm import tqdm


class ASCIIClip:
    defaultfont = os.path.join(os.path.dirname(__file__), "moby.ttf")

    def __init__(self, chunk: Tuple[int, int], chars: Tuple, gsv: list[int, int, int], compression: int, forceaspectratio: bool,
                 quality: str, preset: str, fontsize: int, fontcolor: Tuple[int, int, int], font: str = defaultfont) -> None:
        if compression not in range(0, 9):
            raise ValueError(
                f"Error: Compression level must be greater than 0 (no compression) and less than 9 (max compression).")
        if preset not in [None, '720', '1080']:
            raise ValueError(
                f"Error: Preset can only be set to 720 or 1080.")
        if quality not in ['360', '480', '720', '1080']:
            raise ValueError(
                f"Error: Source quality can only be set to 360, 480, 720 or 1080.")
        if len(chars) not in [2, 3, 5, 9]:
            raise ValueError(
                f"Error: Char tuple must be set to 2, 3, 5 or 9 ellements.")

        self.chars = chars
        self.chunk = chunk
        self.font = font
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        self.compression = compression
        self.forceaspectratio = forceaspectratio
        self.quality = quality
        self.gsv = gsv
        self.preset = preset

    @property
    def _maximumluminosity(self):
        return int(self.chunk[0]*self.chunk[1]*255*3/len(self.chars))

    @staticmethod
    def _cut(clip: VideoFileClip | AudioFileClip, segment: Tuple[int, int]) -> VideoFileClip:
        if segment != (None, None):
            if segment[0] is None:
                segment[0] = 0
            if segment[1] is None:
                segment[1] = clip.duration

            if segment[0] > clip.duration or segment[1] > clip.duration:
                raise ValueError(
                    f"Error: Segment values should be smaller than the video duration.")

            return clip.subclip(*segment)
        else:
            return clip

    @staticmethod
    def _cleanup(temp: str) -> None:
        for fn in os.listdir(temp):
            os.remove(f"{temp}/{fn}")

    @staticmethod
    def _print(message: str, verbose: bool) -> None:
        if verbose:
            print(message)

    @staticmethod
    def _calculate_aspect_ratio(width: int, height: int) -> Tuple[int, int]:
        def gcd(a: int, b: int):
            return a if b == 0 else gcd(b, a % b)

        r = gcd(width, height)
        x = int(width / r)
        y = int(height / r)

        return (x, y)

    @staticmethod
    def _frame_to_image(data: ndarray, width: int, height: int, fps: int, duration: int, destination: str, frame: int, chunk: Tuple[int, int],
                        chars: Tuple, compression: int, font: str, fontsize: str, fontcolor: str, maximumluminosity: int) -> None:
        im = Image.new(mode="RGB", size=(
            int((width*fontsize)/chunk[0]), int((height*fontsize)/chunk[1])))
        di = ImageDraw.Draw(im)

        for y in range(0, int(height/chunk[1])):
            line = ""
            for x in range(0, int(width/chunk[0])):
                y1, y2, x1, x2 = chunk[1]*y, chunk[1] + \
                    chunk[1]*y, chunk[0]*x, chunk[0]+chunk[0]*x
                for i in range(0, len(chars)):
                    if maximumluminosity*(i) <= data[y1:y2, x1:x2].sum() <= maximumluminosity*(i+1):
                        line += chars[i]
                        break

            di.text((0, y*fontsize), line, fill=fontcolor,
                    font=ImageFont.truetype(font, fontsize))

        nm = destination + "/frame_" + \
            str(frame).zfill(len(str(fps*duration))) + ".png"

        im.save(nm, "PNG", optimize=False, compress_level=compression)
        im.close()

    def _apply_preset(self, width, height) -> None:
        if self.preset is not None:
            self.font = self.defaultfont
            ar = self._calculate_aspect_ratio(width, height)
            if ar == (16, 9):
                if self.preset == 720:
                    self.chunk = (2, 2)
                    self.fontsize = 4
                if self.preset == 1080:
                    self.chunk = (2, 2)
                    self.fontsize = 6
            if ar == (4, 3):
                if self.preset == 720:
                    self.chunk = (3, 3)
                    self.fontsize = 6
                if self.preset == 1080:
                    self.chunk = (3, 3)
                    self.fontsize = 9

    def _video_to_sequence(self, video: VideoFileClip, temp: str, threads: int, progress: bool) -> None:
        def update(*a):
            if progress:
                bar.update()

        if progress:
            bar = tqdm(total=int(video.fps*video.duration))

        frame = 1
        pool = Pool(processes=threads)
        for data in video.iter_frames(logger=None):
            pool.apply_async(self._frame_to_image, args=(data, video.w, video.h, video.fps, video.duration, temp, frame, self.chunk,
                             self.chars, self.compression, self.font, self.fontsize, self.fontcolor, self._maximumluminosity), callback=update)
            frame += 1

        pool.close()
        pool.join()

    def _sequence_to_video(self, temp: str, destination: str, name: str, audio: AudioFileClip, fps: int) -> ImageSequenceClip:
        imgseq = [os.path.join(temp, img)
                  for img in os.listdir(temp)
                  if img.endswith(".png")]

        output = ImageSequenceClip(imgseq, fps=fps)
        output = output.set_audio(audio)

        if self.forceaspectratio:
            if output.w < int(output.h/9*16):
                mrg = int((int(output.h/9*16)-output.w)/2)
                output = output.margin(left=mrg, right=mrg, opacity=0)

        output.write_videofile(f"{destination}/{name}.mp4", logger=None)
        return output

    def generate_video(self, source: str, destination: str, filename: str, segment: Tuple[int, int], threads: int, verbose: bool, progress: bool) -> ImageSequenceClip:
        if os.path.exists(destination):
            if not os.access(destination, os.W_OK) or destination == "/":
                raise OSError(
                    f"Error: Destination folder is not writable.")
        else:
            os.makedirs(destination, exist_ok=True)

        temp = tempfile.mkdtemp()
        self._print(
            f"ASCIIClip: Temporary folder for video and frames: {temp}.", verbose)

        if "youtube.com" in source:
            self._print(
                f"ASCIIClip: Processing video from YouTube [{source}].", verbose)
            video = blackwhite(self._cut(VideoFileClip(YouTube(source).streams.filter(
                res="360p" if self.preset is not None else f"{self.quality}p"
            ).first().download(output_path=temp, filename="yt.mp4")), segment), RGB=self.gsv)

            self._print(
                f"ASCIIClip: Processing audio from YouTube [{source}].", verbose)
            audio = self._cut(AudioFileClip(YouTube(source).streams.filter(
                only_audio=True).first().download(output_path=temp, filename="yt.mp3")), segment)
        else:
            if not os.path.exists(source) or not os.access(source, os.R_OK):
                raise OSError(
                    f"Error: Source file is not readable.")

            self._print(
                f"ASCIIClip: Processing video [{source}].", verbose)
            video = blackwhite(
                self._cut(VideoFileClip(source), segment).resize(height=int(self.quality)), RGB=self.gsv)

            self._print(
                f"ASCIIClip: Processing audio [{source}].", verbose)
            audio = self._cut(AudioFileClip(source), segment)

        if video.w % self.chunk[0] != 0:
            raise ValueError(
                f"Error: Source width must be divisible by chunk width ({video.w})px).")
        if video.h % self.chunk[1] != 0:
            raise ValueError(
                f"Error: Source height must be divisible by chunk height ({video.h}px).")

        try:
            self._print(
                f"ASCIIClip: Generating an ASCII copy of each frame.", verbose)
            self._apply_preset(video.w, video.h)
            self._video_to_sequence(video, temp, threads, progress)

            self._print(
                f"ASCIIClip: Saving video to the destination folder: {destination}.", verbose)
            output = self._sequence_to_video(
                temp, destination, filename, audio, video.fps)
        finally:
            video.close()
            audio.close()
            self._cleanup(temp)

        self._print(
            f"ASCIIClip: Video [{filename}.mp4] has been successfully created, temporary files have been deleted.", verbose)

        return output
