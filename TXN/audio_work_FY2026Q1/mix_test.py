#!/usr/bin/env python3
"""
TXN FY2026Q1 ラジオ版テスト ミックス（BGMなし）
構成:
  [0:00-2.0s]   ジングル単独
  [2.0s-5.12s]  ジングル + タイトルコール重ね
  [5.12-5.7s]   ジングル余韻
  [5.7-6.0s]    無音 0.3秒
  [6.0s - END]  本編ナレーション（BGMなし）
"""
import os, subprocess

ASSETS = "/Users/yskzz121/ui-kabu-times/assets/bgm"
WORK = "/Users/yskzz121/ui-kabu-reports/TXN/audio_work_FY2026Q1"
FINAL = "/Users/yskzz121/ui-kabu-reports/TXN/FY2026Q1-radio-test.mp3"

JINGLE = os.path.join(ASSETS, "jingle_trimmed.mp3")
TITLE = os.path.join(ASSETS, "titlecall.mp3")
NARRATION = os.path.join(WORK, "narration_only_test.mp3")

TITLE_OFFSET = 2.0
GAP_AFTER_INTRO = 0.3
JINGLE_GAIN_DB = -4
TITLE_GAIN_DB = +5


def dur(p):
    return float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=nw=1:nk=1",p],
        capture_output=True, text=True, check=True).stdout.strip())


print("[1/2] Intro生成 (jingle + title overlap at 2.0s) ...")
intro_mp3 = os.path.join(WORK, "intro_overlap.mp3")
subprocess.run([
    "ffmpeg","-y",
    "-i", JINGLE,
    "-i", TITLE,
    "-filter_complex",
    f"[0]volume={JINGLE_GAIN_DB}dB[jAdj];"
    f"[1]volume={TITLE_GAIN_DB}dB,adelay={int(TITLE_OFFSET*1000)}|{int(TITLE_OFFSET*1000)}[titleDel];"
    f"[jAdj][titleDel]amix=inputs=2:duration=longest:normalize=0,"
    f"apad=pad_dur={GAP_AFTER_INTRO}[out]",
    "-map","[out]",
    "-c:a","libmp3lame","-b:a","128k","-ar","24000",
    intro_mp3,
], check=True, capture_output=True)

print("[2/2] Concat (intro + narration, no BGM) ...")
concat_list = os.path.join(WORK, "concat_test.txt")
with open(concat_list, "w") as f:
    f.write(f"file '{intro_mp3}'\n")
    f.write(f"file '{NARRATION}'\n")

subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",concat_list,
    "-c:a","libmp3lame","-b:a","128k","-ar","24000",
    FINAL,
], check=True, capture_output=True)

intro_dur = dur(intro_mp3)
total = dur(FINAL)
print(f"\n完成: {FINAL}")
print(f"  全長: {int(total//60)}:{int(total%60):02d}")
print(f"  サイズ: {os.path.getsize(FINAL)/1024:.1f} KB")
print(f"  イントロ: 0:00 - {intro_dur:.2f}s")
print(f"  本編開始: {intro_dur:.2f}s")
