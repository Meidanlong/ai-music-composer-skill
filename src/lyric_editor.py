"""歌词编辑模块：豆包主模型润色 + 通义千问全局校验"""

import json
import requests


class LyricEditor:
    """
    歌词编辑器：
    - 豆包API：负责语感、上口度、情感表达优化
    - 通义千问API（可选）：负责整首歌词结构一致性校验
    """

    def __init__(self, doubao_key: str, doubao_base_url: str = "", doubao_model: str = "doubao-pro-32k",
                 qwen_key: str = "", qwen_base_url: str = "", qwen_model: str = "qwen-plus"):
        self.doubao_key = doubao_key
        self.doubao_base_url = doubao_base_url.rstrip("/")
        self.doubao_model = doubao_model
        self.qwen_key = qwen_key
        self.qwen_base_url = qwen_base_url.rstrip("/")
        self.qwen_model = qwen_model

    def optimize_lyric(self, raw_lyric: str, bpm: float, style: str, duration: float = 180) -> dict:
        """
        第一轮歌词优化：基于原始歌词 + 音乐参数，生成结构化歌词

        Args:
            raw_lyric: 用户原始歌词
            bpm: 歌曲速度
            style: 曲风风格
            duration: 目标时长(秒)

        Returns:
            优化后的结构化歌词 + 校验报告
        """
        prompt = self._build_optimize_prompt(raw_lyric, bpm, style, duration)
        result = self._call_doubao(prompt)

        # 可选：通义千问全局校验
        check_report = "未启用通义千问校验"
        if self.qwen_key:
            check_prompt = self._build_check_prompt(result)
            check_report = self._call_qwen(check_prompt)

        return {
            "lyric_struct": result,
            "check_report": check_report,
        }

    def modify_lyric(self, current_lyric: str, user_command: str) -> dict:
        """
        交互式局部修改歌词

        Args:
            current_lyric: 当前结构化歌词
            user_command: 用户修改指令

        Returns:
            修改后的歌词 + 校验报告
        """
        prompt = f"""
当前歌词：
{current_lyric}

用户修改要求：{user_command}

要求：
1. 只修改用户指定的部分，其余内容保持原样
2. 保持整体风格与韵脚一致
3. 输出完整的结构化歌词（JSON格式）
4. 不要输出任何解释文字，只输出JSON
"""
        new_lyric = self._call_doubao(prompt)

        check_report = "未启用通义千问校验"
        if self.qwen_key:
            check_prompt = self._build_check_prompt(new_lyric)
            check_report = self._call_qwen(check_prompt)

        return {
            "lyric_struct": new_lyric,
            "check_report": check_report,
        }

    def _build_optimize_prompt(self, raw_lyric: str, bpm: float, style: str, duration: float) -> str:
        """构建歌词优化Prompt"""
        return f"""
你是一位资深华语流行音乐作词人。

【原始歌词】
{raw_lyric}

【音乐参数】
- 曲风：{style}
- 速度：{bpm} BPM
- 目标时长：约{int(duration // 60)}分{int(duration % 60)}秒

【优化要求】
1. 保留原作的核心故事、情感和意象，不要完全重写
2. 优化句子节奏，使其适合演唱，每句字数符合{int(bpm)}BPM的律动
3. 自然押韵，韵脚不要太刻意
4. 口语化、有画面感，避免书面语太重
5. 按歌曲结构输出：主歌1、主歌2、预副歌、副歌、桥段、尾句

【输出格式】
严格输出JSON格式，不要输出任何其他内容：
{{
  "title": "歌曲标题",
  "style": "{style}",
  "bpm": {bpm},
  "sections": [
    {{
      "type": "主歌1",
      "lines": ["第一句", "第二句"]
    }}
  ]
}}
"""

    def _build_check_prompt(self, lyric_json: str) -> str:
        """构建歌词一致性校验Prompt"""
        return f"""
请校验以下歌词的结构完整性和一致性：

{lyric_json}

检查项：
1. 段落结构是否完整（主歌/预副歌/副歌/桥段）
2. 韵脚是否统一或有规律转换
3. 主题是否前后一致，有无偏离
4. 每句字数是否适合演唱

输出简短的校验报告，指出问题和改进建议。
"""

    def _call_doubao(self, prompt: str) -> str:
        """调用豆包API"""
        url = f"{self.doubao_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.doubao_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.doubao_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _call_qwen(self, prompt: str) -> str:
        """调用通义千问API（可选）"""
        url = f"{self.qwen_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.qwen_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.qwen_model,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
