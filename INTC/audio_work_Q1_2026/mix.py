#!/usr/bin/env python3
"""
INTC Q1 2026 ラジオ版ミックス（Atlas Quarterly v3 確定パラメータ）
パラメータは TXN FY2026Q1 mix_test_v3.py と同一（仕様書 atlas-quarterly-radio.md §8 v3 確定）
- BGM: cinematic-documentary.mp3
- BGM音量 0.05 / dynaudnorm=f=200:g=15
- 出力 64kbps mono
"""
import os, subprocess

DAILY_ASSETS = "/Users/yskzz121/ui-kabu-times/assets/bgm"
REPORT_ASSETS = "/Users/yskzz121/ui-kabu-reports/_assets/bgm"
WORK = "/Users/yskzz121/ui-kabu-reports/INTC/audio_work_Q1_2026"
FINAL = "/Users/yskzz121/ui-kabu-reports/INTC/Q1_2026-radio.mp3"

JINGLE = os.path.join(DAILY_ASSETS, "jingle_trimmed.mp3")
TITLE = os.path.join(DAILY_ASSETS, "titlecall.mp3")
BGM = os.path.join(REPORT_ASSETS, "cinematic-documentary.mp3")
NARRATION = os.path.join(WORK, "narration_only.mp3")

TITLE_OFFSET = 2.0
GAP_AFTER_INTRO = 0.3
JINGLE_GAIN_DB = -4
TITLE_GAIN_DB = +5
MAIN_BGM_VOL = 0.05
BGM_FADE_IN = 2.0
BGM_FADE_OUT = 3.0

OUTPUT_BITRATE = "64k"
OUTPUT_CHANNELS = 1


def dur(p):
    return float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=nw=1:nk=1",p],
        capture_output=True, text=True, check=True).stdout.strip())


print("[1/3] Intro生成 (jingle + title overlap at 2.0s) ...")
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
    "-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    intro_mp3,
], check=True, capture_output=True)

print("[2/3] Main合成 (narration + BGM cinematic + dynaudnorm) ...")
narr_dur = dur(NARRATION)
main_with_bgm = os.path.join(WORK, "main_with_bgm.mp3")
subprocess.run([
    "ffmpeg","-y",
    "-stream_loop","-1","-i", BGM,
    "-i", NARRATION,
    "-filter_complex",
    f"[0]dynaudnorm=f=200:g=15,volume={MAIN_BGM_VOL},afade=t=in:st=0:d={BGM_FADE_IN}[bgm];"
    f"[1][bgm]amix=inputs=2:duration=first:normalize=0,"
    f"afade=t=out:st={narr_dur - BGM_FADE_OUT:.2f}:d={BGM_FADE_OUT}[out]",
    "-map","[out]",
    "-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    main_with_bgm,
], check=True, capture_output=True)

print("[3/3] Concat ...")
concat_list = os.path.join(WORK, "concat_final.txt")
with open(concat_list, "w") as f:
    f.write(f"file '{intro_mp3}'\n")
    f.write(f"file '{main_with_bgm}'\n")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",concat_list,
    "-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    FINAL,
], check=True, capture_output=True)

intro_dur = dur(intro_mp3)
total = dur(FINAL)
print(f"\n完成: {FINAL}")
print(f"  全長: {int(total//60)}:{int(total%60):02d}")
print(f"  サイズ: {os.path.getsize(FINAL)/1024:.1f} KB")
print(f"  エンコード: {OUTPUT_BITRATE} mono, 24kHz")
print(f"  BGM音量: {MAIN_BGM_VOL}")
