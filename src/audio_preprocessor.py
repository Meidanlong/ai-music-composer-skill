"""音频预处理模块：自动格式探测与标准化转码"""

import os
import shutil
import ffmpeg
from pathlib import Path


class AudioPreprocessor:
    """
    音频预处理：将任意格式输入音频转码为统一标准格式
    输出：16bit PCM, 44.1kHz, 单声道 WAV
    """

    def __init__(self, tmp_dir: str = "./tmp", sample_rate: int = 44100, channels: int = 1):
        self.tmp_dir = Path(tmp_dir)
        self.tmp_dir.mkdir(exist_ok=True)
        self.sample_rate = sample_rate
        self.channels = channels

    def process(self, input_audio: str) -> str:
        """
        处理输入音频文件，输出标准化WAV路径

        Args:
            input_audio: 输入音频文件路径（支持mp3/m4a/flac/wav等）

        Returns:
            标准化后的WAV文件路径

        Raises:
            FileNotFoundError: 输入文件不存在
            RuntimeError: 转码失败
        """
        input_path = Path(input_audio)
        if not input_path.exists():
            raise FileNotFoundError(f"输入音频文件不存在: {input_audio}")

        out_path = str(self.tmp_dir / f"{input_path.stem}_standardized.wav")

        try:
            (
                ffmpeg
                .input(str(input_path))
                .output(
                    out_path,
                    format="wav",
                    acodec="pcm_s16le",
                    ar=str(self.sample_rate),
                    ac=str(self.channels),
                )
                .overwrite_output()
                .run(quiet=True)
            )
            return out_path
        except ffmpeg.Error as e:
            stderr = e.stderr.decode() if e.stderr else "unknown error"
            raise RuntimeError(f"音频转码失败: {stderr}") from e

    def get_audio_info(self, audio_path: str) -> dict:
        """获取音频文件基本信息"""
        try:
            probe = ffmpeg.probe(audio_path)
            stream = next(s for s in probe["streams"] if s["codec_type"] == "audio")
            return {
                "codec": stream.get("codec_name", "unknown"),
                "sample_rate": int(stream.get("sample_rate", 0)),
                "channels": stream.get("channels", 0),
                "duration": float(probe["format"].get("duration", 0)),
                "bit_rate": int(probe["format"].get("bit_rate", 0)),
            }
        except Exception as e:
            return {"error": str(e)}

    def clean_tmp(self):
        """清空临时目录，删除所有中间音频文件"""
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
            self.tmp_dir.mkdir(exist_ok=True)
