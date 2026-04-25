#!/usr/bin/env python3
"""
Atlas Quarterly TXN FY2026Q1 ラジオ版（本番）
- ja-JP-Neural2-C / speaking_rate=1.12（Atlas Daily と同一）
- 7章構成（目安9分）
- ID3 CHAP/CTOC タグはミックス時 (mix.py) で付与
"""
import os, subprocess
from google.cloud import texttospeech

WORK_DIR = "/Users/yskzz121/ui-kabu-reports/TXN/audio_work_FY2026Q1"
NARRATION_OUT = os.path.join(WORK_DIR, "narration_only.mp3")

SECTIONS = [
    ("opening", "オープニング", """
Atlas Quarterly、テキサス・インスツルメンツ、Q1 FY2026決算分析、ラジオ版です。
本日は2026年4月25日。4月22日に発表された、第1四半期決算を、約9分で読み解きます。
総合スコアは、5、「素晴らしい決算」。一言でまとめれば、「大幅なダブルビート、Industrial市場の、全面復活」です。
過去2年間、テキサス・インスツルメンツを苦しめてきた、Industrialの、長期在庫調整サイクル。それが、ついに終焉を迎えたシグナルが、複数のセグメントから、明確に読み取れる決算となりました。
それでは、本編をお届けします。
"""),

    ("highlights", "決算ハイライト", """
まずは、決算ハイライトです。
売上は、48億2,500万ドル、前年比プラス18.5%。コンセンサス予想を、6.7%上回る、大幅なビートでした。前期比でも、プラス9.1%の、力強い増収です。
GAAP EPSは、1ドル68セント、前年比プラス31.3%。コンセンサス予想を、23%上回りました。離散税項目、5セント分を含みます。
ここで、注意点を1つ。前回、Q4 FY2025までは、Non-GAAP EPSで開示していましたが、今回Q1 FY2026から、テキサス・インスツルメンツは、GAAP単独開示に切り替わりました。チャートで、前期比較する際は、基準が異なる点に、ご留意ください。
収益性も、大幅に改善しています。粗利率は58.0%、前期比でプラス210ベーシスポイントの、大幅な改善。営業利益率は37.5%、前年比でプラス510ベーシスポイントです。
キャッシュ創出力も、力強く回復しました。フリーキャッシュフローは、過去12ヶ月で、43億5,100万ドル、前年比プラス154%。FCFマージンは、23.6%まで戻っています。長らく低迷していた、テキサス・インスツルメンツのフリーキャッシュフロー体質が、明確な、回復軌道に乗ったと、判断できます。
"""),

    ("segments", "セグメント別動向", """
続いて、セグメント別の動向です。
最大の注目点は、Industrial市場の、全面復活です。前年比プラス30%超と、ここ数年で初めての、力強い回復を見せました。在庫調整局面が、ようやく終わり、新規受注が、本格的に立ち上がっています。これが、今期スコア5の、最大の根拠です。
Data Centerは、前年比プラス90%。AI関連の、電源IC需要が、引き続き強烈に伸びています。Communications Equipmentもプラス25%、Automotiveは中一桁プラス、Personal Electronicsは、フラットでした。
事業区分で見ますと、主力のAnalogは、売上39億2,400万ドル、前年比プラス22%、全体構成比は81.3%。Embedded Processingは、7億2,300万ドル、プラス12%。その他のOtherは、1億7,800万ドルで、マイナス16%でした。
全6エンドマーケットのうち、5つでプラス成長、Personal Electronicsだけがフラット、という、ほぼ全方位での回復が、今回の決算の核心です。半導体在庫サイクルの、底打ちが、最も鮮明に現れた決算と、評価できます。
"""),

    ("guidance", "ガイダンス", """
続いて、Q2 2026のガイダンスです。
中値は、売上で52億ドル、コンセンサス予想を、8.3%上回ります。EPSは、1ドル91セント、コンセンサスを、21.7%上回る、極めて強気の見通しです。
ガイダンスEPSが、コンセンサスを20%以上、上回るのは、テキサス・インスツルメンツの近年では、極めて稀なパターンです。経営陣は、Q2の決算で、Q1の好調が、一過性ではないことを、数字で証明する必要があります。
通期見通しについては、テキサス・インスツルメンツは、伝統的にガイダンスを出さない姿勢を継続しています。ただし、半導体在庫サイクルの、底打ちを、IR資料で、明確に示唆しました。連続増配、22年継続中という、株主還元の安定性も、変わらぬ強みです。
"""),

    ("valuation", "バリュエーション", """
続いて、バリュエーションです。
3シナリオで、フェアバリューを試算しました。LOWは、推定PER28倍ベースで、178ドル64セント。MIDは、外部実測の、フォワードPER34.62倍で、225ドル72セント。HIGHは、推定44倍ベースで、340ドル12セントです。
4月23日の終値は、282ドル23セント。新52週高値、284ドル12セントを更新しました。決算前比、プラス19.43%の急騰です。
MIDのフェアバリュー、225ドル72セントに対し、現値282ドル23セントは、プラス25.0%のプレミアム水準。判定は、「やや割高」です。
アナリスト平均目標は、263ドル44セント。現値は、これをプラス7%超過する、「目標超え」状態にあります。NTMフェアバリューは、過去3年フォワードPER平均35倍ベースで、228ドルと算出されます。
ベア継続派も健在です。ゴールドマン・サックスは、Sellレーティングで、目標200ドル。モルガン・スタンレーも、Sellで、目標221ドルを維持しています。決算後、目標株価を引き上げた数十社と、慎重派2社の、評価が二極化している銘柄、と、整理できます。
"""),

    ("risks", "リスクとカタリスト", """
リスクとカタリストです。
第一のリスクは、現値が、アナリスト平均目標263ドル44セントを、プラス7%超過している点です。ゴールドマン・サックスは、Sellレーティングで、目標200ドル、モルガン・スタンレーも、Sellで、目標221ドルを維持しています。慎重派の存在は、上値余地が、限定的であることへの、警戒シグナルです。これだけバリュエーション評価が、二極化する銘柄は、極めて稀。マクロ環境や、セクター・ローテーション次第で、評価のバランスが、急変するリスクが、内在しています。
第二のリスクは、データの一部が、まだ確定していない点です。次の四半期報告書、開示まで、未確認のデータが、複数残っています。レポート内で、「10-Q待ち」「未確認」バッジが付いている、9箇所のデータは、Q2決算前後で、最終確定する見込みです。
カタリストとしては、来週から、半導体決算ラッシュが続きます。TSMC、エヌビディア、マイクロン、インテルの開示が、Industrial・Data Centerサイクルの、整合性を、最終チェックする機会となります。
中期では、22年連続増配の維持と、FCFマージン25%超への復帰タイミングが、最大の注目点です。
"""),

    ("closing", "クロージング", """
クロージングです。
本日の要点を、3つにまとめます。
1つめ。テキサス・インスツルメンツは、売上48億2,500万ドル、GAAP EPS 1ドル68セントの、大幅なダブルビートを達成。コンセンサスを、売上で6.7%、EPSで23%、それぞれ上回りました。
2つめ。Industrial市場が、前年比プラス30%超と、全面復活。Data Centerもプラス90%で、AIサイクルへの感応度が、明確に確認されました。
3つめ。フォワードPER34.62倍のMIDフェアバリュー、225ドル72セントに対し、現値282ドル23セントは、プラス25%のプレミアム。判定は、「やや割高」。アナリスト評価が二極化する中、慎重な値動きの観察が、必要です。
あくまで参考情報です。投資判断は、ご自身の責任で、おこなってください。
本日のAtlas Quarterly、テキサス・インスツルメンツ Q1 FY2026決算分析、ラジオ版を、お聴きいただき、ありがとうございました。
"""),
]


def synth_section(client, text, out_path):
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
        input=texttospeech.SynthesisInput(text=text.strip()),
        voice=voice, audio_config=audio_config,
    )
    with open(out_path, "wb") as f:
        f.write(response.audio_content)


def duration_sec(mp3_path):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", mp3_path],
        capture_output=True, text=True, check=True,
    ).stdout.strip())


def main():
    client = texttospeech.TextToSpeechClient()
    section_files = []
    section_durs = []

    for i, (sid, title, text) in enumerate(SECTIONS):
        part = os.path.join(WORK_DIR, f"{i:02d}_{sid}.mp3")
        print(f"[{i+1}/{len(SECTIONS)}] {title}...")
        synth_section(client, text, part)
        section_files.append(part)
        section_durs.append(duration_sec(part))

    concat_list = os.path.join(WORK_DIR, "concat_narration_full.txt")
    with open(concat_list, "w") as f:
        for p in section_files:
            f.write(f"file '{p}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", NARRATION_OUT],
        check=True, capture_output=True,
    )

    # 章境界をテキストで書き出してミックス側で利用
    chapters_txt = os.path.join(WORK_DIR, "narration_chapters.txt")
    cursor = 0.0
    with open(chapters_txt, "w") as f:
        for (sid, title, _), dur in zip(SECTIONS, section_durs):
            f.write(f"{sid}\t{title}\t{cursor:.3f}\t{cursor+dur:.3f}\n")
            cursor += dur

    total = duration_sec(NARRATION_OUT)
    print(f"\nナレーション完成: {NARRATION_OUT}")
    print(f"  全長: {int(total//60)}:{int(total%60):02d}")
    print(f"  サイズ: {os.path.getsize(NARRATION_OUT)/1024:.1f} KB")
    print(f"  章境界: {chapters_txt}")
    for i, ((sid, title, _), dur) in enumerate(zip(SECTIONS, section_durs)):
        print(f"    [{i+1}] {title}: {int(dur//60)}:{int(dur%60):02d}")


if __name__ == "__main__":
    main()
