"""配置管理模块：从环境变量读取所有敏感配置"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """全局配置，所有密钥从环境变量读取，禁止硬编码"""

    # 豆包API
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
    DOUBAO_BASE_URL = os.getenv(
        "DOUBAO_BASE_URL",
        "https://ark.cn-beijing.volces.com/api/v3",
    )
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-pro-32k")

    # 通义千问API（可选）
    QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
    QWEN_BASE_URL = os.getenv(
        "QWEN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")

    # 音乐生成API
    MUSIC_API_PROVIDER = os.getenv("MUSIC_API_PROVIDER", "getge")
    MUSIC_API_KEY = os.getenv("MUSIC_API_KEY", "")

    # 音频参数
    AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
    AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))

    # 任务轮询
    TASK_POLL_INTERVAL = int(os.getenv("TASK_POLL_INTERVAL", "5"))
    TASK_POLL_TIMEOUT = int(os.getenv("TASK_POLL_TIMEOUT", "600"))

    @classmethod
    def validate(cls) -> list[str]:
        """校验必填配置，返回缺失项列表"""
        missing = []
        if not cls.DOUBAO_API_KEY:
            missing.append("DOUBAO_API_KEY")
        if not cls.MUSIC_API_KEY:
            missing.append("MUSIC_API_KEY")
        return missing
