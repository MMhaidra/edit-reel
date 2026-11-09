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


def build_unemployment_storyboard(all_words, total_duration, lang="en"):
    """
    Builds an acoustic-word-locked Beat Map for the 'Hidden Unemployment Crisis' script
    (English & Moroccan Darija) with State 2 'Paper & Objects' aesthetic.
    """
    if lang in ["ary", "darija", "moroccan"]:
        t_freeze = find_word_timestamp(all_words, ["تجميد التوظيف", "تجميد", "طرد", "البيبان مسدودة"], 21.0, min_t=12.0)
        t_2m = find_word_timestamp(all_words, ["جوج د المليون", "مليون", "مكتب إحصائيات", "أكتوبر 2026"], 45.0, min_t=t_freeze + 10.0)
        t_shift = find_word_timestamp(all_words, ["سبعة وعشرين", "27", "22.8", "العاطلين"], 62.0, min_t=t_2m + 10.0)
        t_duration = find_word_timestamp(all_words, ["المعدل المتوسط", "اثنين وعشرين", "ستة وعشرين", "نص عام"], 80.0, min_t=t_shift + 10.0)
        t_hysteresis = find_word_timestamp(all_words, ["تآكل المهارات", "تآكل", "المهارات", "القيمة التفاوضية"], 105.0, min_t=t_duration + 10.0)
        t_outro = find_word_timestamp(all_words, ["الحماية الحقيقية", "احتياط مالي", "داكشي علاش"], 125.0, min_t=t_hysteresis + 12.0)
    else:
        t_freeze = find_word_timestamp(all_words, ["freeze", "low-hire", "mass layoffs", "lagging"], 24.0, min_t=14.0)
        t_2m = find_word_timestamp(all_words, ["two million", "bureau of labor", "labor statistics", "six months"], 50.0, min_t=t_freeze + 12.0)
        t_shift = find_word_timestamp(all_words, ["twenty-seven", "27.6", "22.8", "share of job seekers"], 68.0, min_t=t_2m + 12.0)
        t_duration = find_word_timestamp(all_words, ["average stretch", "twenty-two", "twenty-six", "half a year"], 85.0, min_t=t_shift + 12.0)
        t_hysteresis = find_word_timestamp(all_words, ["hysteresis", "sidelines", "skills", "pricing power"], 110.0, min_t=t_duration + 12.0)
        t_outro = find_word_timestamp(all_words, ["never let", "flattering headline", "cash runway", "protection"], 132.0, min_t=t_hysteresis + 12.0)

    cues = [
        {
            "beat_id": 1,
            "idea": "The Low-Hire, Low-Fire Freeze & Headline Deception",
            "domain": "unemployment_iceberg",
            "template": "unemployment_iceberg",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "U.S. BUREAU OF LABOR STATISTICS • MACROECONOMIC LAGGING INDICATOR",
            "headline": "Headline unemployment looks low, but hiring is quietly locked shut.",
            "title": "LOW-HIRE FREEZE",
            "badge": "BLS MACRO DATA",
            "citation": {
                "journal": "U.S. BUREAU OF LABOR STATISTICS (OCTOBER 2026)",
                "title": "Current Population Survey: The Low-Hire, Low-Fire Phenomenon",
                "authors": "Macroeconomic Indicator Analysis • Labor Force Dynamics"
            },
            "start_time": t_freeze,
            "end_time": max(t_freeze + 14.0, t_2m - 1.2)
        },
        {
            "beat_id": 2,
            "idea": "Nearly 2 Million Americans Unemployed >6 Months",
            "domain": "jobless_2m_curve",
            "template": "jobless_2m_curve",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "BLS HISTORICAL SERIES LNS13008275 (1948–2026)",
            "headline": "Nearly 2,000,000 workers are now stuck in long-term unemployment.",
            "title": "2M LONG-TERM JOBLESS",
            "badge": "HISTORIC SPIKE",
            "citation": {
                "journal": "BLS SERIES LNS13008275 • UNEMPLOYED 27 WEEKS & OVER",
                "title": "Seasonally Adjusted Number of Long-Term Unemployed Persons",
                "authors": "U.S. Department of Labor Statistics • CPS Data Release"
            },
            "start_time": t_2m,
            "end_time": max(t_2m + 14.0, t_shift - 1.2)
        },
        {
            "beat_id": 3,
            "idea": "2-Year Structural Shift: 22.8% to 27.6% (Oct 2024 vs Oct 2026)",
            "domain": "long_term_shift_bar",
            "template": "long_term_shift_bar",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "BLS 24-MONTH COMPARISON (OCTOBER 2024 vs OCTOBER 2026)",
            "headline": "The share of long-term job seekers jumped +4.8% in just 2 years.",
            "title": "22.8% → 27.6% SURGE",
            "badge": "+4.8% SHIFT",
            "citation": {
                "journal": "BLS COMPARATIVE COHORT ANALYSIS (2024–2026)",
                "title": "Distribution of Total Unemployed by Duration of Unemployment",
                "authors": "CPS Historical Series • 27 Weeks and Longer Cohort"
            },
            "start_time": t_shift,
            "end_time": max(t_shift + 14.0, t_duration - 1.2)
        },
        {
            "beat_id": 4,
            "idea": "Average Unemployment Duration Surpasses 26 Weeks (>6 Months)",
            "domain": "unemployment_duration_timeline",
            "template": "unemployment_duration_timeline",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "BLS SERIES LNS13008276 • AVERAGE WEEKS UNEMPLOYED",
            "headline": "Losing a job now means waiting more than half a year for a paycheck.",
            "title": "AVERAGE >26 WEEKS",
            "badge": ">6 MONTHS",
            "citation": {
                "journal": "BLS SERIES LNS13008276 • AVERAGE DURATION OF UNEMPLOYMENT",
                "title": "Mean Weeks Unemployed: Rapid Climb from 22 to 26+ Weeks",
                "authors": "Bureau of Labor Statistics • National Labor Force Estimates"
            },
            "start_time": t_duration,
            "end_time": max(t_duration + 14.0, t_hysteresis - 1.2)
        },
        {
            "beat_id": 5,
            "idea": "Hysteresis: Skill Decay and Permanent Financial Damage",
            "domain": "hysteresis_card",
            "template": "hysteresis_card",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "NBER MACROECONOMICS ANNUAL (BLANCHARD & SUMMERS 1986)",
            "headline": "The longer workers wait, the faster skills, networks & pricing power erode.",
            "title": "HYSTERESIS DECAY",
            "badge": "SKILL EROSION",
            "citation": {
                "journal": "NBER MACROECONOMICS ANNUAL (VOL. 1, PP. 15–78)",
                "title": "Hysteresis and the European Unemployment Problem",
                "authors": "Olivier J. Blanchard & Lawrence H. Summers (1986)"
            },
            "start_time": t_hysteresis,
            "end_time": max(t_hysteresis + 16.0, t_outro - 0.8)
        }
    ]

    valid_cues = []
    safe_end_limit = max(10.0, total_duration - 4.5)
    for c in cues:
        st = round(max(2.6, float(c["start_time"])), 2)
        if valid_cues and st < valid_cues[-1]["end_time"] + 1.1:
            st = round(valid_cues[-1]["end_time"] + 1.1, 2)
        raw_en = float(c["end_time"])
        en = round(min(safe_end_limit, min(st + 16.0, max(st + 6.0, raw_en))), 2)
        if en - st >= 4.5 and st < safe_end_limit - 3.5:
            c["start_time"] = st
            c["end_time"] = en
            c["duration"] = round(en - st, 2)
            c["layout_mode"] = "split"
            c["split_height"] = 920
            c["animation_type"] = c["template"]
            c["custom_render"] = True
            valid_cues.append(c)

    return valid_cues


def build_false_needs_storyboard(all_words, total_duration, lang="en"):
    """
    Builds an acoustic-word-locked Beat Map for Herbert Marcuse's 'False Needs' & Consumerism
    (English & Moroccan Darija) with State 2 'Paper & Objects' aesthetic.
    """
    if lang in ["ary", "darija", "moroccan"]:
        t_marcuse = find_word_timestamp(all_words, ["ماركوز", "البعد الواحد", "الاحتياجات المزيفة", "الطوموبيل"], 13.0, min_t=8.0)
        t_brickman = find_word_timestamp(all_words, ["بريكمان", "دولاب التعود", "1978", "التعود المادي"], 36.0, min_t=t_marcuse + 10.0)
        t_kasser = find_word_timestamp(all_words, ["تيم كاسر", "كاسر", "الجانب المظلم", "الحلم الأمريكي"], 56.0, min_t=t_brickman + 10.0)
        t_bauer = find_word_timestamp(all_words, ["مونيكا باور", "باور", "مستهلك", "العلوم النفسية"], 78.0, min_t=t_kasser + 10.0)
        t_outro = find_word_timestamp(all_words, ["ماركوز حذرنا", "كنخسرو الحرية", "قبل ما تجري"], 100.0, min_t=t_bauer + 10.0)
    else:
        t_marcuse = find_word_timestamp(all_words, ["marcuse", "one-dimensional", "false needs", "automobile"], 14.0, min_t=9.0)
        t_brickman = find_word_timestamp(all_words, ["brickman", "hedonic", "treadmill", "1978", "lottery"], 38.0, min_t=t_marcuse + 10.0)
        t_kasser = find_word_timestamp(all_words, ["kasser", "dark side", "american dream", "1993", "vitality"], 58.0, min_t=t_brickman + 10.0)
        t_bauer = find_word_timestamp(all_words, ["bauer", "psychological science", "cuing", "consumer", "2012"], 80.0, min_t=t_kasser + 10.0)
        t_outro = find_word_timestamp(all_words, ["marcuse warned", "lose our freedom", "pause and ask"], 102.0, min_t=t_bauer + 10.0)

    cues = [
        {
            "beat_id": 1,
            "idea": "Herbert Marcuse (1964): One-Dimensional Man & Manufactured False Needs",
            "domain": "marcuse_false_needs",
            "template": "marcuse_false_needs",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "HERBERT MARCUSE (1964) • BEACON PRESS",
            "headline": "Modern society traps us through manufactured desires we mistake for our own.",
            "title": "FALSE NEEDS",
            "badge": "MARCUSE 1964",
            "citation": {
                "journal": "BEACON PRESS • BOSTON (1964)",
                "title": "One-Dimensional Man: Studies in the Ideology of Advanced Industrial Society",
                "authors": "Herbert Marcuse (Chapter 1: The New Forms of Control)"
            },
            "start_time": t_marcuse,
            "end_time": max(t_marcuse + 15.0, t_brickman - 1.2)
        },
        {
            "beat_id": 2,
            "idea": "Philip Brickman (1978): The Hedonic Treadmill & Dopamine Adaptation",
            "domain": "brickman_hedonic_treadmill",
            "template": "brickman_hedonic_treadmill",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "JOURNAL OF PERSONALITY AND SOCIAL PSYCHOLOGY (1978)",
            "headline": "Financial windfalls lose their emotional rush, forcing an endless upgrade loop.",
            "title": "HEDONIC TREADMILL",
            "badge": "BRICKMAN 1978",
            "citation": {
                "journal": "J. PERSONALITY & SOCIAL PSYCHOLOGY (VOL. 36, NO. 8, PP. 917–927)",
                "title": "Lottery winners and accident victims: Is happiness relative?",
                "authors": "Philip Brickman, Dan Coates & Ronnie Janoff-Bulman (1978)"
            },
            "start_time": t_brickman,
            "end_time": max(t_brickman + 15.0, t_kasser - 1.2)
        },
        {
            "beat_id": 3,
            "idea": "Kasser & Ryan (1993): A Dark Side of the American Dream",
            "domain": "kasser_ryan_dark_side",
            "template": "kasser_ryan_dark_side",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "JOURNAL OF PERSONALITY AND SOCIAL PSYCHOLOGY (1993)",
            "headline": "Prioritizing material wealth rewires the brain for anxiety and depression.",
            "title": "DARK SIDE OF WEALTH",
            "badge": "KASSER & RYAN 1993",
            "citation": {
                "journal": "J. PERSONALITY & SOCIAL PSYCHOLOGY (VOL. 65, NO. 2, PP. 410–422)",
                "title": "A dark side of the American dream: Correlates of financial success",
                "authors": "Tim Kasser & Richard M. Ryan (1993)"
            },
            "start_time": t_kasser,
            "end_time": max(t_kasser + 15.0, t_bauer - 1.2)
        },
        {
            "beat_id": 4,
            "idea": "Bauer et al. (2012): Cuing Consumerism & Societal Dissatisfaction",
            "domain": "bauer_cuing_consumerism",
            "template": "bauer_cuing_consumerism",
            "layout_mode": "split",
            "split_height": 920,
            "kicker": "PSYCHOLOGICAL SCIENCE (BAUER ET AL. 2012)",
            "headline": "Labeling someone a consumer immediately spikes insecurity and competitiveness.",
            "title": "INDIVIDUAL → CONSUMER",
            "badge": "BAUER 2012",
            "citation": {
                "journal": "PSYCHOLOGICAL SCIENCE (VOL. 23, NO. 5, PP. 517–523)",
                "title": "Cuing Consumerism: Situational Materialism Undermines Well-Being",
                "authors": "Monika A. Bauer, James E. B. Wilkie, Jung K. Kim & Galen V. Bodenhausen"
            },
            "start_time": t_bauer,
            "end_time": max(t_bauer + 15.0, t_outro - 0.8)
        }
    ]

    valid_cues = []
    safe_end_limit = max(10.0, total_duration - 4.5)
    for c in cues:
        st = round(max(2.6, float(c["start_time"])), 2)
        if valid_cues and st < valid_cues[-1]["end_time"] + 1.1:
            st = round(valid_cues[-1]["end_time"] + 1.1, 2)
        raw_en = float(c["end_time"])
        en = round(min(safe_end_limit, min(st + 16.0, max(st + 6.0, raw_en))), 2)
        if en - st >= 4.5 and st < safe_end_limit - 3.5:
            c["start_time"] = st
            c["end_time"] = en
            c["duration"] = round(en - st, 2)
            c["layout_mode"] = "split"
            c["split_height"] = 920
            c["animation_type"] = c["template"]
            c["custom_render"] = True
            valid_cues.append(c)

    return valid_cues


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

    is_unemployment = any(k in full_text for k in [
        "unemployment", "jobless", "hysteresis", "bureau of labor",
        "بطالة", "تجميد التوظيف", "تآكل المهارات", "مكتب إحصائيات"
    ])
    is_false_needs = any(k in full_text for k in [
        "marcuse", "one-dimensional", "brickman", "kasser", "bauer", "false needs",
        "ماركوز", "احتياجات مزيفة", "دولاب التعود", "تيم كاسر", "الجانب المظلم", "مونيكا باور"
    ])
    is_money_happiness = any(k in full_text for k in [
        "kahneman", "killingsworth", "hedonic", "كانيمان", "كوستاريكا", "لوغاريتمية"
    ]) and not is_unemployment and not is_false_needs

    post_metadata = {}
    credit_usage = {}
    semantic_highlights = {}

    if is_unemployment:
        print(f"[storyboard_planner] Planning Step 2 Beat Map for The Hidden Unemployment Crisis ({lang})!")
        cues = build_unemployment_storyboard(all_words, total_duration, lang=lang)
        if lang in ["ary", "darija", "moroccan"]:
            post_metadata = {
                "post_title": "الحقيقة الصادمة وراء أرقام البطالة: علاش ولات الرجعة للخدمة كتاخد نص عام؟",
                "caption": "فاش كتسمع بلي أرقام الشغل طالعة والبطالة هابطة، كيجيك الإحساس بلي الاقتصاد بخير، ولكن الواقع مختلف تماماً.\n\nالشركات ما بقاتش كتدير طرد جماعي، بل دخلات فـ مرحلة كيسميوها الاقتصاديين تجميد التوظيف (Low-Hire Freeze). قليل لي كيطردوه، ولكن البيبان مسدودة فـ وجه أي واحد كيقلب على فرصة جديدة.\n\nأرقام مكتب إحصائيات الشغل (BLS) حتى لأكتوبر 2026:\n[1] جوج د المليون ديال الناس جالسين بلا خدمة لأكثر من 6 أشهر.\n[2] نسبة العاطلين لأكثر من 27 سيمانة طلعات من 22.8% لـ 27.6% فـ عامين فقط.\n[3] المعدل المتوسط ديال الانتظار باش تلقى خدمة فات 26 سيمانة (أكثر من نص عام).\n\nفـ الاقتصاد، الخطر الكبير كيتسمى تآكل المهارات (Hysteresis): كلما طالت مدة العطالة، كلما ضعفات القيمة التفاوضية ديالك.\n\nالمصادر العلمية:\n• U.S. Bureau of Labor Statistics (BLS): Current Population Survey (Series LNS13008275 & LNS13008276)\n• Blanchard & Summers (1986): \"Hysteresis and the European Unemployment Problem\", NBER Macroeconomics Annual",
                "save_cta": "خبي هاد الفيديو باش تفكر ديما تبني احتياط مالي ديال 6 لـ 12 لشهر.",
                "pinned_comment": "واش كتحس بلي سوق الشغل دابا داخل فـ مرحلة تجميد (Low-Hire Freeze)؟ شاركنا تجربتك فـ الكومنت.",
                "hashtags": ["#المغرب", "#الدارجة", "#اقتصاد", "#شغل", "#بطالة", "#استثمار", "#حرية_مالية", "#تطوير_الذات", "#ذكاء_اصطناعي", "#مراكش"]
            }
        else:
            post_metadata = {
                "post_title": "The Hidden Unemployment Crisis: Why Getting Hired Now Takes Over 6 Months (BLS 2026)",
                "caption": "Headlines celebrate strong job numbers and a low 4.1% unemployment rate, but beneath the surface, companies have entered a low-hire, low-fire freeze.\n\nHere is what the latest U.S. Bureau of Labor Statistics data reveals:\n[1] Nearly 2,000,000 Americans have now been jobless for six months or longer.\n[2] Over just two years (Oct 2024 to Oct 2026), long-term unemployment jumped from 22.8% to 27.6%.\n[3] The average stretch of unemployment has climbed from 22 weeks to over 26 weeks — meaning the average job search now takes over half a year.\n\nEconomists call the ultimate trap Hysteresis: the longer workers sit on the sidelines, the faster skills and pricing power erode.\n\nAcademic & Data Sources:\n• U.S. Bureau of Labor Statistics: CPS Series LNS13008275 & LNS13008276.\n• Blanchard & Summers (1986): \"Hysteresis and the European Unemployment Problem\", NBER Macroeconomics Annual.",
                "save_cta": "Save this reel as a guide to building a 6-12 month cash runway in a frozen job market.",
                "pinned_comment": "Are you seeing the low-hire freeze in your industry? Share what you are noticing below.",
                "hashtags": ["#macroeconomics", "#economy", "#unemployment", "#jobmarket", "#hiringfreeze", "#finance", "#investing", "#wealthmindset", "#careertips", "#blsdata"]
            }
        return cues, post_metadata, credit_usage, semantic_highlights

    if is_false_needs:
        print(f"[storyboard_planner] Planning Step 2 Beat Map for Herbert Marcuse & False Needs ({lang})!")
        cues = build_false_needs_storyboard(all_words, total_duration, lang=lang)
        if lang in ["ary", "darija", "moroccan"]:
            post_metadata = {
                "post_title": "علاش كتبقى ديما مزير وعياّن واخا الصالير كيزيد؟ (هربرت ماركوز ودولاب التعود المادي)",
                "caption": "فـ 1964، الفيلسوف هربرت ماركوز كتب فـ كتابو الشهير \"الإنسان ذو البعد الواحد\" بلي المجتمع ما بقاش كيحتاج للقوة باش يتحكم فينا، بل كيحكمنا عن طريق الاحتياجات المزيفة (False Needs).\n\nرغبات مصنوعة ديال الاستهلاك لي كتخلينا نخدمو بلا توقف باش نشريو حوايج كيبنجونا مؤقتاً.\n\nشنو تبت العلم من بعد؟\n[1] فيليب بريكمان (1978): أتبت وجود دولاب التعود المادي (Hedonic Treadmill) — أي ترقية أو ربح مالي كيتلاشى النشوة ديالو دغيا وترجع لنفس نقطة البداية.\n[2] تيم كاسر وريتشارد ريان (1993): الدراسة التاريخية \"الجانب المظلم للحلم الأمريكي\" أتبتات أن التركيز على المظاهر والفلوس كيرفع القلق، التوتر، والاكتئاب مباشرة.\n[3] مونيكا باور (2012): غير تشوف إعلانات أو يتسمى الإنسان \"مستهلك\" عوض \"فرد\"، كيطلع عندو الستريس وعدم الأمان فـ البلاصة.\n\nالدراسات المرجعية:\n• Marcuse (1964) — One-Dimensional Man (Beacon Press)\n• Brickman, Coates & Janoff-Bulman (1978) — Journal of Personality & Social Psychology\n• Kasser & Ryan (1993) — Journal of Personality & Social Psychology\n• Bauer et al. (2012) — Psychological Science",
                "save_cta": "بارطاجي هاد الفيديو مع شي حد عزيز عليك كيخدم بلا قياس باش يوقف ويسول راسو هاد السؤال.",
                "pinned_comment": "واش فايت حسيتي بدولاب التعود المادي: كتشري حاجة جديدة ودغيا كتلفها وترجع لنفس الإحساس؟",
                "hashtags": ["#المغرب", "#الدارجة", "#علم_النفس", "#فلسفة", "#هربرت_ماركوز", "#استثمار", "#حرية_مالية", "#تطوير_الذات", "#راحة_البال", "#سعادة"]
            }
        else:
            post_metadata = {
                "post_title": "Why Making More Money Still Feels Broke: Herbert Marcuse & The Hedonic Treadmill",
                "caption": "In 1964, philosopher Herbert Marcuse predicted why modern life feels exhausting no matter how much income grows. Decades later, psychology proved he was right.\n\nIn One-Dimensional Man, Marcuse introduced \"false needs\": manufactured desires for luxury and endless upgrades that keep us trapped working exhausting jobs to buy things we do not need.\n\nWhat Psychological Research Discovered:\n[1] Philip Brickman (1978): Proved the Hedonic Treadmill — material upgrades give a temporary dopamine rush before quickly resetting to baseline, keeping you constantly chasing the next hit.\n[2] Tim Kasser & Richard Ryan (1993): Published \"A Dark Side of the American Dream\", showing that prioritizing financial status directly correlates with higher anxiety, lower vitality, and depression.\n[3] Monika Bauer (2012): Found that merely viewing luxury cues or being labeled a \"consumer\" instead of an \"individual\" immediately triggers stress and competitiveness.\n\nLandmark Research Citations:\n• Marcuse (1964) — One-Dimensional Man (Beacon Press)\n• Brickman et al. (1978) — Journal of Personality and Social Psychology\n• Kasser & Ryan (1993) — Journal of Personality and Social Psychology\n• Bauer et al. (2012) — Psychological Science",
                "save_cta": "Save this reel as a reminder before chasing your next lifestyle upgrade.",
                "pinned_comment": "What is one purchase you thought would change your life, but you adapted to within two weeks?",
                "hashtags": ["#psychology", "#philosophy", "#herbertmarcuse", "#hedonictreadmill", "#consumerism", "#mentalhealth", "#wealthmindset", "#financialfreedom", "#mindset", "#productivity"]
            }
        return cues, post_metadata, credit_usage, semantic_highlights

    if is_money_happiness:
        print(f"[storyboard_planner] Planning Step 2 Beat Map (Money vs Happiness) ({lang})!")
        cues = build_money_happiness_storyboard(all_words, total_duration, lang=lang)
        return cues, post_metadata, credit_usage, semantic_highlights

    # Generic fallback
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
