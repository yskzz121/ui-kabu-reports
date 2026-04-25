#!/usr/bin/env python3
"""
Atlas Quarterly TXN FY2026Q1 ラジオ版 テスト生成（ナレーションのみ）
- ja-JP-Neural2-C
- speaking_rate=1.12（Atlas Daily と同一）
- 構成: オープニング + 決算ハイライト + クロージング（約1.5分）
"""
import os, subprocess
from google.cloud import texttospeech

WORK_DIR = "/Users/yskzz121/ui-kabu-reports/TXN/audio_work_FY2026Q1"
NARRATION_OUT = os.path.join(WORK_DIR, "narration_only_test.mp3")

SECTIONS = [
    ("opening", "オープニング", """
Atlas Quarterly、テキサス・インスツルメンツ、Q1 FY2026決算分析の音声版テストです。
本日は2026年4月25日。4月22日に発表された、第1四半期決算の要点を、お届けします。
総合スコアは、5。「素晴らしい決算」です。一言でまとめれば、大幅なダブルビート、Industrial市場の、全面復活です。
"""),

    ("highlights", "決算ハイライト", """
それでは、決算ハイライトです。
売上は、48億2,500万ドル、前年比プラス18.5%。コンセンサス予想を、6.7%上回るビートでした。
GAAP EPSは、1ドル68セント、前年比プラス31.3%、コンセンサス予想を、23%上回りました。離散税項目、5セント分を含みます。
収益性も、大幅に改善しました。粗利率は58.0%、前期比でプラス210ベーシスポイントの改善。営業利益率は37.5%、前年比でプラス510ベーシスポイントです。
キャッシュ創出力も、力強く回復しています。フリーキャッシュフローは、過去12ヶ月で43億5,100万ドル、前年比プラス154%。FCFマージンは、23.6%まで戻りました。
セグメント別では、Industrialがプラス30%超、Data Centerがプラス90%、Communications Equipmentがプラス25%、Automotiveが中一桁プラス、Personal Electronicsはフラットでした。
"""),

    ("closing", "クロージング", """
クロージングです。
Q2 2026のガイダンス中値は、売上52億ドル、コンセンサスをプラス8.3%上回り、EPSは1ドル91セント、コンセンサスをプラス21.7%上回る、強気の見通しです。
決算後株価は、4月23日終値で282ドル23セント、プラス19.43%、新52週高値の284ドル12セントを更新しました。
バリュエーションは、3シナリオ中値で、フェアバリュー225ドル72セント。現値282ドル23セントは、これに対しマイナス20%、つまり、やや割高との判定です。
本日のテスト音声は、以上です。ご視聴、ありがとうございました。
"""),
]


def synth_section(client, text, out_path):
    synthesis_input = texttospeech.SynthesisInput(text=text.strip())
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name="ja-JP-Neural2-C",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.12,
        sample_rate_hertz=24000,
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config,
    )
    with open(out_path, "wb") as f:
        f.write(response.audio_content)


def duration_sec(mp3_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", mp3_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main():
    client = texttospeech.TextToSpeechClient()
    section_files = []

    for i, (sid, title, text) in enumerate(SECTIONS):
        part = os.path.join(WORK_DIR, f"{i:02d}_{sid}.mp3")
        print(f"[{i+1}/{len(SECTIONS)}] {title}...")
        synth_section(client, text, part)
        section_files.append(part)

    concat_list = os.path.join(WORK_DIR, "concat_narration.txt")
    with open(concat_list, "w") as f:
        for p in section_files:
            f.write(f"file '{p}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", NARRATION_OUT],
        check=True, capture_output=True,
    )

    total = duration_sec(NARRATION_OUT)
    print(f"\nナレーション完成: {NARRATION_OUT}")
    print(f"  全長: {int(total//60)}:{int(total%60):02d}")
    print(f"  サイズ: {os.path.getsize(NARRATION_OUT)/1024:.1f} KB")


if __name__ == "__main__":
    main()
