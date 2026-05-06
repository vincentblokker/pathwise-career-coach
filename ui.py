"""Pathwise UI helpers — SVG glyphs, brand markup, and the persistent shell.

Streamlit renders raw HTML through `st.markdown(..., unsafe_allow_html=True)`,
so every helper here returns either an HTML string (for composing) or writes
directly via Streamlit when convenient.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Iterable, Sequence

import streamlit as st

STATIC_DIR = Path(__file__).parent / "static"
BRAND_CSS = STATIC_DIR / "brand.css"

STEP_LABELS = ("Welcome", "Resume", "Interview", "Roadmap", "Recap")


# --- Bootstrap --------------------------------------------------------------


def inject_brand_css() -> None:
    css = BRAND_CSS.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --- SVG glyphs -------------------------------------------------------------


def path_glyph(size: int = 24, color: str = "var(--pw-sage)", accent: str = "var(--pw-amber)") -> str:
    """Compact stepped-horizon mark for inline use (lockups, headers)."""
    return f'''<svg width="{size}" height="{size}" viewBox="14 4 72 88" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="20" y="64" width="14" height="22" rx="7" fill="{color}"/>
  <rect x="43" y="48" width="14" height="38" rx="7" fill="{color}"/>
  <rect x="66" y="30" width="14" height="56" rx="7" fill="{color}"/>
  <circle cx="73" cy="14" r="7.5" fill="{accent}"/>
</svg>'''


def lockup(size: int = 22, color: str = "var(--pw-ink)") -> str:
    """Wordmark + glyph — used in the top shell."""
    glyph = path_glyph(size=int(size * 1.5))
    return f'''<div style="display:inline-flex;align-items:center;gap:{int(size*0.36)}px;">
  {glyph}
  <span style="font-family:var(--pw-font-display);font-weight:700;font-size:{size}px;letter-spacing:-0.025em;color:{color};">Pathwise</span>
</div>'''


def monogram(size: int = 80) -> str:
    r = round(size * 0.22)
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="0" y="0" width="100" height="100" rx="{r * 100 // size}" fill="var(--pw-cream)"/>
  <rect x="20" y="64" width="14" height="22" rx="7" fill="var(--pw-sage)"/>
  <rect x="43" y="48" width="14" height="38" rx="7" fill="var(--pw-sage)"/>
  <rect x="66" y="30" width="14" height="56" rx="7" fill="var(--pw-sage)"/>
  <circle cx="73" cy="14" r="7.5" fill="var(--pw-amber)"/>
</svg>'''


def glyph_animated(size: int = 22) -> str:
    """A tiny redrawing-glyph used inside the 'Coach is thinking…' spinner."""
    return f'''<svg width="{size}" height="{size}" viewBox="14 4 72 88" fill="none" xmlns="http://www.w3.org/2000/svg" class="pw-glyph-anim" aria-hidden="true">
  <rect x="20" y="64" width="14" height="22" rx="7" fill="var(--pw-sage)"/>
  <rect x="43" y="48" width="14" height="38" rx="7" fill="var(--pw-sage)"/>
  <rect x="66" y="30" width="14" height="56" rx="7" fill="var(--pw-sage)"/>
  <circle cx="73" cy="14" r="7.5" fill="var(--pw-amber)"/>
</svg>'''


# --- Top shell --------------------------------------------------------------


def stepper(step: int) -> str:
    parts: list[str] = ['<div class="pw-stepper">']
    for i, label in enumerate(STEP_LABELS):
        state = "done" if i < step else ("active" if i == step else "pending")
        parts.append(
            f'<div class="step {state}">'
            f'<span class="dot"></span>'
            f'<span class="lbl">{escape(label)}</span>'
            f'</div>'
        )
        if i < len(STEP_LABELS) - 1:
            seg_state = "done" if i < step else ""
            parts.append(f'<span class="seg {seg_state}"></span>')
    parts.append("</div>")
    return "".join(parts)


def top_shell(step: int, target_role: str, initials: str) -> None:
    """Render the persistent header (logo + stepper + persona chip).

    Note: in this Streamlit port the 'New session' control is rendered as a
    Streamlit button next to the chip via columns so it remains clickable.
    """
    left = (
        '<div class="pw-shell-left">'
        f'{lockup(size=18)}'
        '<span class="pw-shell-divider"></span>'
        f'{stepper(step)}'
        '</div>'
    )
    chip = (
        '<div class="pw-profile-chip">'
        '<span style="color:var(--pw-ink-soft);">Coaching</span>'
        f'<strong>{escape(target_role)}</strong>'
        f'<span class="pa">{escape(initials)}</span>'
        '</div>'
    )
    col_main, col_chip, col_btn = st.columns([6, 3, 1.4], gap="small")
    with col_main:
        st.markdown(f'<div class="pw">{left}</div>', unsafe_allow_html=True)
    with col_chip:
        st.markdown(
            f'<div class="pw" style="display:flex;justify-content:flex-end;align-items:center;height:100%;">{chip}</div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("↻ New session", key=f"newsess_{step}", help="Reset and start a new coaching session"):
            for k in ("step", "memory", "outputs", "profile", "expanded_qs", "practiced_qs"):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    st.markdown('<div class="pw"><hr class="pw-divider" style="margin: 6px 0 18px;"/></div>', unsafe_allow_html=True)


# --- Coach line -------------------------------------------------------------


def coach_line(text: str, signature: str = "Coach") -> None:
    html = (
        '<div class="pw"><div class="pw-coach">'
        f'<div class="pw-coach-avatar">{path_glyph(size=18, color="var(--pw-cream)")}</div>'
        '<div style="flex:1;min-width:0;">'
        f'<div class="sig">{escape(signature)}</div>'
        f'<div class="body">{escape(text)}</div>'
        '</div></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# --- Bullet list (resume) ---------------------------------------------------


def bullet_card(title: str, bullets: Sequence[str]) -> None:
    items = "".join(
        f'<li><span class="num">{i + 1:02d}</span><p class="text">{escape(b)}</p></li>'
        for i, b in enumerate(bullets)
    )
    html = (
        '<div class="pw">'
        '<div class="pw-card pw-card-flush">'
        '<div class="pw-card-header">'
        f'<div class="pw-card-title">{path_glyph(size=18)}<span>{escape(title)}</span></div>'
        '<span class="pw-hint">ATS-friendly · action-led · quantified</span>'
        '</div>'
        f'<ol class="pw-bullets">{items}</ol>'
        '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# --- Question card (interview) ----------------------------------------------


def question_card(index: int, question: str, hint: str, tags: Sequence[str], expanded: bool) -> None:
    tag_html = "".join(f'<span class="qtag">{escape(t)}</span>' for t in tags)
    hint_html = (
        '<div class="qhint">'
        '<span class="label">Coach hint</span>'
        f'{escape(hint)}'
        '</div>'
        if expanded
        else ""
    )
    html = (
        '<div class="pw"><div class="pw-qcard">'
        '<div class="pw-qcard-row">'
        f'<span class="qnum">Q{index:02d}</span>'
        '<div style="flex:1;min-width:0;">'
        f'<p class="qtext">{escape(question)}</p>'
        f'<div class="qtags">{tag_html}</div>'
        f'{hint_html}'
        '</div></div></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# --- Roadmap lane card ------------------------------------------------------


_ICON_BOOK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'
)
_ICON_PEOPLE = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
    '<circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
)
_ICON_SPARK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v6M12 16v6M2 12h6M16 12h6M5 5l4 4M15 15l4 4M19 5l-4 4M9 15l-4 4"/></svg>'
)

LANE_ICONS = {"courses": _ICON_BOOK, "networking": _ICON_PEOPLE, "projects": _ICON_SPARK}


def lane_card_html(title: str, kind: str, items: Iterable[dict]) -> str:
    icon = LANE_ICONS.get(kind, _ICON_SPARK)
    li = []
    for it in items:
        meta_parts = [f'<span class="mono">{escape(it.get("cadence") or it.get("weeks") or "")}</span>']
        if it.get("priority"):
            meta_parts += [
                '<span class="sep"></span>',
                f'<span class="pri">{escape(it["priority"])}</span>',
            ]
        if it.get("price"):
            meta_parts += [
                '<span class="sep"></span>',
                f'<span>{escape(it["price"])}</span>',
            ]
        li.append(
            '<li>'
            f'<div class="iname">{escape(it["name"])}</div>'
            f'<div class="imeta">{"".join(meta_parts)}</div>'
            '</li>'
        )
    return (
        '<div class="pw-lane">'
        f'<h4><span class="icon">{icon}</span>{escape(title)}</h4>'
        f'<ul>{"".join(li)}</ul>'
        '</div>'
    )


# --- Roadmap milestone path -------------------------------------------------


_MILESTONE_CY = [60, 45, 30, 50, 75, 50]


def milestone_path_html(milestones: Sequence[dict]) -> str:
    nodes = []
    for i, m in enumerate(milestones[:6]):
        first_cls = " first" if i == 0 else ""
        cy = _MILESTONE_CY[i]
        nodes.append(
            f'<div class="pw-milestone{first_cls}" style="padding-top:{cy - 8}px;">'
            '<div class="node"></div>'
            '<div class="meta">'
            f'<div class="mlabel">{escape(m["m"])}</div>'
            f'<div class="mtitle">{escape(m["title"])}</div>'
            f'<div class="mtext">{escape(m["text"])}</div>'
            '</div></div>'
        )
    svg = (
        '<svg class="pw-path" viewBox="0 0 1000 120" preserveAspectRatio="none">'
        '<path d="M40 60 C 180 60, 200 30, 340 30 C 480 30, 500 80, 660 80 C 800 80, 820 40, 960 40" '
        'stroke="var(--pw-sage)" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
        '<path d="M952 32 L968 38 L962 50" stroke="var(--pw-sage)" stroke-width="2.5" '
        'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    )
    return (
        '<div class="pw"><div class="pw-path-wrap">'
        f'{svg}'
        f'<div class="pw-milestones">{"".join(nodes)}</div>'
        '</div></div>'
    )


# --- Recap fragments --------------------------------------------------------


def kv_grid(items: Sequence[tuple[str, str]]) -> str:
    cells = "".join(
        f'<div class="pw-kv"><span class="label">{escape(k)}</span>'
        f'<div class="value">{escape(v)}</div></div>'
        for k, v in items
    )
    return f'<div class="pw-kv-grid">{cells}</div>'


def chips(items: Iterable[str]) -> str:
    return "".join(f'<span class="pw-chip">{escape(c)}</span>' for c in items)


def milestone_tile_grid(milestones: Sequence[dict]) -> str:
    tiles = "".join(
        '<div class="pw-mtile">'
        f'<div class="m">{escape(m["m"])}</div>'
        f'<div class="t">{escape(m["title"])}</div>'
        f'<div class="x">{escape(m["text"])}</div>'
        '</div>'
        for m in milestones
    )
    return f'<div class="pw-mtile-grid">{tiles}</div>'


def recap_question_block(index: int, q: str, hint: str) -> str:
    return (
        '<div class="pw-recap-q">'
        f'<span class="qid">Q{index:02d}</span>'
        f'<span class="q">{escape(q)}</span>'
        f'<p class="h"><strong>Hint · </strong>{escape(hint)}</p>'
        '</div>'
    )


# --- Decorative welcome path ------------------------------------------------


def deco_path() -> str:
    return (
        '<div class="pw-decopath">'
        '<svg width="320" height="80" viewBox="0 0 320 80" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 60 C 50 60, 60 30, 110 30 C 160 30, 170 55, 220 50 C 270 45, 280 18, 310 14" '
        'stroke="var(--pw-sage)" stroke-width="1.5" fill="none" stroke-dasharray="4 6"/>'
        '<path d="M302 8 L312 12 L308 22" stroke="var(--pw-sage)" stroke-width="1.5" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg></div>'
    )
