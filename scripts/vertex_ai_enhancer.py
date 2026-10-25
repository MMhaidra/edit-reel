#!/usr/bin/env python3
"""
vertex_ai_enhancer.py - Google Cloud Vertex AI & Discovery Engine Engagement Enhancer.

Leverages:
1. Vertex AI Gemini 2.5 Flash on 'general-app-dev-2026' (Monthly Free Credits):
   - Multimodal transcript analysis
   - High-impact viral hooks and on-screen headlines
   - High-retention Instagram caption, 'Save this' CTA, and debate-sparking pinned comment
2. Discovery Engine Semantic Ranking API on 'genai-app-builder-3500' (3,515.10 PLN Credit):
   - Reranks candidate viral hooks to select the #1 highest-converting opening visual
3. Seamless fallback: If credentials or network fail, gracefully falls back to local rules.
"""

import os
import sys
import json
import urllib.request
import subprocess
from pathlib import Path

# Add skill root to path
SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from motion_library.catalog import MOTION_CATALOG

PROJECT_DEV = "general-app-dev-2026"
PROJECT_GENAI = "genai-app-builder-3500"
LOCATION = "us-central1"


def get_access_token():
    """Retrieves Google Cloud OAuth2 access token via Application Default Credentials."""
    try:
        cmd = ["gcloud", "auth", "application-default", "print-access-token"]
        token = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        if token:
            return token
    except Exception:
        pass
    return None


def call_gemini_2_5_flash(prompt_text, token):
    """Invokes Vertex AI Gemini 2.5 Flash on general-app-dev-2026 with JSON output mode."""
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_DEV}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash:generateContent"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt_text}]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text), data.get("usageMetadata", {})
    except Exception as e:
        print(f"[vertex_ai_enhancer] Gemini 2.5 Flash request error: {e}")
        return None, {}


def rank_hooks_with_discovery_engine(hooks, query, token):
    """Reranks candidate hooks using Discovery Engine Semantic Ranking API on genai-app-builder-3500."""
    try:
        rank_url = f"https://discoveryengine.googleapis.com/v1/projects/{PROJECT_GENAI}/locations/global/rankingConfigs/default_ranking_config:rank"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        records = [{"id": str(i), "content": hook} for i, hook in enumerate(hooks)]
        payload = {
            "model": "semantic-ranker-512@latest",
            "query": query,
            "records": records
        }

        req = urllib.request.Request(rank_url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            ranked_records = res.get("records", [])
            if ranked_records:
                top_id = int(ranked_records[0]["id"])
                return hooks[top_id]
    except Exception as e:
        print(f"[vertex_ai_enhancer] Semantic ranker note: {e}")
    # Default to first hook if ranker fails
    return hooks[0] if hooks else "SYSTEMIC RISK"


def enhance_storyboard_with_vertex_ai(transcript_data, lang="en"):
    """
    Analyzes spoken transcript with Gemini 2.5 Flash and Semantic Ranker.
    Generates:
    1. Speech-tailored cues with dynamic headlines, badges, icons, and templates.
    2. Comprehensive Instagram Post Package (viral caption, Save CTA, pinned comment, hashtags).
    """
    token = get_access_token()
    if not token:
        print("[vertex_ai_enhancer] No ADC token available. Using local planner.")
        return None

    segments = transcript_data.get("segments", [])
    total_duration = transcript_data.get("duration", 25.0)
    full_transcript_text = " ".join([s.get("text", "") for s in segments])
    reference_script = transcript_data.get("reference_script", "")
    script_context = transcript_data.get("script_context", "")

    available_templates = list(MOTION_CATALOG.keys())

    script_section = ""
    if reference_script or script_context:
        script_section = f"""
Authoritative Reference Script & Context Provided by Creator:
\"\"\"{reference_script}\"\"\"
Additional Script Context / Notes:
\"\"\"{script_context}\"\"\"
(Use this reference script and context to ensure 100% accuracy for domain concepts, headlines, badges, semantic word highlights, and post metadata. If multiple takes appear in the transcript, prioritize the cleanest final take.)
"""

    system_prompt = f"""
You are an elite Instagram Reels content strategist for "Quant and the Physicist" (quantitative finance, macroeconomic policy, math, and system stability) and Moroccan Darija educational tech/finance content.
We have an automated video editing engine that burns in 2D motion graphics overlays on top of the video in 1080x1920 9:16 format.

Full Spoken Video Transcript:
\"\"\"{full_transcript_text}\"\"\"
{script_section}
Duration: {total_duration:.1f} seconds.
Language: {lang}

Available motion library templates to choose from:
{available_templates}

Your Task:
1. Provide 5 punchy opening viral hook headlines (3-5 words max, ALL CAPS) designed to stop scrollers in the first 2 seconds.
2. Segment the video into 3-5 visual motion graphics cues that match the speaker's argument.
   Each cue must have:
   - "start_time" (float)
   - "end_time" (float)
   - "duration" (float, minimum 4.5s so viewers can absorb it)
   - "domain" (one of the available templates)
   - "template" (same as domain)
   - "title" (3-5 words bold headline in ALL CAPS)
   - "badge" (2-3 words punchy pill badge like "+18.4% ALPHA" or "82% RISK EXPOSURE")
   - "icon" (appropriate icon name like 'trending-up', 'blocks', 'alert-triangle', 'network', 'landmark', 'candlestick-chart', 'brain', 'graduation-cap', 'atom', 'sigma', 'flame', 'shield-check')
3. Identify key spoken words from the transcript for Semantic Subtitle Color Highlighting:
   - "alpha": words related to money, growth, capital, profit, markets, stability, yield
   - "risk": words related to systemic risk, vulnerabilities, unbacked, crisis, challenges, loss
   - "tech": words related to AI, crypto, decentralized, quantum, physics, math, equations, thesis
4. Generate the Complete High-Engagement Instagram Post Package:
   - "post_title": A curiosity-driven Reel cover title.
   - "caption": A high-retention caption with open loops, concise educational value, and line breaks.
   - "save_cta": A call-to-action specifically encouraging saves (e.g. "Save this for your next macro risk briefing").
   - "pinned_comment": A debate-sparking question to drive high comments (the #1 interaction booster).
   - "hashtags": Array of 10 targeted niche hashtags.

Respond ONLY with valid JSON matching this schema:
{{
  "hook_candidates": ["HOOK 1", "HOOK 2", "HOOK 3", "HOOK 4", "HOOK 5"],
  "cues": [
    {{
      "start_time": 0.4,
      "end_time": 5.0,
      "duration": 4.6,
      "domain": "macro_markets",
      "template": "market_trend",
      "title": "CAPITAL MARKETS",
      "badge": "+18.4% ALPHA",
      "icon": "trending-up"
    }}
  ],
  "semantic_highlights": {{
    "alpha": ["markets", "capital"],
    "risk": ["vulnerabilities", "unbacked"],
    "tech": ["crypto-assets", "decentralized"]
  }},
  "post_metadata": {{
    "post_title": "...",
    "caption": "...",
    "save_cta": "...",
    "pinned_comment": "...",
    "hashtags": ["#tag1", "#tag2"]
  }}
}}
"""

    print("[vertex_ai_enhancer] Analyzing transcript & reference script context with Vertex AI Gemini 2.5 Flash...")
    ai_result, usage_meta = call_gemini_2_5_flash(system_prompt, token)
    if not ai_result:
        return None

    # Track credit usage in persistent ledger
    p_tokens = usage_meta.get("promptTokenCount", 900)
    c_tokens = usage_meta.get("candidatesTokenCount", 450)
    from scripts.progress_tracker import record_api_usage
    credit_summary = record_api_usage(
        prompt_tokens=p_tokens,
        output_tokens=c_tokens,
        ranker_queries=1,
        video_name=full_transcript_text[:45]
    )

    # Rerank opening hook candidates using Discovery Engine Semantic Ranker
    hooks = ai_result.get("hook_candidates", [])
    if hooks:
        rank_query = f"viral high engagement quantitative finance Instagram hook for: {full_transcript_text[:120]}"
        print(f"[vertex_ai_enhancer] Reranking {len(hooks)} hook candidates on 'genai-app-builder-3500'...")
        best_hook = rank_hooks_with_discovery_engine(hooks, rank_query, token)
        print(f"[vertex_ai_enhancer] Top-Ranked Opening Hook: '{best_hook}'")
        
        # Ensure first cue title or badge carries the winning hook
        if ai_result.get("cues"):
            ai_result["cues"][0]["badge"] = best_hook

    # Fill default colors from catalog
    enriched_cues = []
    for c in ai_result.get("cues", []):
        domain = c.get("domain", "macro_markets")
        cat_info = MOTION_CATALOG.get(domain, MOTION_CATALOG["macro_markets"])
        c["badge_color"] = cat_info.get("badge_color", (0, 255, 163, 230))
        c["accent_color"] = cat_info.get("accent_color", (0, 240, 255, 255))
        if "icon" not in c or not c["icon"]:
            c["icon"] = cat_info.get("icon", "trending-up")
        c["animation_type"] = cat_info.get("template", c.get("template", "market_trend"))
        c["template"] = cat_info.get("template", c.get("template", "market_trend"))
        c["custom_render"] = True
        enriched_cues.append(c)

    return {
        "cues": enriched_cues,
        "semantic_highlights": ai_result.get("semantic_highlights", {}),
        "post_metadata": ai_result.get("post_metadata", {}),
        "credit_usage": credit_summary,
        "source": "vertex_ai_gemini_2.5_flash"
    }


if __name__ == "__main__":
    test_transcript = {
        "duration": 25.0,
        "segments": [
            {"start": 0.4, "end": 4.5, "text": "Financial stability macroeconomic policy and capital markets"},
            {"start": 4.8, "end": 10.2, "text": "Module one Regulating the crypto ecosystem the case of unbacked crypto-assets"},
            {"start": 10.4, "end": 16.7, "text": "Primary scope regulatory challenges and systemic vulnerabilities arising from unbacked crypto-assets"},
            {"start": 16.9, "end": 24.8, "text": "Core thesis Although crypto-assets were designed to disintermediate finance operating in a decentralized manner"}
        ]
    }
    res = enhance_storyboard_with_vertex_ai(test_transcript, lang="en")
    print("\nResult:")
    print(json.dumps(res, indent=2))
