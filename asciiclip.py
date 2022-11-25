import os
import tempfile

from tqdm import tqdm
from typing import Tuple
from pytube import YouTube
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip, VideoFileClip
from moviepy.video.fx.blackwhite import blackwhite
from multiprocessing import cpu_count


class ASCIIClip:
    def __init__(self, chunk=(4, 3), chars=(".", ";", "*", "u", "o"), font="moby.ttf", fontsize=6, fontcolor=(255, 255, 255), compression=0, forceaspectratio=True, forceconsistency=True, sourcequality="480p", gsv=[0.299, 0.587, 0.114]):
        if compression not in range(0, 9):
            raise ValueError(
                "ERR: Compression level must be greater than 0 (no compression) and less than 9 (max compression)")
        if len(chars) not in [2, 3, 5, 9]:
            raise ValueError(
                "ERR: Number of grey levels must be set to 2, 3, 5 or 9")

        self.chunk = chunk
        self.chars = chars
        self.font = font
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        self.compression = compression
        self.forceaspectratio = forceaspectratio
        self.forceconsistency = forceconsistency
        self.sourcequality = sourcequality
        self.gsv = gsv

    @property
    def _maximumluminosity(self):
        return int(self.chunk[0]*self.chunk[1]*255*3/len(self.chars))

    @staticmethod
    def _cut(source: VideoFileClip, segment: Tuple[int, int]) -> VideoFileClip:
        if segment != (None, None):
            if segment[0] is None:
                segment[0] = 0
            if segment[1] is None:
                segment[1] = source.duration
            return source.subclip(*segment)
        else:
            return source

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
    def _frame_to_image(data: any, width: int, height: int, fps: int, duration: int, destination: str, frame: int, chunk: Tuple[int, int], chars: Tuple,
                        compression: int, font: str, fontsize: str, fontcolor: str, maximumluminosity: int) -> None:

        im = Image.new(mode="RGB", size=(int(width/chunk[0])*fontsize, int(height/chunk[1])*fontsize))
        di = ImageDraw.Draw(im)

        for y in range(0, int(height/chunk[1])):
            line = ""
            for x in range(0, int(width/chunk[0])):
                y1, y2, x1, x2 = chunk[1]*y, chunk[1]+chunk[1]*y, chunk[0]*x, chunk[0]+chunk[0]*x
                for i in range(0, len(chars)):
                    if maximumluminosity*(i) <= data[y1:y2, x1:x2].sum() <= maximumluminosity*(i+1):
                        line += chars[i]
                        break

            di.text((0, y*fontsize), line, fill=fontcolor, font=ImageFont.truetype(font, fontsize))

        nm = destination + "/frame_" + str(frame).zfill(len(str(fps*duration))) + ".png"
        im.save(nm, "PNG", optimize=False, compress_level=compression)
        im.close()

    def _video_to_sequence(self, source: VideoFileClip, temp: str, threads: int, progress: bool = True) -> None:
        def update(*a):
            if progress:
                bar.update()

        if progress:
            bar = tqdm(total=int(source.fps*source.duration))

        pool = Pool(processes=threads)

        frame = 1
        for data in source.iter_frames(logger=None):
            pool.apply_async(self._frame_to_image, args=(data, source.w, source.h, source.fps, source.duration, temp, frame, self.chunk,
                             self.chars, self.compression, self.font, self.fontsize, self.fontcolor, self._maximumluminosity), callback=update)
            frame += 1

        pool.close()
        pool.join()

    def _sequence_to_video(self, source: VideoFileClip, temp: str, destination: str, name: str) -> None:
        imgseq = [os.path.join(temp, img)
                  for img in os.listdir(temp)
                  if img.endswith(".png")]

        output = ImageSequenceClip(imgseq, fps=source.fps)
        output = output.set_audio(source.audio)

        if self.forceaspectratio:
            if output.w < int(output.h/9*16):
                mrg = int((int(output.h/9*16)-output.w)/2)
                output = output.margin(left=mrg, right=mrg, opacity=0)

        output.write_videofile(f"{destination}/{name}.mp4", logger=None)

    def generate(self, link: str, destination: str, name: str = "ascii", segment: Tuple[int, int] = (None, None), threads: int = cpu_count(), verbose: bool = True, progress: bool = True) -> None:
        if os.path.exists(destination):
            if not os.access(destination, os.W_OK):
                raise OSError(
                    f"ERR: Destination folder is not writable")
        else:
            os.makedirs(destination, exist_ok=True)

        temp = tempfile.mkdtemp()
        self._print(f"ASCIIClip - Temporary folder for video and frames: {temp}", verbose)

        try:
            self._print(f"ASCIIClip - Downloading video from YouTube", verbose)
            source = blackwhite(self._cut(VideoFileClip(YouTube(link).streams.filter(
                res=self.sourcequality).first().download(output_path=temp, filename="yt.mp4")), segment), RGB=self.gsv)

            if source.w % self.chunk[0] != 0:
                raise ValueError(
                    f"ERR: Source width must be divisible by chunk width ({source.w})px")
            if source.h % self.chunk[1] != 0:
                raise ValueError(
                    f"ERR: Source height must be divisible by chunk height ({source.h}px)")

            if self.forceconsistency:
                ar = self._calculate_aspect_ratio(source.w, source.h)
                if ar == (16, 9):
                    self.chunk = (4, 3)
                if ar == (4, 3):
                    self.chunk = (3, 3)
        except:
            raise RuntimeError(
                f"ERR: An unexpected error occurred while processing the video")

        try:
            self._print(f"ASCIIClip - Generating an ASCII copy of each frame", verbose)
            self._video_to_sequence(source, temp, threads, progress)

            self._print(f"ASCIIClip - Saving video to the destination folder: {destination}", verbose)
            self._sequence_to_video(source, temp, destination, name)
        finally:
            source.close()
            self._cleanup(temp)

        self._print(f"ASCIIClip - Video [{name}.mp4] has been successfully created, temporary files have been deleted", verbose)


if __name__ == '__main__':
    ASCIIClip().generate("https://www.youtube.com/watch?v=_LLCz1FCWrY", "/", segment=(65, 69))
