import os
import tempfile
import numpy

from multiprocessing import Pool
from typing import Tuple
from moviepy.editor import AudioFileClip, ImageSequenceClip, VideoFileClip
from moviepy.video.fx.blackwhite import blackwhite
from PIL import Image, ImageDraw, ImageFont
from pytube import YouTube
from tqdm import tqdm


class ASCIIClip:
    default_font = os.path.join(os.path.dirname(__file__), "moby.ttf")
    supported_video_formats = ('.mp4', '.avi', '.mov', '.flv', '.mkv')
    supported_image_formats = ('.png', '.jpg', '.jpeg', '.bmp')

    def __init__(self, chunk: Tuple[int, int], chars: Tuple, gsv: list[float, float, float], compression: int, force_aspect_ratio: bool,
                 quality: str, preset: str, verbose: bool, font_size: int, font_color: Tuple[int, int, int], font: str = default_font) -> None:
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
        self.font_size = font_size
        self.font_color = font_color
        self.force_aspect_ratio = force_aspect_ratio
        self.compression = compression
        self.quality = quality
        self.gsv = gsv
        self.preset = preset
        self.verbose = verbose

    @property
    def _maximum_luminosity(self):
        return int(self.chunk[0]*self.chunk[1]*255*3/len(self.chars))

    @staticmethod
    def _cut(clip: VideoFileClip | AudioFileClip, segment: Tuple[int, int] | int) -> VideoFileClip | numpy.ndarray:
        if isinstance(segment, int):
            if segment > clip.duration:
                raise ValueError(
                    f"Error: Segment values [{segment}] should be smaller than the video duration [{clip.duration}].")

            return clip.get_frame(segment)
        else:
            if segment != (None, None):
                if segment[0] is None:
                    segment[0] = 0
                if segment[1] is None:
                    segment[1] = clip.duration

                if segment[0] > clip.duration or segment[1] > clip.duration:
                    raise ValueError(
                        f"Error: Segment values [{segment[0]}:{segment[1]}] should be smaller than the video duration [{clip.duration}].")

                return clip.subclip(*segment)
            else:
                return clip

    @staticmethod
    def _calculate_aspect_ratio(width: int, height: int) -> Tuple[int, int]:
        def gcd(a: int, b: int):
            return a if b == 0 else gcd(b, a % b)

        r = gcd(width, height)
        x = int(width / r)
        y = int(height / r)

        return (x, y)

    @staticmethod
    def _image_to_greyscale(image: numpy.ndarray, gsv: list[float, float, float]) -> numpy.ndarray:
        R, G, B = 1.0*numpy.array(gsv)/sum(gsv)
        image = (R*image[:, :, 0] + G*image[:, :, 1] + B*image[:, :, 2])
        return numpy.dstack(3*[image]).astype('uint8')

    @staticmethod
    def _image_remove_alpha(image: Image) -> Image:
        image = image.convert('RGBA')
        background = Image.new('RGBA', image.size, (255, 255, 255))
        image = Image.alpha_composite(background, image).convert("RGB")
        background.close()

        return image

    @staticmethod
    def _image_resize(image: Image, height: int) -> Image:
        h = int(height)
        w = int((h * image.width) / image.height)

        return image.resize((w, h), Image.ANTIALIAS)

    @staticmethod
    def _frame_to_image(data: numpy.ndarray, width: int, height: int, fps: int, duration: int, destination: str, frame: int, chunk: Tuple[int, int],
                        chars: Tuple, compression: int, font: str, font_size: str, font_color: str, maximum_luminosity: int, file_name: str = '', verbose: bool = False) -> None:
        image = Image.new(mode="RGB", size=(
            int((width*font_size)/chunk[0]), int((height*font_size)/chunk[1])))
        drawer = ImageDraw.Draw(image)

        if verbose:
            bar = tqdm(total=int(height/chunk[1]))

        for y in range(0, int(height/chunk[1])):
            line = ""
            if verbose:
                bar.update()

            for x in range(0, int(width/chunk[0])):

                y1, y2, x1, x2 = chunk[1]*y, chunk[1] + \
                    chunk[1]*y, chunk[0]*x, chunk[0]+chunk[0]*x
                for i in range(0, len(chars)):
                    if maximum_luminosity*(i) <= data[y1:y2, x1:x2].sum() <= maximum_luminosity*(i+1):
                        line += chars[i]
                        break

            drawer.text((0, y*font_size), line, fill=font_color,
                        font=ImageFont.truetype(font, font_size))

        if not file_name:
            name = f"frame_{str(frame).zfill(len(str(fps*duration)))}.png"
        else:
            name = f"{file_name}.png"

        if verbose:
            bar.update()
            bar.close()
            print(
                f"ASCIIClip: Saving image to the destination folder [{destination}].")

        image.save(f"{destination}/{name}", "PNG",
                   optimize=False, compress_level=compression)
        image.close()

        if verbose:
            print(
                f"ASCIIClip: Image [{name}] has been successfully created.")

    def _print(self, message: str) -> None:
        if self.verbose:
            print(message)

    def _create_temp(self) -> str:
        temp = tempfile.mkdtemp()
        self._print(
            f"ASCIIClip: Initializing temporary folder [{temp}].")

        return temp

    def _cleanup(self, temp: str) -> None:
        for fn in os.listdir(temp):
            os.remove(f"{temp}/{fn}")

        self._print(
            f"ASCIIClip: Temporary files have been removed.")

    def _apply_preset(self, width, height) -> None:
        if self.preset is not None:
            self.font = self.default_font
            ar = self._calculate_aspect_ratio(width, height)
            if ar == (16, 9):
                if self.preset == 720:
                    self.chunk = (2, 2)
                    self.font_size = 4
                if self.preset == 1080:
                    self.chunk = (2, 2)
                    self.font_size = 6
            if ar == (4, 3):
                if self.preset == 720:
                    self.chunk = (3, 3)
                    self.font_size = 6
                if self.preset == 1080:
                    self.chunk = (3, 3)
                    self.font_size = 9

    def _source_processing(self, source: str, temp: str, destination: str, segment: Tuple[int, int] | int, mute: bool) -> Tuple[VideoFileClip | numpy.ndarray, AudioFileClip]:
        visuals, audio = None, None

        if os.path.exists(destination):
            if not os.access(destination, os.W_OK) or destination == "/":
                raise OSError(
                    f"Error: Destination folder is not writable.")
        else:
            os.makedirs(destination, exist_ok=True)

        if "youtube.com" in source:
            self._print(
                f"ASCIIClip: Processing video from YouTube [{source}].")
            visuals = self._cut(blackwhite(VideoFileClip(YouTube(source).streams.filter(
                res="360p" if self.preset is not None else f"{self.quality}p"
            ).first().download(output_path=temp, filename="yt.mp4")), RGB=self.gsv), segment)

            if not mute and not isinstance(segment, int):
                self._print(
                    f"ASCIIClip: Processing audio from YouTube [{source}].")
                audio = self._cut(AudioFileClip(YouTube(source).streams.filter(
                    only_audio=True).first().download(output_path=temp, filename="yt.mp3")), segment)
        else:
            if not os.path.exists(source) or not os.access(source, os.R_OK):
                raise OSError(
                    f"Error: Source file is not readable.")

            if not source.lower().endswith(self.supported_video_formats + self.supported_image_formats):
                raise OSError(
                    f"Error: Only file types such as {self.supported_video_formats + self.supported_image_formats} are supported.")

            if source.lower().endswith(self.supported_video_formats):
                self._print(
                    f"ASCIIClip: Processing video [{source}].")
                visuals = self._cut(blackwhite(VideoFileClip(
                    source).resize(height=int(self.quality)), RGB=self.gsv), segment)

                if not mute and not isinstance(segment, int):
                    self._print(
                        f"ASCIIClip: Processing audio [{source}].")
                    audio = self._cut(AudioFileClip(source), segment)
            if source.lower().endswith(self.supported_image_formats):
                self._print(
                    f"ASCIIClip: Processing image [{source}].")

                visuals = self._image_to_greyscale(numpy.array(self._image_resize(
                    self._image_remove_alpha(Image.open(source)), self.quality)), self.gsv)
        if isinstance(visuals, VideoFileClip):
            if visuals.w % self.chunk[0] != 0:
                raise ValueError(
                    f"Error: Source width must be divisible by chunk width ({visuals.w}px).")
            if visuals.h % self.chunk[1] != 0:
                raise ValueError(
                    f"Error: Source height must be divisible by chunk height ({visuals.h}px).")

        return (visuals, audio)

    def _video_to_sequence(self, video: VideoFileClip, temp: str, threads: int) -> None:
        self._print(
            f"ASCIIClip: Generating an ASCII copy of each frame.")

        def update(*a):
            if self.verbose:
                bar.update()

        if self.verbose:
            bar = tqdm(total=int(video.fps*video.duration))

        frame = 1
        pool = Pool(processes=threads)
        for data in video.iter_frames(logger=None):
            pool.apply_async(self._frame_to_image, args=(data, video.w, video.h, video.fps, video.duration, temp, frame, self.chunk,
                             self.chars, self.compression, self.font, self.font_size, self.font_color, self._maximum_luminosity), callback=update)
            frame += 1

        pool.close()
        pool.join()
        bar.close()

    def _sequence_to_video(self, temp: str, destination: str, name: str, audio: AudioFileClip, fps: int) -> None:
        imgseq = [os.path.join(temp, img)
                  for img in os.listdir(temp)
                  if img.endswith(".png")]

        output = ImageSequenceClip(imgseq, fps=fps)
        output = output.set_audio(audio)

        if self.force_aspect_ratio:
            if output.w < int(output.h/9*16):
                margin = int((int(output.h/9*16)-output.w)/2)
                output = output.margin(left=margin, right=margin, opacity=0)

        self._print(
            f"ASCIIClip: Saving video to the destination folder [{destination}].")

        output.write_videofile(f"{destination}/{name}.mp4", logger=None)
        output.close()

        self._print(
            f"ASCIIClip: Video [{name}.mp4] has been successfully created.")

    def generate(self, source: str, destination: str, file_name: str, segment: Tuple[int, int] | int, threads: int, mute: bool) -> None:
        temp = self._create_temp()

        visuals, audio = self._source_processing(
            source, temp, destination, segment, mute)

        try:
            if isinstance(visuals, numpy.ndarray):
                # Routine for images
                self._apply_preset(visuals.shape[1], visuals.shape[0])
                self._frame_to_image(visuals, visuals.shape[1], visuals.shape[0], 1, 1, destination, segment, self.chunk,
                                     self.chars, self.compression, self.font, self.font_size, self.font_color, self._maximum_luminosity, file_name, verbose=True)
            else:
                # Routine for videos
                self._apply_preset(visuals.w, visuals.h)
                self._video_to_sequence(visuals, temp, threads)
                self._sequence_to_video(
                    temp, destination, file_name, audio, visuals.fps)
        finally:
            if isinstance(visuals, VideoFileClip):
                visuals.close()
            if isinstance(audio, AudioFileClip):
                audio.close()
            self._cleanup(temp)
