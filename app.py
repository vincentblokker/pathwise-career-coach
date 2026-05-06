"""Pathwise — Personalized AI Career Coach.

Streamlit port of the Pathwise design (Claude Design handoff, 2026-05-06).
ADA AI Professional · Module 7 · final assignment.
"""
from __future__ import annotations

import os
from html import escape

import streamlit as st
from dotenv import load_dotenv

from chains import build_chains, new_memory, remember
from ui import (
    bullet_card,
    chips,
    coach_line,
    deco_path,
    inject_brand_css,
    kv_grid,
    lane_card_html,
    lockup,
    milestone_path_html,
    milestone_tile_grid,
    path_glyph,
    question_card,
    recap_question_block,
    top_shell,
)


load_dotenv()

st.set_page_config(
    page_title="Pathwise — AI Career Coach",
    page_icon="🪴",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_brand_css()


# --- Sample / default profile (Sara, the Claude-Design persona) -------------

DEFAULT_PROFILE = {
    "target_role": "Product Manager (SaaS)",
    "current_role": "Senior Marketing Manager",
    "persona": "Career Switcher · Marketing → Tech",
    "tone": "Encouraging",
    "goal": "Move into product management at a SaaS scale-up within 6 months.",
    "skills": [
        "Customer research",
        "Cross-functional leadership",
        "Roadmapping",
        "A/B testing",
        "SQL (basic)",
        "Figma",
        "Stakeholder comms",
    ],
}

PERSONAS = (
    "Junior Data Scientist",
    "Career Switcher · Marketing → Tech",
    "High School Graduate",
    "Return-to-Work Parent",
    "Freelancer going full-time",
)
TONES = ("Professional", "Friendly", "Direct", "Encouraging")

SAMPLE_JD = """Product Manager — Growth · Lumen (Series C SaaS)

We're looking for a PM to own the activation surface area: the first 14 days of a new account. You'll partner with a dedicated growth squad (3 eng, 1 designer, 1 data scientist) and report to the Director of Product, Growth.

What you'll do
• Define and ship experiments across onboarding, in-product education, and lifecycle email
• Set the activation north-star and weekly leading indicators
• Run weekly experiment review with the squad and monthly business review with leadership
• Partner closely with marketing and CS to align messaging end-to-end

What we're looking for
• 3+ years of PM experience, ideally with a quantitative or growth-focused background
• Comfort with SQL, experimentation frameworks, and reasoning about funnels
• Strong written communication; you can frame a problem in a one-pager
• Track record of taking a product area from messy to measurable"""


# --- State ------------------------------------------------------------------


def init_state() -> None:
    defaults = {
        "step": 0,
        "memory": new_memory(),
        "outputs": {},
        "profile": dict(DEFAULT_PROFILE),
        "expanded_qs": set(),
        "practiced_qs": set(),
        "job_description": SAMPLE_JD,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_state()

profile = st.session_state.profile


# --- Hard-stop if no API key -----------------------------------------------


if not os.getenv("OPENAI_API_KEY"):
    st.markdown('<div class="pw">' + lockup(size=22) + "</div>", unsafe_allow_html=True)
    st.error("`OPENAI_API_KEY` is missing from `.env`. Add it and rerun the app.")
    st.stop()


# --- Helpers ----------------------------------------------------------------


def goto(step: int) -> None:
    st.session_state.step = max(0, min(4, step))
    st.rerun()


def make_initials(full_name: str) -> str:
    parts = [p for p in full_name.split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "P"


# --- Screens ----------------------------------------------------------------


def screen_welcome() -> None:
    top_shell(0, profile["target_role"], make_initials("Sara Lindqvist"))

    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown(
            '<div class="pw pw-hero" style="padding: 32px 8px 0 0;">'
            '<span class="pw-eyebrow">Session 01 · Coaching</span>'
            "<h1>Let's map your<br/>next move.</h1>"
            "<p>Tell us where you're heading. In about ten minutes, you'll walk away with tailored "
            "resume bullets, an interview prep set, and a six-month plan you can actually follow.</p>"
            '<div class="meta-line">'
            '<div class="dots"><span></span><span></span><span></span></div>'
            "<span>3 coaching steps · ~10 min · private to you</span>"
            "</div>"
            f"{deco_path()}"
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="pw" style="padding: 8px 0 0 0;">'
            '<div class="pw-card">'
            '<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
            f'{path_glyph(size=22)}'
            '<span style="font-family:var(--pw-font-display);font-weight:600;font-size:15px;">Your profile</span>'
            "</div></div></div>",
            unsafe_allow_html=True,
        )

        with st.form("profile_form", clear_on_submit=False, border=False):
            c1, c2 = st.columns(2)
            with c1:
                target_role = st.text_input("Target role", value=profile["target_role"])
            with c2:
                persona = st.selectbox(
                    "Persona",
                    PERSONAS,
                    index=PERSONAS.index(profile["persona"]) if profile["persona"] in PERSONAS else 1,
                )
            goal = st.text_area("Career goal · one sentence", value=profile["goal"], height=80)
            skills_text = st.text_input(
                "Current skills (comma-separated)",
                value=", ".join(profile["skills"]),
            )
            tone = st.radio(
                "Coaching tone",
                TONES,
                index=TONES.index(profile["tone"]) if profile["tone"] in TONES else 3,
                horizontal=True,
            )
            st.markdown(
                '<div class="pw" style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">'
                '<span class="pw-hint">Takes about 10 minutes · you can edit anything later</span>'
                "</div>",
                unsafe_allow_html=True,
            )
            submitted = st.form_submit_button("Start coaching →", type="primary", use_container_width=False)
            if submitted:
                st.session_state.profile = {
                    **profile,
                    "target_role": target_role.strip() or profile["target_role"],
                    "persona": persona,
                    "goal": goal.strip(),
                    "skills": [s.strip() for s in skills_text.split(",") if s.strip()],
                    "tone": tone,
                }
                goto(1)


def screen_resume() -> None:
    top_shell(1, profile["target_role"], make_initials("Sara Lindqvist"))

    st.markdown(
        '<div class="pw" style="max-width:880px;margin:0 auto;">'
        '<span class="pw-eyebrow">Step 1 of 3 · Resume bullets</span>'
        "<h1 style='margin-top:6px;font-size:38px;'>Five bullets, tailored to your move.</h1>"
        "<p class='pw-hint' style='font-size:16px;max-width:620px;'>Drafted from your goal and skills "
        "— ATS-friendly, action-led, and quantified where the work actually was.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    container = st.container()
    with container:
        outputs = st.session_state.outputs
        if "resume" not in outputs:
            with st.spinner("Drafting your bullets…"):
                chains = build_chains(st.session_state.memory)
                result = chains.resume.invoke(
                    {
                        "audience": profile["persona"],
                        "tone": profile["tone"].lower(),
                        "job_title": profile["target_role"],
                        "skills": ", ".join(profile["skills"]),
                    }
                )
                bullets = list(result.bullets)
                outputs["resume"] = bullets
                remember(
                    st.session_state.memory,
                    f"[step 1] resume bullets for {profile['target_role']}",
                    "\n".join(f"- {b}" for b in bullets),
                )

        bullets = outputs["resume"]

        coach_line(
            "Nice — here's a draft of your bullets. Tweak anything that doesn't sound like you. "
            "Bullets 2 and 3 are the strongest evidence; lead with those on a SaaS application."
        )

        st.markdown(
            f'<div style="max-width:880px;margin:0 auto;">',
            unsafe_allow_html=True,
        )
        bullet_card(f"Resume bullets · {profile['target_role']}", bullets)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="max-width:880px;margin:24px auto 0;">', unsafe_allow_html=True)
    nav_a, nav_b, nav_c = st.columns([1, 4, 2])
    with nav_a:
        if st.button("← Back", key="back_resume"):
            goto(0)
    with nav_b:
        st.markdown('<span class="pw-hint">Edit any bullet inline · regenerate one at a time</span>', unsafe_allow_html=True)
    with nav_c:
        if st.button("Continue to interview prep →", key="next_resume", type="secondary"):
            goto(2)
    st.markdown("</div>", unsafe_allow_html=True)


def screen_interview() -> None:
    top_shell(2, profile["target_role"], make_initials("Sara Lindqvist"))

    st.markdown(
        '<div class="pw">'
        '<span class="pw-eyebrow">Step 2 of 3 · Mock interview</span>'
        "<h1 style='margin-top:6px;font-size:30px;'>Five questions you'll likely hear.</h1>"
        "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 1.6], gap="large")

    with left:
        st.markdown(
            '<div class="pw"><div class="pw-card">'
            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">'
            '<span class="pw-eyebrow" style="margin:0;">Job description</span>'
            '<span class="pw-hint" style="font-size:11.5px;">Lumen · PM, Growth · detected</span>'
            "</div></div></div>",
            unsafe_allow_html=True,
        )
        jd = st.text_area(
            "Paste a job description",
            value=st.session_state.job_description,
            height=380,
            label_visibility="collapsed",
        )
        col_clear, col_sample = st.columns(2)
        with col_clear:
            if st.button("Clear", key="jd_clear"):
                st.session_state.job_description = ""
                st.session_state.outputs.pop("interview", None)
                st.rerun()
        with col_sample:
            if st.button("Use a sample JD", key="jd_sample"):
                st.session_state.job_description = SAMPLE_JD
                st.session_state.outputs.pop("interview", None)
                st.rerun()
        if jd != st.session_state.job_description:
            st.session_state.job_description = jd
            st.session_state.outputs.pop("interview", None)

    with right:
        outputs = st.session_state.outputs
        jd_text = st.session_state.job_description.strip()
        if not jd_text:
            st.markdown(
                '<div class="pw"><div class="pw-card" style="padding:40px;text-align:center;">'
                f"{path_glyph(size=36)}"
                "<h3 style='margin:14px 0 8px;'>Drop in a JD to begin</h3>"
                "<p class='pw-hint' style='max-width:360px;margin:0 auto;'>Once we see the role, we'll draft "
                "five questions and an answer hint for each. No JD on hand? Use a sample.</p>"
                "</div></div>",
                unsafe_allow_html=True,
            )
            return

        if "interview" not in outputs:
            with st.spinner("Generating tailored interview questions…"):
                chains = build_chains(st.session_state.memory)
                resume_md = "\n".join(f"- {b}" for b in outputs.get("resume", []))
                result = chains.interview.invoke(
                    {
                        "audience": profile["persona"],
                        "tone": profile["tone"].lower(),
                        "resume_bullets": resume_md or "(not yet generated)",
                        "job_description": jd_text,
                    }
                )
                questions = [q.model_dump() for q in result.questions]
                outputs["interview"] = questions
                remember(
                    st.session_state.memory,
                    "[step 2] interview prep",
                    "\n".join(f"Q{i+1}: {q['q']}" for i, q in enumerate(questions)),
                )

        questions = outputs["interview"]
        for i, q in enumerate(questions, start=1):
            expanded = i in st.session_state.expanded_qs
            question_card(i, q["q"], q["hint"], q["tags"], expanded)
            tcol_a, tcol_b, _ = st.columns([1.4, 1.4, 4])
            with tcol_a:
                lbl = "Hide hint" if expanded else "Show answer hint"
                if st.button(lbl, key=f"hint_{i}"):
                    if expanded:
                        st.session_state.expanded_qs.discard(i)
                    else:
                        st.session_state.expanded_qs.add(i)
                    st.rerun()
            with tcol_b:
                practiced = i in st.session_state.practiced_qs
                lbl2 = "✓ Practiced" if practiced else "Mark as practiced"
                if st.button(lbl2, key=f"prac_{i}"):
                    if practiced:
                        st.session_state.practiced_qs.discard(i)
                    else:
                        st.session_state.practiced_qs.add(i)
                    st.rerun()

        practiced_count = len(st.session_state.practiced_qs)
        st.markdown(
            f'<div class="pw" style="margin-top:10px;display:flex;justify-content:space-between;align-items:center;">'
            f'<span class="pw-hint">{practiced_count} of {len(questions)} practiced</span>'
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="pw"><hr class="pw-divider"/></div>', unsafe_allow_html=True)
    nav_a, _, nav_c = st.columns([1, 4, 2])
    with nav_a:
        if st.button("← Back", key="back_interview"):
            goto(1)
    with nav_c:
        if st.button("Continue to roadmap →", key="next_interview", type="secondary"):
            goto(3)


def screen_roadmap() -> None:
    top_shell(3, profile["target_role"], make_initials("Sara Lindqvist"))

    st.markdown(
        '<div class="pw">'
        '<span class="pw-eyebrow">Step 3 of 3 · Growth roadmap</span>'
        "<h1 style='margin-top:6px;font-size:30px;'>Six months, one path forward.</h1>"
        "<p class='pw-hint' style='font-size:15px;max-width:620px;'>Three lanes feeding into a monthly "
        "milestone. Lighter on month 1 by design — momentum first.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    outputs = st.session_state.outputs
    if "roadmap" not in outputs:
        with st.spinner("Composing your six-month roadmap…"):
            chains = build_chains(st.session_state.memory)
            interview_md = "\n".join(
                f"Q{i+1}: {q['q']}" for i, q in enumerate(outputs.get("interview", []))
            )
            resume_md = "\n".join(f"- {b}" for b in outputs.get("resume", []))
            result = chains.roadmap.invoke(
                {
                    "audience": profile["persona"],
                    "tone": profile["tone"].lower(),
                    "career_goal": profile["goal"],
                    "skills": ", ".join(profile["skills"]),
                    "resume_bullets": resume_md or "(not yet generated)",
                    "interview_prep": interview_md or "(not yet generated)",
                }
            )
            roadmap = result.model_dump()
            outputs["roadmap"] = roadmap
            remember(
                st.session_state.memory,
                "[step 3] growth roadmap",
                f"{len(roadmap['milestones'])} milestones, {len(roadmap['courses'])} courses",
            )

    rm = outputs["roadmap"]

    lanes_html = (
        '<div class="pw"><div class="pw-lanes">'
        + lane_card_html("Courses & certifications", "courses", rm["courses"])
        + lane_card_html("Networking actions", "networking", rm["networking"])
        + lane_card_html("Portfolio projects", "projects", rm["projects"])
        + "</div></div>"
    )
    st.markdown(lanes_html, unsafe_allow_html=True)

    st.markdown(milestone_path_html(rm["milestones"]), unsafe_allow_html=True)

    st.markdown('<div class="pw"><hr class="pw-divider"/></div>', unsafe_allow_html=True)
    nav_a, _, nav_c = st.columns([1, 4, 2])
    with nav_a:
        if st.button("← Back", key="back_roadmap"):
            goto(2)
    with nav_c:
        if st.button("See your coaching recap →", key="next_roadmap", type="primary"):
            goto(4)


def screen_recap() -> None:
    top_shell(4, profile["target_role"], make_initials("Sara Lindqvist"))

    outputs = st.session_state.outputs
    rm = outputs.get("roadmap")
    bullets = outputs.get("resume", [])
    questions = outputs.get("interview", [])

    aside, main = st.columns([1, 3.5], gap="large")

    with aside:
        toc_html = (
            '<div class="pw"><div class="pw-recap-toc">'
            '<span class="pw-eyebrow">Coaching recap</span>'
            '<h2 style="font-size:22px;margin-top:8px;letter-spacing:-0.02em;">Your session</h2>'
            "<nav>"
            '<a href="#sec-profile"><span class="bullet"></span>Profile</a>'
            '<a href="#sec-resume"><span class="bullet"></span>Resume bullets</a>'
            '<a href="#sec-interview"><span class="bullet"></span>Interview prep</a>'
            '<a href="#sec-roadmap"><span class="bullet"></span>Growth roadmap</a>'
            "</nav>"
            '<hr class="pw-divider" style="margin: 8px 0 12px;"/>'
            '<p class="pw-hint" style="margin:14px 0 0;font-size:12px;">Saved locally. Not shared.<br/>'
            "Re-run any step from the dots above.</p>"
            "</div></div>"
        )
        st.markdown(toc_html, unsafe_allow_html=True)
        if st.button("⤓ Download as PDF", key="pdf_btn", type="primary"):
            st.toast("PDF export not wired up yet — copy/screenshot the recap for now.")
        if st.button("Start a new session", key="recap_new"):
            for k in ("step", "memory", "outputs", "profile", "expanded_qs", "practiced_qs", "job_description"):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        with st.expander("💬 Memory log", expanded=False):
            messages = getattr(st.session_state.memory.chat_memory, "messages", [])
            if not messages:
                st.markdown('<span class="pw-hint">No turns logged yet.</span>', unsafe_allow_html=True)
            for m in messages:
                role = "🧑 You" if m.type == "human" else "🤖 Coach"
                st.markdown(f"**{role}**")
                st.markdown(m.content)
                st.markdown("---")

    with main:
        from datetime import date

        today = date.today().strftime("%-d %B %Y")
        st.markdown(
            '<div class="pw">'
            f'<div class="pw-eyebrow">Coaching recap · {escape(today)}</div>'
            "<h1 style='font-size:40px;letter-spacing:-0.025em;line-height:1.05;'>"
            "A path from where you are<br/>to where you're going."
            "</h1>"
            "<p class='pw-hint' style='font-size:16px;max-width:600px;margin-top:10px;'>Everything we drafted "
            "together. Copy-friendly, screenshot-friendly, and yours to edit.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        # --- Profile
        st.markdown('<div id="sec-profile"></div>', unsafe_allow_html=True)
        kv_html = kv_grid(
            [
                ("Target role", profile["target_role"]),
                ("Persona", profile["persona"]),
                ("Tone", profile["tone"]),
                ("Skills count", str(len(profile["skills"]))),
            ]
        )
        chips_html = chips(profile["skills"])
        goal_html = escape(profile["goal"])
        st.markdown(
            '<div class="pw"><div class="pw-card" style="padding:28px;">'
            '<div class="pw-eyebrow" style="margin-bottom:4px;">01 · Profile</div>'
            "<h3 style='margin:0 0 14px;'>Who you are, where you're heading</h3>"
            f"{kv_html}"
            f"<div style='margin-top:16px;'><span class='pw-eyebrow'>Goal</span>"
            f"<p style='margin:6px 0 0;font-size:15.5px;line-height:1.6;'>{goal_html}</p></div>"
            f"<div style='margin-top:16px;'><span class='pw-eyebrow'>Skills</span>"
            f"<div style='margin-top:6px;'>{chips_html}</div></div>"
            "</div></div>",
            unsafe_allow_html=True,
        )

        # --- Resume
        st.markdown('<div id="sec-resume"></div>', unsafe_allow_html=True)
        if bullets:
            li = "".join(
                f'<li style="display:grid;grid-template-columns:32px 1fr;gap:14px;align-items:flex-start;">'
                f'<span style="font-family:var(--pw-font-mono);font-size:11px;color:var(--pw-sage-deep);'
                f'padding-top:4px;font-weight:500;">{i+1:02d}</span>'
                f'<p style="margin:0;font-size:14.5px;line-height:1.6;">{escape(b)}</p></li>'
                for i, b in enumerate(bullets)
            )
            st.markdown(
                '<div class="pw"><div class="pw-card" style="padding:28px;margin-top:24px;">'
                '<div class="pw-eyebrow" style="margin-bottom:4px;">02 · Resume bullets</div>'
                "<h3 style='margin:0 0 14px;'>Five bullets, ATS-friendly</h3>"
                f"<ol style='margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:14px;'>{li}</ol>"
                "</div></div>",
                unsafe_allow_html=True,
            )

        # --- Interview
        st.markdown('<div id="sec-interview"></div>', unsafe_allow_html=True)
        if questions:
            blocks = "".join(recap_question_block(i + 1, q["q"], q["hint"]) for i, q in enumerate(questions))
            st.markdown(
                '<div class="pw"><div class="pw-card" style="padding:28px;margin-top:24px;">'
                '<div class="pw-eyebrow" style="margin-bottom:4px;">03 · Interview prep</div>'
                "<h3 style='margin:0 0 14px;'>Five questions · with coach hints</h3>"
                f"{blocks}</div></div>",
                unsafe_allow_html=True,
            )

        # --- Roadmap
        st.markdown('<div id="sec-roadmap"></div>', unsafe_allow_html=True)
        if rm:
            lane_titles = {
                "courses": ("Courses", rm["courses"]),
                "networking": ("Networking", rm["networking"]),
                "projects": ("Projects", rm["projects"]),
            }
            lane_cols = "".join(
                f'<div><div class="pw-eyebrow" style="font-size:10.5px;margin-bottom:8px;">{title}</div>'
                "<ul style='margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px;'>"
                + "".join(
                    f'<li style="font-size:12.5px;line-height:1.45;padding-left:12px;position:relative;">'
                    f'<span style="position:absolute;left:0;top:7px;width:4px;height:4px;border-radius:50%;background:var(--pw-sage);"></span>'
                    f"{escape(item['name'])}</li>"
                    for item in items
                )
                + "</ul></div>"
                for title, items in lane_titles.values()
            )
            st.markdown(
                '<div class="pw"><div class="pw-card" style="padding:28px;margin-top:24px;">'
                '<div class="pw-eyebrow" style="margin-bottom:4px;">04 · Growth roadmap</div>'
                "<h3 style='margin:0 0 14px;'>Six months, monthly milestones</h3>"
                f"{milestone_tile_grid(rm['milestones'])}"
                f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">{lane_cols}</div>'
                "</div></div>",
                unsafe_allow_html=True,
            )

        # --- Footer
        st.markdown(
            '<div class="pw" style="padding-top:24px;margin-top:24px;border-top:1px solid var(--pw-ink-08);'
            "display:flex;align-items:center;justify-content:space-between;\">"
            f'<div style="display:flex;align-items:center;gap:10px;">{path_glyph(size=18)}'
            "<span class='pw-hint' style='font-size:12px;'>Pathwise · session 01</span></div>"
            "<span class='pw-hint'>Coaching recaps live for 30 days unless you save them.</span>"
            "</div>",
            unsafe_allow_html=True,
        )


# --- Router -----------------------------------------------------------------


SCREENS = {
    0: screen_welcome,
    1: screen_resume,
    2: screen_interview,
    3: screen_roadmap,
    4: screen_recap,
}


SCREENS[st.session_state.step]()
