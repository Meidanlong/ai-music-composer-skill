"""音乐生成API客户端：多服务商统一封装"""

import time
import requests


class MusicAPIClient:
    """
    音乐生成API客户端
    支持服务商：歌歌AI(getge) / 天谱乐(tianpule) / 音潮(yinchao)
    可扩展接入更多国内音乐生成服务
    """

    PROVIDERS = {
        "getge": {
            "base_url": "https://api.getgeai.com/v1",
            "create_path": "/music/generate",
            "task_path": "/task/{task_id}",
        },
        "tianpule": {
            "base_url": "https://api.tianpule.com/v1",
            "create_path": "/song/create",
            "task_path": "/task/{task_id}",
        },
        "yinchao": {
            "base_url": "https://api.yinchaoai.com/v1",
            "create_path": "/audio/create",
            "task_path": "/task/{task_id}",
        },
    }

    def __init__(self, provider: str, api_key: str, poll_interval: int = 5, poll_timeout: int = 600):
        if provider not in self.PROVIDERS:
            raise ValueError(f"不支持的服务商: {provider}，可选: {list(self.PROVIDERS.keys())}")
        self.provider = provider
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout
        self.config = self.PROVIDERS[provider]

    def submit_generate_task(self, midi_motif: dict, lyric: str, bpm: float, style: str) -> str:
        """
        提交音乐生成任务（异步）

        Args:
            midi_motif: 主旋律MIDI动机数据
            lyric: 结构化歌词JSON字符串
            bpm: 歌曲速度
            style: 曲风

        Returns:
            任务ID
        """
        url = f"{self.config['base_url']}{self.config['create_path']}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "bpm": bpm,
            "style": style,
            "lyric": lyric,
            "midi_motif": midi_motif,
            "format": "mp3",
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        task_id = data.get("task_id") or data.get("data", {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"API返回中未找到task_id: {data}")
        return task_id

    def poll_task(self, task_id: str) -> str:
        """
        轮询任务状态直到完成

        Args:
            task_id: 任务ID

        Returns:
            成品音频URL

        Raises:
            TimeoutError: 轮询超时
            RuntimeError: 任务失败
        """
        url = f"{self.config['base_url']}{self.config['task_path'].format(task_id=task_id)}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        elapsed = 0
        while elapsed < self.poll_timeout:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status") or data.get("data", {}).get("status")

            if status == "success" or status == "completed":
                audio_url = data.get("audio_url") or data.get("data", {}).get("audio_url")
                if not audio_url:
                    raise RuntimeError(f"任务完成但未返回音频URL: {data}")
                return audio_url

            if status == "failed":
                error_msg = data.get("error") or data.get("msg") or "未知错误"
                raise RuntimeError(f"音乐生成任务失败: {error_msg}")

            time.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(f"任务轮询超时（{self.poll_timeout}秒）: {task_id}")

    def generate(self, midi_motif: dict, lyric: str, bpm: float, style: str) -> str:
        """
        一站式生成：提交任务 + 轮询等待结果

        Returns:
            成品音频URL
        """
        task_id = self.submit_generate_task(midi_motif, lyric, bpm, style)
        return self.poll_task(task_id)
