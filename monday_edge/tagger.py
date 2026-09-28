"""Weekend news tagging: category, risk tone, Trump statement vs action.

Rule-based by default. `--llm` sends titles (not bodies) to an Anthropic model
and merges the answer over the rule result. Fact and interpretation stay
separated: the rule tagger records its scores; the LLM tagger records its own
one-sentence summary as the model's words.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

CATEGORIES = ("geopolitical", "tariffs_trade", "fed_rates", "fiscal_politics",
              "energy", "financial_stress", "megacap_ai")

_CAT_WORDS = {
    "geopolitical": [r"\bwar\b", r"\bmissiles?\b", r"\bmilitary\b", r"\biran\b", r"\bisrael\b", r"\bhormuz\b",
                     r"\btaiwan\b", r"\bukraine\b", r"\brussia\b", r"\bhouthis?\b", r"\bcease-?fire\b",
                     r"\battacks?\b", r"\bnato\b", r"\bblockade\b", r"\bdrones?\b", r"\bnuclear\b"],
    "tariffs_trade": [r"\btariffs?\b", r"\btrade (?:deal|war|talks)\b", r"\bimport duties\b",
                      r"\bexport controls?\b", r"\breciprocal\b", r"\bcustoms\b"],
    "fed_rates": [r"\bfed\b", r"\bpowell\b", r"\brate (?:cut|hike)s?\b", r"\bfomc\b", r"\byields?\b",
                  r"\binflation\b", r"\bcpi\b", r"\bpce\b", r"\bpayrolls?\b", r"\brecession\b"],
    "fiscal_politics": [r"\bshutdown\b", r"\bdebt ceiling\b", r"\bspending bill\b", r"\bcontinuing resolution\b",
                        r"\belections?\b", r"\bsupreme court\b", r"\bcongress\b", r"\bstimulus\b"],
    "energy": [r"\bopec\b", r"\bcrude\b", r"\boil\b", r"\bbrent\b", r"\bwti\b", r"\bgasoline\b", r"\bnatural gas\b"],
    "financial_stress": [r"\bbank (?:failure|run)s?\b", r"\bdefault\b", r"\bbailout\b", r"\bcontagion\b",
                         r"\bdowngrades?\b", r"\bbankrupt(?:cy)?\b"],
    "megacap_ai": [r"\bnvidia\b", r"\bapple\b", r"\bmicrosoft\b", r"\bgoogle\b", r"\bamazon\b", r"\bmeta\b",
                   r"\btesla\b", r"\bopenai\b", r"\bai\b", r"\bchips?\b"],
}
CAT_RE = {c: re.compile("|".join(ws), re.I) for c, ws in _CAT_WORDS.items()}

RISK_ON_RE = re.compile(r"\bdeal\b|\bcease-?fire\b|\bagreement\b|\btruce\b|\brate cuts?\b|\bstimulus\b|\bpause[sd]?\b"
                        r"|\breopen(?:s|ed|ing)?\b|\bde-?escalat\w*|\bprogress\b", re.I)
RISK_OFF_RE = re.compile(r"\bescalat\w*|\battacks?\b|\bstrikes?\b|\bretaliat\w*|\bsanctions?\b|\bcollapse[sd]?\b"
                         r"|\bcrisis\b|\bthreat\w*|\breject\w*|\bshutdown\b|\bdefault\w*", re.I)
TRUMP_RE = re.compile(r"\btrump\b|\bwhite house\b|\bpresident\b|\bpotus\b", re.I)
ACTION_RE = re.compile(r"\bsigned\b|\bsigns\b|\bexecutive order\b|\bimposed?\b|\bimposes\b|\btakes effect\b"
                       r"|\blaunched\b|\bstruck\b|\bordered\b|\bbanned\b|\bauthorized\b", re.I)
STATEMENT_RE = re.compile(r"\bwill\b|\bmay\b|\bcould\b|\bconsider\w*|\bthreaten\w*|\bwarns?\b|\bexpects?\b"
                          r"|\bplans?\b|\bsays?\b|\bsoon\b|\bwants?\b|\bclaims?\b", re.I)
MARKET_RE = re.compile(r"\bmarkets?\b|\bstocks?\b|\beconomy\b|\bdollar\b|\bwall street\b|\bdow\b|\bnasdaq\b|\bs&p\b", re.I)


def _count(rx: re.Pattern, text: str) -> int:
    return len(rx.findall(text or ""))


def post_is_market_relevant(post: dict) -> bool:
    """Use the feed's own flag when present; else keyword fallback (documented)."""
    if post.get("market_relevant") is not None:
        return bool(post["market_relevant"])
    text = post.get("text") or ""
    return bool(MARKET_RE.search(text) or any(rx.search(text) for rx in CAT_RE.values()))


def tag_rules(headlines: list[dict], posts: list[dict], quiet_threshold: float = 3.0) -> dict:
    scores = Counter({c: 0.0 for c in CATEGORIES})
    relevant_texts: list[str] = []      # headlines hitting a category + relevant posts (for tone)
    trump_texts: list[str] = []         # category-hitting headlines that mention Trump/WH/President + posts
    market_posts = [p for p in posts if post_is_market_relevant(p)]

    for h in headlines:
        title = h.get("title") or ""
        w = 3.0 if h.get("is_major") else 1.0
        hit = False
        for c, rx in CAT_RE.items():
            if rx.search(title):
                scores[c] += w
                hit = True
        if hit:
            relevant_texts.append(title)
            if TRUMP_RE.search(title):
                trump_texts.append(title)
    for p in market_posts:
        text = p.get("text") or ""
        for c, rx in CAT_RE.items():
            if rx.search(text):
                scores[c] += 2.0
        relevant_texts.append(text)
        trump_texts.append(text)

    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], CATEGORIES.index(kv[0])))
    top, top_score = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 else ""
    category = top if top_score >= quiet_threshold else "quiet"

    tone = sum(_count(RISK_ON_RE, t) - _count(RISK_OFF_RE, t) for t in relevant_texts)
    risk_tone = "risk_on" if tone >= 2 else ("risk_off" if tone <= -2 else "mixed")

    act = sum(_count(ACTION_RE, t) for t in trump_texts)
    stmt = sum(_count(STATEMENT_RE, t) for t in trump_texts)
    if act > 0 and act >= 0.5 * stmt:
        trump_mode = "action"
    elif trump_texts:
        trump_mode = "statement"
    else:
        trump_mode = "none"

    return {
        "category": category,
        "category_2nd": second,
        "category_score": float(top_score),
        "risk_tone": risk_tone,
        "tone_score": int(tone),
        "trump_mode": trump_mode,
        "trump_action_hits": int(act),
        "trump_statement_hits": int(stmt),
        "n_headlines": len(headlines),
        "trump_market_posts": len(market_posts),
        "top_headlines": [h.get("title") or "" for h in headlines[:5]],
        "tagger": "rules",
        "summary": "",
        "surprise": None,
    }


# ----- LLM tagger -----

LLM_PROMPT = """You tag weekend market news for a study of what SPY/QQQ do after the Monday open.
Return JSON only, no prose, with exactly these keys:
- "category": one of {cats} or "quiet"
- "risk_tone": "risk_on", "risk_off" or "mixed"
- "trump_mode": "action" (the President did something concrete: signed, imposed, ordered, struck, banned),
  "statement" (said, threatened, predicted, or rejected something), or "none"
- "surprise": integer 1-5, how unexpected this weekend's news was for markets
- "summary": one sentence in your own words

Headlines (published between Friday 16:00 ET and Monday 09:30 ET):
{headlines}

Market-relevant presidential posts:
{posts}
"""


def tag_llm(headlines: list[dict], posts: list[dict], cfg, rules_result: dict) -> dict:
    """Merge an LLM tag over the rule result. Cached by SHA1(model + prompt). Falls back to rules on any failure."""
    try:
        import anthropic  # optional dependency
    except ImportError:
        out = dict(rules_result)
        out["summary"] = "LLM tagging unavailable: `anthropic` not installed"
        return out
    if not cfg.anthropic_api_key:
        out = dict(rules_result)
        out["summary"] = "LLM tagging unavailable: ANTHROPIC_API_KEY not set"
        return out
    market_posts = [p for p in posts if post_is_market_relevant(p)]
    h_lines = "\n".join(f"- {h.get('title', '')}" for h in headlines[:80]) or "(none)"
    p_lines = "\n".join(f"- {(p.get('text') or '')[:400]}" for p in market_posts[:20]) or "(none)"
    prompt = LLM_PROMPT.format(cats=", ".join(f'"{c}"' for c in CATEGORIES), headlines=h_lines, posts=p_lines)
    key = hashlib.sha1((cfg.llm_model + "\n" + prompt).encode("utf-8")).hexdigest()
    cache_dir = Path(cfg.cache_dir) / "llm"
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{key}.json"
    parsed = None
    if path.is_file():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            parsed = None
    if parsed is None:
        try:
            client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
            msg = client.messages.create(model=cfg.llm_model, max_tokens=400,
                                         messages=[{"role": "user", "content": prompt}])
            text = "".join(getattr(b, "text", "") for b in msg.content)
            i, j = text.find("{"), text.rfind("}")
            parsed = json.loads(text[i:j + 1]) if i >= 0 and j > i else {}
            path.write_text(json.dumps(parsed), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 — degrade to rules, never crash a build
            out = dict(rules_result)
            out["summary"] = f"LLM tagging failed: {type(exc).__name__}"
            return out
    out = dict(rules_result)
    cat = parsed.get("category")
    if cat in CATEGORIES or cat == "quiet":
        out["category"] = cat
    if parsed.get("risk_tone") in ("risk_on", "risk_off", "mixed"):
        out["risk_tone"] = parsed["risk_tone"]
    if parsed.get("trump_mode") in ("action", "statement", "none"):
        out["trump_mode"] = parsed["trump_mode"]
    try:
        s = int(parsed.get("surprise"))
        out["surprise"] = min(5, max(1, s))
    except (TypeError, ValueError):
        pass
    out["summary"] = str(parsed.get("summary") or "")[:300]
    out["tagger"] = "llm"
    return out


def tag_weekend(headlines: list[dict], posts: list[dict], cfg, use_llm: bool = False) -> dict:
    res = tag_rules(headlines, posts, cfg.quiet_threshold)
    if use_llm:
        res = tag_llm(headlines, posts, cfg, res)
    return res


def tone_vs_gap(risk_tone: str, gap_bucket: str) -> str:
    if gap_bucket in ("flat", "n/a") or risk_tone == "mixed":
        return "mixed/flat"
    up = gap_bucket.endswith("_up")
    if (risk_tone == "risk_on" and up) or (risk_tone == "risk_off" and not up):
        return "news agrees with gap"
    return "news opposes gap"
