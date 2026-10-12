"""音频分析模块：提取BPM、节拍网格、主旋律MIDI动机"""

from pydub import AudioSegment


class AudioAnalyzer:
    """
    音频分析器：从标准化WAV中提取音乐特征
    当前为骨架实现，后续可接入 librosa + crepe 做真实音高检测
    """

    def __init__(self):
        pass

    def analyze(self, wav_path: str) -> dict:
        """
        分析音频文件，提取音乐特征

        Args:
            wav_path: 标准化WAV文件路径

        Returns:
            分析结果字典：
            - bpm: 预估速度
            - duration: 时长(秒)
            - beats: 节拍时间轴列表
            - midi_data: 主旋律MIDI动机（占位）
            - deviation_notes: 节奏/音准偏差标记
        """
        audio = AudioSegment.from_wav(wav_path)
        duration_sec = len(audio) / 1000

        # TODO: 接入 librosa 做真实BPM检测
        # 骨架版：基于默认BPM生成节拍时间轴
        estimated_bpm = self._estimate_bpm_skeleton(duration_sec)
        beats = self._gen_beat_timeline(estimated_bpm, duration_sec)

        return {
            "bpm": estimated_bpm,
            "duration": round(duration_sec, 2),
            "beats": beats,
            "bars": self._beats_to_bars(beats),
            "midi_data": {
                "notes": [],
                "bpm": estimated_bpm,
                "note": "骨架版：后续接入crepe实现真实音高提取",
            },
            "deviation_notes": [
                "骨架版：此处可扩展标记演奏节奏不稳的段落",
                "骨架版：此处可扩展标记音准偏移的音符",
            ],
            "analysis_note": "当前为骨架实现，生产环境请接入 librosa + crepe",
        }

    def _estimate_bpm_skeleton(self, duration_sec: float) -> int:
        """骨架版BPM预估：默认88，后续替换为librosa真实检测"""
        return 88

    def _gen_beat_timeline(self, bpm: int, total_sec: float) -> list[float]:
        """根据BPM生成节拍时间轴"""
        beat_gap = 60.0 / bpm
        timeline = []
        t = 0.0
        while t < total_sec:
            timeline.append(round(t, 3))
            t += beat_gap
        return timeline

    def _beats_to_bars(self, beats: list[float]) -> list[dict]:
        """将节拍列表转换为小节信息（4/4拍）"""
        bars = []
        for i in range(0, len(beats), 4):
            bar_beats = beats[i:i+4]
            if len(bar_beats) == 4:
                bars.append({
                    "bar_number": i // 4 + 1,
                    "start_time": bar_beats[0],
                    "end_time": bar_beats[-1],
                })
        return bars
