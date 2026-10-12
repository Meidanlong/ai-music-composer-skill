"""流水线单元测试（不调用真实API）"""

import unittest
import sys
from pathlib import Path

# 将src加入路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_preprocessor import AudioPreprocessor
from task_manager import TaskManager
from audio_analyzer import AudioAnalyzer


class TestAudioPreprocessor(unittest.TestCase):
    def test_tmp_dir_creation(self):
        prep = AudioPreprocessor(tmp_dir="./test_tmp")
        self.assertTrue(prep.tmp_dir.exists())
        prep.clean_tmp()

    def test_input_not_found(self):
        prep = AudioPreprocessor(tmp_dir="./test_tmp")
        with self.assertRaises(FileNotFoundError):
            prep.process("./nonexistent_file.mp3")
        prep.clean_tmp()


class TestTaskManager(unittest.TestCase):
    def test_task_lifecycle(self):
        mgr = TaskManager(meta_dir="./test_tasks")
        task_id = mgr.create_task()
        self.assertTrue(task_id)

        task = mgr.get_task(task_id)
        self.assertEqual(task["status"], "running")

        mgr.update_lyric(task_id, "test lyric")
        task = mgr.get_task(task_id)
        self.assertEqual(task["final_lyric"], "test lyric")

        mgr.mark_success(task_id, "http://example.com/audio.mp3")
        task = mgr.get_task(task_id)
        self.assertEqual(task["status"], "success")


class TestAudioAnalyzer(unittest.TestCase):
    def test_beat_generation(self):
        analyzer = AudioAnalyzer()
        beats = analyzer._gen_beat_timeline(120, 4.0)
        # 120BPM = 每0.5秒一拍，4秒应该有8拍
        self.assertGreaterEqual(len(beats), 7)
        self.assertLessEqual(len(beats), 9)


if __name__ == "__main__":
    unittest.main()
