"""AI Music Composer Skill - 主入口

完整流水线：
1. 音频预处理（格式标准化）
2. 音频分析（BPM/节拍/旋律提取）
3. 歌词交互式润色（多轮修改循环）
4. 提交音乐API生成成品歌曲
5. 保存工程元数据，清理临时文件
"""

from config import Config
from task_manager import TaskManager
from audio_preprocessor import AudioPreprocessor
from audio_analyzer import AudioAnalyzer
from lyric_editor import LyricEditor
from music_api_client import MusicAPIClient


def main():
    print("=" * 50)
    print("  🎵 AI Music Composer - 歌曲创作流水线")
    print("=" * 50)

    # 校验配置
    missing = Config.validate()
    if missing:
        print(f"\n⚠️  缺少必填环境变量: {', '.join(missing)}")
        print("请复制 .env.example 为 .env 并填入密钥")
        return

    # 初始化各模块
    task_mgr = TaskManager()
    audio_prep = AudioPreprocessor(tmp_dir="./tmp")
    audio_analyzer = AudioAnalyzer()
    lyric_editor = LyricEditor(
        doubao_key=Config.DOUBAO_API_KEY,
        doubao_base_url=Config.DOUBAO_BASE_URL,
        doubao_model=Config.DOUBAO_MODEL,
        qwen_key=Config.QWEN_API_KEY,
        qwen_base_url=Config.QWEN_BASE_URL,
        qwen_model=Config.QWEN_MODEL,
    )
    music_client = MusicAPIClient(
        provider=Config.MUSIC_API_PROVIDER,
        api_key=Config.MUSIC_API_KEY,
        poll_interval=Config.TASK_POLL_INTERVAL,
        poll_timeout=Config.TASK_POLL_TIMEOUT,
    )

    # 获取用户输入
    print("\n📝 请输入创作信息：")
    audio_path = input("  1. Demo音频文件路径: ").strip()
    raw_lyric = input("  2. 原始歌词文本: ").strip()
    style = input("  3. 目标曲风（如：华语流行/民谣/摇滚）: ").strip() or "华语流行"

    # 创建任务
    task_id = task_mgr.create_task()
    print(f"\n✅ 已创建任务: {task_id[:8]}...")

    try:
        # Step 1: 音频预处理
        print("\n🔄 [1/4] 音频预处理...")
        audio_info = audio_prep.get_audio_info(audio_path)
        print(f"   原始格式: {audio_info.get('codec', 'unknown')}, "
              f"时长: {audio_info.get('duration', 0):.1f}秒")
        standardized_wav = audio_prep.process(audio_path)
        print(f"   ✅ 已转码为标准化WAV")

        # Step 2: 音频分析
        print("\n🔍 [2/4] 音频分析（BPM/节拍/旋律）...")
        analysis = audio_analyzer.analyze(standardized_wav)
        print(f"   BPM: {analysis['bpm']}")
        print(f"   时长: {analysis['duration']}秒")
        print(f"   小节数: {len(analysis['bars'])}")
        task_mgr.update_audio_analysis(task_id, analysis)

        # Step 3: 歌词优化 + 交互修改
        print("\n✍️  [3/4] 歌词优化...")
        lyric_result = lyric_editor.optimize_lyric(
            raw_lyric=raw_lyric,
            bpm=analysis["bpm"],
            style=style,
            duration=analysis["duration"],
        )
        current_lyric = lyric_result["lyric_struct"]
        print("\n--- 优化后歌词 ---")
        print(current_lyric)
        if lyric_result.get("check_report"):
            print(f"\n--- 校验报告 ---")
            print(lyric_result["check_report"])

        # 交互修改循环
        print("\n💬 输入修改指令调整歌词，输入 'ok' 确认定稿")
        while True:
            user_cmd = input("  > ").strip()
            if user_cmd.lower() == "ok":
                break
            if not user_cmd:
                continue
            print("  ✏️  正在修改...")
            result = lyric_editor.modify_lyric(current_lyric, user_cmd)
            current_lyric = result["lyric_struct"]
            print("\n--- 更新后歌词 ---")
            print(current_lyric)

        task_mgr.update_lyric(task_id, current_lyric)

        # Step 4: 生成歌曲
        print("\n🎵 [4/4] 提交音乐生成任务...")
        print("   异步排队中，请耐心等待...")
        final_audio_url = music_client.generate(
            midi_motif=analysis["midi_data"],
            lyric=current_lyric,
            bpm=analysis["bpm"],
            style=style,
        )

        # 完成
        task_mgr.mark_success(task_id, final_audio_url, analysis, current_lyric)
        print(f"\n🎉 任务完成！")
        print(f"   成品音频: {final_audio_url}")
        print(f"   任务ID: {task_id}")

    except Exception as e:
        task_mgr.mark_failed(task_id, str(e))
        print(f"\n❌ 任务失败: {e}")
        raise

    finally:
        # 清理临时音频文件
        audio_prep.clean_tmp()
        print("\n🧹 已清理临时文件")


if __name__ == "__main__":
    main()
