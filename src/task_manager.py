"""任务管理模块：异步任务状态追踪与工程元数据持久化"""

import json
import uuid
from datetime import datetime
from pathlib import Path


class TaskManager:
    """
    任务管理器：
    - 每个创作任务分配唯一ID
    - 保存音频分析结果、最终歌词、成品链接
    - 工程元数据持久化为JSON文件
    """

    def __init__(self, meta_dir: str = "./task_meta"):
        self.meta_dir = Path(meta_dir)
        self.meta_dir.mkdir(exist_ok=True)

    def create_task(self) -> str:
        """创建新任务，返回任务ID"""
        task_id = str(uuid.uuid4())
        meta = {
            "task_id": task_id,
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "audio_analysis": None,
            "final_lyric": None,
            "final_audio_url": None,
        }
        self._save(task_id, meta)
        return task_id

    def update_audio_analysis(self, task_id: str, analysis: dict):
        """更新音频分析结果"""
        meta = self._load(task_id)
        meta["audio_analysis"] = analysis
        self._save(task_id, meta)

    def update_lyric(self, task_id: str, lyric: str):
        """更新最终歌词"""
        meta = self._load(task_id)
        meta["final_lyric"] = lyric
        self._save(task_id, meta)

    def mark_success(self, task_id: str, audio_url: str, analysis: dict = None, lyric: str = None):
        """标记任务成功，保存完整工程元数据"""
        meta = self._load(task_id)
        meta["status"] = "success"
        meta["finished_at"] = datetime.now().isoformat()
        meta["final_audio_url"] = audio_url
        if analysis:
            meta["audio_analysis"] = analysis
        if lyric:
            meta["final_lyric"] = lyric
        self._save(task_id, meta)

    def mark_failed(self, task_id: str, error: str):
        """标记任务失败"""
        meta = self._load(task_id)
        meta["status"] = "failed"
        meta["error"] = error
        meta["finished_at"] = datetime.now().isoformat()
        self._save(task_id, meta)

    def get_task(self, task_id: str) -> dict:
        """查询任务状态与元数据"""
        return self._load(task_id)

    def list_tasks(self) -> list[dict]:
        """列出所有任务"""
        tasks = []
        for f in self.meta_dir.glob("*.json"):
            tasks.append(json.loads(f.read_text(encoding="utf-8")))
        return sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)

    def _save(self, task_id: str, meta: dict):
        path = self.meta_dir / f"{task_id}.json"
        path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load(self, task_id: str) -> dict:
        path = self.meta_dir / f"{task_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"任务不存在: {task_id}")
        return json.loads(path.read_text(encoding="utf-8"))
