#!/usr/bin/env python3
"""
storyboard_planner.py - Step 2: Design & Beat Mapping Engine (Master AI Video Editor Workflow)
Inspired by 'Example to learn from.MP4' (50/50 Split-Screen: 100% Opaque Visuals Above + Speaker Below)
& Prompt Motion Light Editorial Guidelines.

Features:
1. Beat Map Generation (`beat_map.json`):
   - Maps out every core idea in the script and assigns strictly ONE graphic per idea.
2. 50/50 Split-Screen Layout (`layout_mode = "split"`):
   - Top Half (1080x920, y=0..920): 100% Opaque Light Modern Editorial Canvas (#F6F8FC) so the
     background video NEVER bleeds through behind the graphic.
   - Bottom Half (1080x1000, y=920..1920): Speaker talking live down below (matching 'Example to learn from.MP4').
3. Longer Visual Durations (8.0s - 15.5s per Beat):
   - Each visual beat stays on screen for the full duration of that concept's spoken explanation,
     with a brief 1.2s full-screen speaker transition before the next beat begins.
4. English Study Names Across All Languages:
   - In both English and Moroccan Darija videos, all academic study names, paper titles, researcher
     names, institutions, and visual headers remain strictly in English.
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from motion_library.catalog import MOTION_CATALOG


def find_word_timestamp(all_words, phrases, default_t, min_t=0.0):
    """
    Searches the aligned word list for the first occurrence of any phrase in `phrases`
    at or after `min_t`, returning its exact acoustic start timestamp.
    """
    if not all_words:
        return round(default_t, 2)

    norm_words = [re.sub(r"[^\w\u0600-\u06FF\d\.]", "", w["word"]).lower() for w in all_words]
    for phrase in phrases:
        p_toks = [re.sub(r"[^\w\u0600-\u06FF\d\.]", "", t).lower() for t in phrase.split() if t.strip()]
        if not p_toks:
            continue
        n = len(p_toks)
        for i in range(len(norm_words) - n + 1):
            if float(all_words[i]["start"]) < min_t:
                continue
            match = True
            for k in range(n):
                pt = p_toks[k]
                wt = norm_words[i + k]
                if not wt:
                    match = False
                    break
                if pt == wt:
                    continue
                if len(pt) >= 4 and len(wt) >= 4 and (pt in wt or wt in pt):
                    continue
                match = False
                break
            if match:
                return round(float(all_words[i]["start"]), 2)
    return round(default_t, 2)


def build_money_happiness_storyboard(all_words, total_duration, lang="en"):
    """
    Builds an acoustic-word-locked Beat Map for the 'Money vs Happiness' script
    (English & Moroccan Darija) with:
    - 50/50 Split-Screen layout (`layout_mode = "split"`): 100% opaque top light visual + bottom speaker talking
    - Extended visual durations (7.5s - 15.5s) so visuals never disappear prematurely while the concept is explained
    - Strictly English study names, paper titles, and author citations in BOTH languages
    """
    t_75k = find_word_timestamp(
        all_words,
        ["75,000", "75000", "stops buying", "كتشري ليك السعادة", "لدخل معين"],
        default_t=2.6,
        min_t=1.2
    )
    t_kahneman = find_word_timestamp(
        all_words,
        ["2023", "kahneman", "killingsworth", "كانيمان", "كيلينغسوورث", "نوبل"],
        default_t=6.2,
        min_t=t_75k + 2.0
    )
    t_rising = find_word_timestamp(
        all_words,
        ["discovered", "keep rising", "200,000", "بينات", "كتزيد مع الدخل"],
        default_t=t_kahneman + 6.5,
        min_t=t_kahneman + 4.0
    )
    t_log = find_word_timestamp(
        all_words,
        ["linear dollars", "logarithmic", "50,000", "لوغاريتمية", "تصاعدية", "تدوبلو"],
        default_t=t_rising + 7.5,
        min_t=t_rising + 4.5
    )
    t_corr = find_word_timestamp(
        all_words,
        ["statistical correlation", "correlation", "0.09", "العلاقة", "ضعيفة", "0.09"],
        default_t=t_log + 11.5,
        min_t=t_log + 6.0
    )
    t_whr = find_word_timestamp(
        all_words,
        ["world happiness", "costa rica", "تقرير السعادة", "كوستاريكا"],
        default_t=t_corr + 12.5,
        min_t=t_corr + 6.0
    )
    t_hedonic = find_word_timestamp(
        all_words,
        ["adapt to material", "hedonic treadmill", "bigger house", "كيولف الماديات", "التعود المادي", "الطوموبيل"],
        default_t=t_whr + 11.5,
        min_t=t_whr + 6.0
    )
    t_pillars = find_word_timestamp(
        all_words,
        ["decades of behavioral", "elizabeth dunn", "harvard", "three things", "الأبحاث ديال جامعة هارفارد", "إليزابيث دان", "ثلاثة ديال"],
        default_t=t_hedonic + 11.0,
        min_t=t_hedonic + 6.0
    )
    t_step1 = find_word_timestamp(
        all_words,
        ["first, autonomy", "first", "autonomy", "buying back", "أول حاجة", "الأمان والحرية", "الأمان"],
        default_t=t_pillars + 10.0,
        min_t=t_pillars + 3.0
    )
    t_step2 = find_word_timestamp(
        all_words,
        ["second, shared", "second", "shared experiences", "memories", "تاني حاجة", "التجارب عوض", "التجارب"],
        default_t=t_step1 + 6.5,
        min_t=t_step1 + 3.5
    )
    t_step3 = find_word_timestamp(
        all_words,
        ["third, generosity", "third", "generosity", "spending on others", "تالت حاجة", "العشرة والعطاء", "العشرة"],
        default_t=t_step2 + 6.5,
        min_t=t_step2 + 3.5
    )
    t_outro = find_word_timestamp(
        all_words,
        ["terrible master", "meaningless scoreboard", "الفلوس وسيلة", "أكبر ربح"],
        default_t=max(total_duration - 14.0, t_pillars + 14.0),
        min_t=t_pillars + 8.0
    )

    # IMPORTANT: Study names, researchers, paper titles, journals, and visual headers are kept
    # strictly in ENGLISH for BOTH the English and Moroccan Darija videos!
    # Each visual beat lasts through the full explanation of its concept (up to next_beat - 1.2s).
    cues = [
        {
            "beat_id": 1,
            "idea": "2023 PNAS Adversarial Collaboration (Kahneman & Killingsworth)",
            "domain": "study_citation",
            "template": "study_citation",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "PNAS 2023 • DANIEL KAHNEMAN & MATTHEW KILLINGSWORTH",
            "headline": "Kahneman & Killingsworth settled the $75,000 happiness debate.",
            "title": "KAHNEMAN & KILLINGSWORTH (2023)",
            "badge": "PNAS • N = 33,391",
            "cards": [
                {
                    "badge": "NOBEL LAUREATE + PENN RESEARCHER",
                    "title": "Daniel Kahneman & Matthew Killingsworth (2023)",
                    "sub": "Adversarial Collaboration to Resolve the $75,000 Happiness Plateau",
                    "highlight": False
                },
                {
                    "badge": "PROCEEDINGS OF THE NATIONAL ACADEMY OF SCIENCES (2023)",
                    "title": "\"Income and emotional well-being: A conflict resolved\"",
                    "sub": "PNAS Vol. 120, No. 10 • 33,391 Adults • 1.7M Real-Time Points",
                    "highlight": True
                }
            ],
            "citation": {
                "journal": "PROCEEDINGS OF THE NATIONAL ACADEMY OF SCIENCES (MARCH 2023)",
                "title": "\"Income and emotional well-being: A conflict resolved\"",
                "authors": "Matthew A. Killingsworth, Daniel Kahneman & Barbara Mellers (PNAS)"
            },
            "start_time": max(2.8, t_kahneman),
            "end_time": max(t_kahneman + 6.8, t_rising - 1.1)
        },
        {
            "beat_id": 2,
            "idea": "Happiness Rises Beyond $75,000 to $200,000 and $500,000+",
            "domain": "threshold_counter",
            "template": "threshold_counter",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "KAHNEMAN & DEATON (2010) VS. PNAS (2023)",
            "headline": "Happiness keeps rising past $200,000 and $500,000.",
            "title": "BEYOND THE $75,000 PLATEAU",
            "badge": "$75K → $500K+",
            "citation": {
                "journal": "KAHNEMAN & DEATON (2010) VS. KILLINGSWORTH & KAHNEMAN (2023)",
                "title": "Experience Sampling Shows Well-Being Climbs Past $500,000",
                "authors": "PNAS Empirical Resolution • Real-Time Smartphone Sampling"
            },
            "start_time": t_rising,
            "end_time": max(t_rising + 7.2, t_log - 1.1)
        },
        {
            "beat_id": 3,
            "idea": "Logarithmic Income Law ($50K -> $100K -> $200K -> $400K -> $800K)",
            "domain": "log_income_curve",
            "template": "log_income_curve",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "LOGARITHMIC UTILITY STUDY • PNAS (2023)",
            "headline": "You must double your income for the same small happiness boost.",
            "title": "LOGARITHMIC VS. LINEAR INCOME",
            "badge": "$50K → $800K",
            "citation": {
                "journal": "LOGARITHMIC SCALING OF WELL-BEING • PNAS (2023)",
                "title": "$50K → $100K → $200K → $400K → $800K Equal Vertical Steps",
                "authors": "Every 2x Doubling Produces Only a Constant Marginal Happiness Step"
            },
            "start_time": t_log,
            "end_time": max(t_log + 8.5, t_corr - 1.2)
        },
        {
            "beat_id": 4,
            "idea": "Statistical Correlation r = 0.09 & Unhappiest 20% Flatline",
            "domain": "correlation_split",
            "template": "correlation_split",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "KILLINGSWORTH & KAHNEMAN (2023) • r = 0.09 EFFECT SIZE",
            "headline": "The statistical correlation with daily happiness is just 0.09.",
            "title": "CORRELATION r = 0.09 & BOTTOM 20%",
            "badge": "r = 0.09 ONLY",
            "citation": {
                "journal": "KILLINGSWORTH & KAHNEMAN (2023) • LUCAS ET AL. (2004)",
                "title": "Unhappiest 20% Flatten Above $100K While Happiest 80% Rise Slowly",
                "authors": "Synthesized in PWL Capital Research (Ben Felix, 'Finding a Good Life')"
            },
            "start_time": t_corr,
            "end_time": max(t_corr + 8.5, t_whr - 1.2)
        },
        {
            "beat_id": 5,
            "idea": "World Happiness Report: Costa Rica vs. US & Singapore",
            "domain": "country_comparison",
            "template": "country_comparison",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "WORLD HAPPINESS REPORT • OXFORD & GALLUP",
            "headline": "Costa Rica outranks the US and Singapore with a fraction of GDP.",
            "title": "COSTA RICA VS. US & SINGAPORE",
            "badge": "WORLD HAPPINESS REPORT",
            "citation": {
                "journal": "WORLD HAPPINESS REPORT • OXFORD WELLBEING RESEARCH CENTRE",
                "title": "Costa Rica (~$16K GDP/cap) Ranks Ahead of US & Singapore ($80K+)",
                "authors": "Gallup World Poll • Social Connection & Time Affluence Beat Raw GDP"
            },
            "start_time": t_whr,
            "end_time": max(t_whr + 8.5, t_hedonic - 1.2)
        },
        {
            "beat_id": 6,
            "idea": "The Hedonic Treadmill & Material Adaptation",
            "domain": "hedonic_treadmill",
            "template": "hedonic_treadmill",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "THE HEDONIC TREADMILL • LUCAS ET AL. (2004)",
            "headline": "The Hedonic Treadmill resets your material baseline in weeks.",
            "title": "THE HEDONIC TREADMILL",
            "badge": "BASELINE RESET",
            "citation": {
                "journal": "HEDONIC ADAPTATION STUDY • LUCAS, CLARK, GEORGELIS & DIENER (2004)",
                "title": "Material Upgrades (House / Luxury Car) Adapt Back to Baseline",
                "authors": "Journal of Personality and Social Psychology • Brickman & Campbell"
            },
            "start_time": t_hedonic,
            "end_time": max(t_hedonic + 8.5, t_pillars - 1.2)
        },
        {
            "beat_id": 7,
            "idea": "Harvard 85-Year Study & Elizabeth Dunn's 3 Pillars of Wealth",
            "domain": "three_pillars",
            "template": "three_pillars",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "HARVARD 85-YEAR STUDY & ELIZABETH DUNN (PNAS / SCIENCE)",
            "headline": "Money buys happiness only when converted into three things.",
            "title": "3 PILLARS OF HUMAN FLOURISHING",
            "badge": "HARVARD 85-YR STUDY",
            "citation": {
                "journal": "WHILLANS & DUNN (2017) PNAS • DUNN ET AL. (2008) SCIENCE • HARVARD",
                "title": "\"Buying time promotes happiness\" & \"The Good Life\" (85-Year Study)",
                "authors": "Elizabeth W. Dunn, Ashley V. Whillans, Robert Waldinger & Marc Schulz"
            },
            "step_timestamps": [t_step1, t_step2, t_step3],
            "start_time": t_pillars,
            "end_time": max(t_pillars + 18.0, t_outro - 0.7)
        }
    ]

    valid_cues = []
    safe_end_limit = max(10.0, total_duration - 5.0)
    for c in cues:
        st = round(max(2.6, float(c["start_time"])), 2)
        if valid_cues and st < valid_cues[-1]["end_time"] + 1.1:
            st = round(valid_cues[-1]["end_time"] + 1.1, 2)
        max_dur = 42.0 if c.get("template") == "three_pillars" else 14.5
        raw_en = float(c["end_time"])
        en = round(min(safe_end_limit, min(st + max_dur, max(st + 6.5, raw_en))), 2)
        if en - st >= 5.0 and st < safe_end_limit - 4.0:
            c["start_time"] = st
            c["end_time"] = en
            c["duration"] = round(en - st, 2)
            c["layout_mode"] = c.get("layout_mode", "split")
            c["split_height"] = c.get("split_height", 920)
            c["animation_type"] = c["template"]
            c["custom_render"] = True
            valid_cues.append(c)

    return valid_cues


def plan_storyboard(transcript_data, lang="en", use_ai=True):
    segments = transcript_data.get("segments", [])
    total_duration = float(transcript_data.get("duration", 25.0))
    all_words = [w for s in segments for w in s.get("words", [])]
    if all_words:
        total_duration = max(total_duration, float(all_words[-1]["end"]) + 0.3)

    full_text = (" ".join(s.get("text", "") for s in segments) + " " + str(transcript_data.get("reference_script", ""))).lower()

    is_money_happiness = any(k in full_text for k in ["kahneman", "killingsworth", "hedonic", "كانيمان", "كوستاريكا", "لوغاريتمية"])

    post_metadata = {}
    credit_usage = {}
    semantic_highlights = {}

    if use_ai:
        try:
            from scripts.vertex_ai_enhancer import enhance_storyboard_with_vertex_ai
            res = enhance_storyboard_with_vertex_ai(transcript_data, lang=lang)
            if res:
                post_metadata = res.get("post_metadata", {})
                credit_usage = res.get("credit_usage", {})
                semantic_highlights = res.get("semantic_highlights", {})
                if not is_money_happiness and res.get("cues"):
                    for idx, c in enumerate(res["cues"]):
                        c["layout_mode"] = "fullscreen"
                    return res["cues"], post_metadata, credit_usage, semantic_highlights
        except Exception as e:
            print(f"[storyboard_planner] Vertex AI metadata note: {e}")

    if is_money_happiness:
        print(f"[storyboard_planner] ✓ Planning Step 2 Beat Map (50/50 Split-Screen Light Visuals Above + Speaker Below, Longer Durations, English Studies) ({lang})!")
        cues = build_money_happiness_storyboard(all_words, total_duration, lang=lang)
        if not post_metadata:
            if lang in ["ary", "darija", "moroccan"]:
                post_metadata = {
                    "post_title": "واش بصح الفلوس كتشري السعادة؟ (Kahneman & Killingsworth PNAS 2023)",
                    "caption": "شحال هادي كنا كنسمعو بلي الفلوس مكتبقاش تشري السعادة فوق $75,000.\n\nفـ 2023، العالم الحائز على نوبل Daniel Kahneman والباحث Matthew Killingsworth نشرو دراسة حاسمة فمجلة PNAS:\n1️⃣ السعادة كتزيد بطريقة لوغاريتمية ($50k → $100k → $200k → $400k → $800k).\n2️⃣ العلاقة الإحصائية بين الدخل والسعادة اليومية يلاه r = 0.09.\n3️⃣ حسب Harvard Study of Adult Development (85-Year Study) وأبحاث Elizabeth Dunn، الفلوس كتشري السعادة غير إلا حولتيها لـ: الأمان والحرية (Autonomy & Time)، التجارب (Shared Experiences)، والعطاء (Generosity).\n\n📚 Academic Studies Referenced:\n• Killingsworth, Kahneman & Mellers (2023) — 'Income and emotional well-being: A conflict resolved', PNAS Vol. 120 No. 10\n• Whillans & Dunn (2017) — 'Buying time promotes happiness', PNAS\n• Dunn, Aknin & Norton (2008) — 'Spending Money on Others Promotes Happiness', Science\n• Waldinger & Schulz (2023) — Harvard Study of Adult Development ('The Good Life')\n• World Happiness Report — Oxford Wellbeing Research Centre & Gallup",
                    "save_cta": "خبي هاد الفيديو عندك باش تفكر علاش كتجمع الفلوس.",
                    "pinned_comment": "شنو هي الحاجة لي فنظرك كتعطي أكبر قيمة للفلوس: الوقت الحر (Autonomy)، التجارب (Experiences)، ولا العطاء (Generosity)؟",
                    "hashtags": ["#المغرب", "#الدارجة", "#الفلوس", "#السعادة", "#استثمار", "#حرية_مالية", "#علم_النفس", "#اقتصاد", "#تطوير_الذات", "#مراكش"]
                }
            else:
                post_metadata = {
                    "post_title": "The $75,000 Happiness Myth vs. The Logarithmic Wealth Law (PNAS 2023)",
                    "caption": "For years, we were told money stops buying happiness at $75,000. In 2023, Nobel laureate Daniel Kahneman and Matthew Killingsworth teamed up in PNAS to settle the conflict.\n\nHere is what the data actually shows:\n1️⃣ Happiness rises with LOGARITHMIC income ($50k → $100k → $200k → $400k → $800k require full doublings for the same small boost).\n2️⃣ The statistical correlation between log-income and daily happiness is just r = 0.09 — and for the unhappiest 20%, more money adds zero emotional well-being past $100k.\n3️⃣ Harvard's 85-Year Study & Elizabeth Dunn's research prove money only buys happiness when converted into Autonomy (buying back time), Shared Experiences, and Generosity.\n\n📚 Academic Citations:\n• Killingsworth, Kahneman & Mellers (2023) — 'Income and emotional well-being: A conflict resolved', PNAS Vol. 120, No. 10.\n• Whillans, Dunn et al. (2017) — 'Buying time promotes happiness', PNAS.\n• Dunn, Aknin & Norton (2008) — 'Spending Money on Others Promotes Happiness', Science.\n• Waldinger & Schulz (2023) — 'The Good Life' (Harvard Study of Adult Development).\n• World Happiness Report — Oxford Wellbeing Research Centre.",
                    "save_cta": "Save this reel as a reminder to build wealth for freedom, not for show.",
                    "pinned_comment": "Which of the 3 pillars gives you the highest return on money right now: Autonomy (time), Shared Experiences, or Generosity?",
                    "hashtags": ["#quantfinance", "#behavioraleconomics", "#danielkahneman", "#wealthmindset", "#financialfreedom", "#psychologyofmoney", "#harvardstudy", "#scienceexplained", "#investing", "#hedonictreadmill"]
                }
        return cues, post_metadata, credit_usage, semantic_highlights

    # Generic fallback for other scripts
    cues = []
    cur_t = 3.5
    templates = ["study_citation", "log_income_curve", "correlation_split", "country_comparison", "three_pillars"]
    idx = 0
    while cur_t < total_duration - 6.0:
        end_t = min(total_duration - 5.0, cur_t + 8.5)
        tpl = templates[idx % len(templates)]
        cues.append({
            "beat_id": idx + 1,
            "idea": f"Core Concept Beat {idx + 1}",
            "domain": tpl,
            "template": tpl,
            "animation_type": tpl,
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "QUANTITATIVE RESEARCH STUDY",
            "headline": "Empirical evidence and mathematical proof.",
            "title": "EMPIRICAL PROOF",
            "badge": "RESEARCH DATA",
            "start_time": round(cur_t, 2),
            "end_time": round(end_t, 2),
            "duration": round(end_t - cur_t, 2),
            "custom_render": True
        })
        idx += 1
        cur_t = end_t + 2.0

    return cues, post_metadata, credit_usage, semantic_highlights


def main():
    parser = argparse.ArgumentParser(description="Generate Step 2 Beat Map & 50/50 Split-Screen Light Editorial Storyboard cues.")
    parser.add_argument("--transcript", "-t", required=True, help="Input transcript JSON file")
    parser.add_argument("--output", "-o", default=None, help="Output storyboard JSON path")
    parser.add_argument("--lang", "-l", default="en", help="Language code (en or darija)")
    args = parser.parse_args()

    t_path = Path(args.transcript)
    if not t_path.exists():
        print(f"Error: {t_path} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(t_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    storyboard, post_metadata, credit_usage, semantic_highlights = plan_storyboard(data, lang=args.lang)
    out_path = Path(args.output) if args.output else t_path.parent / f"{t_path.stem}_storyboard.json"
    beat_map_path = out_path.parent / "beat_map.json"

    if semantic_highlights:
        data["semantic_highlights"] = semantic_highlights
        with open(t_path, "w", encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)

    payload = {
        "total_cues": len(storyboard),
        "design_theme": "Light Modern Editorial Studio (#F6F8FC Alabaster + #2563EB Royal Cobalt + #059669 Emerald)",
        "background_mode": "50/50 Split-Screen: 100% Opaque Top Visual (1080x920) + Bottom Speaker Talking (1080x1000)",
        "study_language_policy": "All study names, authors, journals, and headers in English",
        "storyboard": storyboard,
        "semantic_highlights": semantic_highlights,
        "post_metadata": post_metadata,
        "credit_usage": credit_usage
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    with open(beat_map_path, "w", encoding="utf-8") as bf:
        json.dump(payload, bf, indent=2, ensure_ascii=False)

    print(f"[storyboard_planner] Planned {len(storyboard)} 50/50 Split-Screen Light Editorial Beat Cues. Saved to {out_path} and {beat_map_path}")


if __name__ == "__main__":
    main()
