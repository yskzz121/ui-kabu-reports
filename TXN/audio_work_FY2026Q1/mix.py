#!/usr/bin/env python3
"""
Atlas Quarterly TXN FY2026Q1 ラジオ版（本番）ミックス
v3 確定パラメータ + ID3 CHAP/CTOC チャプター埋め込み
"""
import os, subprocess, json
from mutagen.id3 import ID3, CHAP, CTOC, TIT2, CTOCFlags

DAILY_ASSETS = "/Users/yskzz121/ui-kabu-times/assets/bgm"
REPORT_ASSETS = "/Users/yskzz121/ui-kabu-reports/_assets/bgm"
WORK = "/Users/yskzz121/ui-kabu-reports/TXN/audio_work_FY2026Q1"
FINAL = "/Users/yskzz121/ui-kabu-reports/TXN/FY2026Q1-radio.mp3"
JSON_OUT = "/Users/yskzz121/ui-kabu-reports/TXN/FY2026Q1-radio-chapters.json"

JINGLE = os.path.join(DAILY_ASSETS, "jingle_trimmed.mp3")
TITLE = os.path.join(DAILY_ASSETS, "titlecall.mp3")
BGM = os.path.join(REPORT_ASSETS, "cinematic-documentary.mp3")
NARRATION = os.path.join(WORK, "narration_only.mp3")
CHAPTERS_TXT = os.path.join(WORK, "narration_chapters.txt")

# v3 確定パラメータ
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


def fmt(ms):
    s = ms // 1000
    return f"{s//60}:{s%60:02d}"


print("[1/3] Intro生成 (jingle + title overlap at 2.0s) ...")
intro_mp3 = os.path.join(WORK, "intro_overlap_full.mp3")
subprocess.run([
    "ffmpeg","-y","-i", JINGLE, "-i", TITLE,
    "-filter_complex",
    f"[0]volume={JINGLE_GAIN_DB}dB[jAdj];"
    f"[1]volume={TITLE_GAIN_DB}dB,adelay={int(TITLE_OFFSET*1000)}|{int(TITLE_OFFSET*1000)}[titleDel];"
    f"[jAdj][titleDel]amix=inputs=2:duration=longest:normalize=0,"
    f"apad=pad_dur={GAP_AFTER_INTRO}[out]",
    "-map","[out]","-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    intro_mp3,
], check=True, capture_output=True)

print("[2/3] Main合成 (narration + BGM cinematic + dynaudnorm) ...")
narr_dur = dur(NARRATION)
main_with_bgm = os.path.join(WORK, "main_with_bgm_full.mp3")
subprocess.run([
    "ffmpeg","-y","-stream_loop","-1","-i", BGM, "-i", NARRATION,
    "-filter_complex",
    f"[0]dynaudnorm=f=200:g=15,volume={MAIN_BGM_VOL},afade=t=in:st=0:d={BGM_FADE_IN}[bgm];"
    f"[1][bgm]amix=inputs=2:duration=first:normalize=0,"
    f"afade=t=out:st={narr_dur - BGM_FADE_OUT:.2f}:d={BGM_FADE_OUT}[out]",
    "-map","[out]","-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    main_with_bgm,
], check=True, capture_output=True)

print("[3/3] Concat ...")
concat_list = os.path.join(WORK, "concat_full.txt")
with open(concat_list, "w") as f:
    f.write(f"file '{intro_mp3}'\n")
    f.write(f"file '{main_with_bgm}'\n")
subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",concat_list,
    "-ac", str(OUTPUT_CHANNELS),
    "-c:a","libmp3lame","-b:a", OUTPUT_BITRATE, "-ar","24000",
    FINAL,
], check=True, capture_output=True)

# チャプター埋め込み（ジングル + 各章）
intro_dur_ms = int(dur(intro_mp3) * 1000)
chapters = [
    {"id": "intro", "title": "ジングル＋タイトルコール",
     "start_ms": 0, "end_ms": intro_dur_ms},
]
with open(CHAPTERS_TXT) as f:
    for line in f:
        sid, title, start, end = line.strip().split("\t")
        s_ms = intro_dur_ms + int(float(start) * 1000)
        e_ms = intro_dur_ms + int(float(end) * 1000)
        chapters.append({"id": sid, "title": title,
                         "start_ms": s_ms, "end_ms": e_ms})

# start_label 付与
for ch in chapters:
    ch["start_label"] = fmt(ch["start_ms"])

try:
    tags = ID3(FINAL)
except Exception:
    tags = ID3()
tags.delall("CHAP"); tags.delall("CTOC")
for ch in chapters:
    tags.add(CHAP(
        element_id=ch["id"], start_time=ch["start_ms"], end_time=ch["end_ms"],
        start_offset=0xFFFFFFFF, end_offset=0xFFFFFFFF,
        sub_frames=[TIT2(encoding=3, text=[ch["title"]])],
    ))
tags.add(CTOC(
    element_id="toc", flags=CTOCFlags.TOP_LEVEL | CTOCFlags.ORDERED,
    child_element_ids=[ch["id"] for ch in chapters],
    sub_frames=[TIT2(encoding=3, text=["目次"])],
))
tags.add(TIT2(encoding=3, text=["Atlas Quarterly TXN FY2026Q1"]))
tags.save(FINAL)

total_ms = int(dur(FINAL) * 1000)
with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump({
        "ticker": "TXN", "period": "FY2026Q1",
        "total_ms": total_ms, "total_label": fmt(total_ms),
        "chapters": chapters,
    }, f, ensure_ascii=False, indent=2)

print(f"\n完成: {FINAL}")
print(f"  全長: {fmt(total_ms)}")
print(f"  サイズ: {os.path.getsize(FINAL)/1024:.1f} KB ({os.path.getsize(FINAL)/1024/1024:.2f} MB)")
print(f"  チャプター: {len(chapters)}個 (intro + 7セクション)")
print(f"  チャプターJSON: {JSON_OUT}")
for ch in chapters:
    print(f"    [{ch['start_label']}] {ch['title']}")
