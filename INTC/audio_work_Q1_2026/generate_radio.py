#!/usr/bin/env python3
"""
Atlas Quarterly INTC Q1 2026 ラジオ版生成（ナレーションのみ）
- ja-JP-Neural2-C / speaking_rate=1.12
- 7章構成（オープニング + ハイライト + セグメント + ガイダンス + バリュエーション + リスク + クロージング、約7-9分）
"""
import os, subprocess
from google.cloud import texttospeech

WORK_DIR = "/Users/yskzz121/ui-kabu-reports/INTC/audio_work_Q1_2026"
NARRATION_OUT = os.path.join(WORK_DIR, "narration_only.mp3")

SECTIONS = [
    ("opening", "オープニング", """
Atlas Quarterly、Intel Corporation、Q1 2026決算分析、ラジオ版です。
本日は2026年4月25日。4月23日に発表された、第1四半期決算を、お届けします。
総合スコアは、5。「素晴らしい決算」です。一言でまとめれば、リップ・ブ・タンCEO体制の構造改革が、損益計算書の主要3行で、同時に数値化された、歴史的な四半期です。
"""),

    ("highlights", "決算ハイライト", """
それでは、決算ハイライトです。
売上は、135億8,000万ドル、前年比プラス6.9%。コンセンサス予想を、9.3%上回るビートでした。6四半期連続のトップライン上振れとなります。
Non-GAAP EPSは、0ドル29セント、コンセンサス予想0ドル01セントを、29倍上回る、歴史的サプライズです。前年比では、プラス123%の改善となりました。
収益性も、大幅に上振れしました。Non-GAAP粗利率は、41.0%。自社ガイダンス34.5%を、650ベーシスポイント、上振れています。ファウンドリーの減価償却負担を吸収しながらの数値で、製品ミックス改善と、18A歩留まり改善が、同時に効いた結果です。
Non-GAAP営業利益率は、12.3%。前年5.4%から、6.9パーセントポイントの大幅改善でした。
一方で、GAAP EPSは、マイナス0ドル73セント。モバイルアイ のれん減損41億ドルを含む特別損失計上が要因です。営業キャッシュフローは、10億9,600万ドルの黒字を維持しましたが、CapEx 50億ドルに対して、調整後フリーキャッシュフローは、マイナス20億1,600万ドル。直近2四半期は黒字に転換していましたが、今四半期は、ファウンドリー投資の再加速で、再びマイナスに戻っています。
"""),

    ("segments", "セグメント別", """
セグメント別の状況です。
クライアント・コンピューティング、CCGの売上は、77億ドル、前年比プラス1.3%。営業利益率は32.6%です。
データセンター・AI、DCAIの売上は、51億ドル、前年比プラス22.0%、過去8四半期で最高の伸びを記録しました。AI主導売上は、全社の60%を占め、前年比プラス40%で拡大しています。
Intel ファウンドリーの売上は、54億ドル、前年比プラス15.9%。営業利益率はマイナス45.0%、前期マイナス55.7%から、10.7パーセントポイント改善しました。ただし、外部顧客向け売上は、1億7,400万ドル、ファウンドリー全体の3.2%にとどまっています。
その他事業、モバイルアイを含む合計は、6億2,800万ドルでした。
"""),

    ("guidance", "ガイダンス", """
次に、ガイダンスです。
Q2 2026の売上ガイダンス中央値は、143億ドル。コンセンサス130億7,000万ドルを、9.4%上回る、強気の見通しです。
Non-GAAP EPSガイダンスは、0ドル20セント。コンセンサス0ドル06セントから0ドル09セントを、122%から233%上回ります。
Non-GAAP粗利率ガイダンスは、39.0%。
これで、6四半期連続のガイダンス上方修正となります。ジンスナーCFOは、「2026年通期のCapExは前年比横ばい、前回ガイダンスから上方修正」と明言しました。
"""),

    ("valuation", "バリュエーション", """
バリュエーションです。
通常終値は、4月23日時点で、66ドル78セント、プラス2.3%。決算後の時間外取引では、75ドルから80ドル、中央値77ドル50セントに上昇しました。
26年ぶりに、2000年につけた史上最高値、75ドル81セントを、突破した形です。
3シナリオで見ると、ローシナリオは、6ドル10セント、現値からマイナス91%。ミッドシナリオは、30ドル90セント、マイナス54%。ハイシナリオは、67ドルで、現値とほぼ並ぶ水準です。
フォワードPERは、124倍。半導体メガキャップでも、突出した水準です。アナリストの平均目標株価51ドルに対し、時間外取引の77ドル50セントは、52%上回っており、織り込み超過の警戒水準にあります。
"""),

    ("risks", "リスク・カタリスト", """
リスクとカタリストです。
リスクは、4点です。
第一に、フォワードPER 124倍の、赤字回復過程の異常値。EPS正常化が進めばマルチプルは急速に圧縮される性質のものです。
第二に、調整後フリーキャッシュフロー マイナス20億ドルへの再赤字転換と、モバイルアイ減損41億ドルなど、GAAPベースの財務的重石。
第三に、ジンスナーCFOが、2026年下半期のパソコン市場は、2桁前半パーセント減少すると、明示した、パソコン市場のリスク。
第四に、決算後のアイブイ・クラッシュ、つまりインプライド・ボラティリティ急落と、過熱解消売りで、マイナス10からマイナス15%の調整は、十分あり得るシナリオです。
カタリストは、18Aの量産進捗、14Aの成熟度、ファウンドリーの外部顧客契約発表、ティーエスエムシー追撃のロードマップ、です。
"""),

    ("closing", "クロージング", """
クロージングです。
本日のポイントを、3つに絞ります。
1つ目、Non-GAAP EPSが予想の29倍、6四半期連続のガイダンス上振れで、構造改革が損益計算書に同時表面化した、歴史的な決算でした。
2つ目、フォワードPER 124倍、アナリスト平均目標との52%乖離は、織り込み超過の警戒水準です。
3つ目、ファウンドリー投資のキャッシュフロー振れと、パソコン市場の下期リスクは、引き続き注視が必要です。
次回の決算は、Q2 2026、2026年7月下旬の発表が見込まれます。本日は、ご視聴、ありがとうございました。
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
