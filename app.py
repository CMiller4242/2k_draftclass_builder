"""
2K Draft Class Builder — Main Streamlit Application

Tabs:
  1. Dashboard       — overview, instructions, quick stats
  2. Draft Class     — generate a full draft class
  3. Player Builder  — generate a single custom player
  4. Archetype Library — browse all archetypes
  5. Class Review    — explore the generated class
  6. Export Center   — download JSON / CSV
"""

import streamlit as st
import random

# ── Page config must be first ────────────────────────────────────────────────
st.set_page_config(
    page_title="2K Draft Class Builder",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom dark theme overrides ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Dark background */
    .stApp { background-color: #0E1117; color: #FAFAFA; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1A2E;
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
        color: #AAAAAA;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E94560 !important;
        color: white !important;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1A1A2E;
        border-radius: 8px;
        padding: 12px;
    }

    /* Expanders */
    .streamlit-expanderHeader { background-color: #1A1A2E; }

    /* Buttons */
    .stButton > button {
        background-color: #E94560;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton > button:hover { background-color: #C73652; }

    /* Info boxes */
    .stAlert { border-radius: 8px; }

    /* Dividers */
    hr { border-color: #2D2D2D; }

    /* Selectbox / slider labels */
    label { color: #CCCCCC !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Imports (after page config) ───────────────────────────────────────────────
from data.archetypes import ARCHETYPES, ARCHETYPE_NAMES
from data.class_rules import (
    CLASS_TYPES, CLASS_TYPE_NAMES, CLASS_FLAVORS, CLASS_FLAVOR_NAMES,
    TIER_LABELS,
)
from data.fields import ATTRIBUTE_CATEGORIES, TENDENCY_CATEGORIES, ALL_BADGES
from utils.generate_class import generate_draft_class, get_class_summary
from utils.generate_player import generate_player
from utils.scouting import (
    generate_scouting_summary, generate_development_notes, generate_2k_entry_notes,
)
from utils.export_utils import players_to_json, players_to_csv
from utils.scaling import scale_tier_distribution
from components.player_cards import (
    render_player_card_compact, render_player_detail, TIER_COLORS,
)
from components.tables import (
    render_class_summary_table, render_tier_breakdown_chart,
    render_archetype_distribution, render_position_distribution,
    render_diversity_stats, render_sleeper_summary,
)
from components.filters import render_class_filters
from components.build_mapper_ui import render_build_mapper_section
from utils.build_mapper import find_excel_path

# ── Session state initialisation ─────────────────────────────────────────────
if "draft_class" not in st.session_state:
    st.session_state.draft_class = []
if "class_summary" not in st.session_state:
    st.session_state.class_summary = {}
if "single_player" not in st.session_state:
    st.session_state.single_player = None
if "last_class_config" not in st.session_state:
    st.session_state.last_class_config = {}

# ── Main Tabs ─────────────────────────────────────────────────────────────────
def _ht(inches: int) -> str:
    """Convert integer inches to feet'inches\" display string."""
    return f"{inches // 12}'{inches % 12}\""


tab_dash, tab_gen, tab_builder, tab_arch, tab_review, tab_export = st.tabs([
    "🏠 Dashboard",
    "🎲 Draft Class Generator",
    "🔧 Player Builder",
    "📚 Archetype Library",
    "📋 Class Review",
    "📦 Export Center",
])

# =============================================================================
# TAB 1 — DASHBOARD
# =============================================================================
with tab_dash:
    st.markdown(
        """
        <div style="text-align:center; padding: 30px 0 10px 0">
            <h1 style="color:#E94560; font-size:3em; margin:0">🏀 2K Draft Class Builder</h1>
            <p style="color:#AAAAAA; font-size:1.2em; margin-top:8px">
                Generate realistic NBA 2K draft class profiles for MyNBA / MyEras
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Quick stats if a class exists
    if st.session_state.draft_class:
        summary = st.session_state.class_summary
        config = st.session_state.last_class_config
        st.markdown("### Current Draft Class")
        st.caption(
            f"**{config.get('class_type', '—')}** class · "
            f"{config.get('class_flavor', '—')} flavor · "
            f"{summary.get('total_players', 0)} players"
        )
        render_tier_breakdown_chart(summary)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Avg Potential", summary.get("avg_potential", 0))
        with col_b:
            st.metric("Bust Count", summary.get("bust_count", 0))
        with col_c:
            st.metric("Bust %", f"{summary.get('bust_percentage', 0)}%")
        st.info("Go to **Class Review** to explore players, or **Export Center** to download.")
    else:
        # Getting started guide
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                """
                <div style="background:#1A1A2E; border-radius:10px; padding:20px; text-align:center">
                    <div style="font-size:2em">🎲</div>
                    <h3 style="color:#E94560">1. Generate</h3>
                    <p style="color:#AAAAAA">Go to <strong>Draft Class Generator</strong>,
                    pick a class type and flavor, then hit Generate.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                """
                <div style="background:#1A1A2E; border-radius:10px; padding:20px; text-align:center">
                    <div style="font-size:2em">📋</div>
                    <h3 style="color:#E94560">2. Review</h3>
                    <p style="color:#AAAAAA">Browse your class in <strong>Class Review</strong>.
                    Click any player to see full attributes, badges, and scouting notes.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                """
                <div style="background:#1A1A2E; border-radius:10px; padding:20px; text-align:center">
                    <div style="font-size:2em">🎮</div>
                    <h3 style="color:#E94560">3. Enter in 2K</h3>
                    <p style="color:#AAAAAA">Use the <strong>2K Entry Notes</strong> on each player
                    to manually create them in Create-a-Player.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # App info
    with st.expander("ℹ️ About This App"):
        st.markdown(
            """
            **2K Draft Class Builder** is a companion tool for NBA 2K MyNBA / MyEras modes.

            It does **NOT** integrate directly with 2K — it generates complete, realistic
            player profiles that you manually enter into 2K's Create-a-Player system.

            **What gets generated:**
            - Full attribute sets (60+ attributes across 6 categories)
            - Complete tendency profiles (90+ tendencies)
            - Badge assignments with levels (Bronze → Legend)
            - Scouting summaries, development outlooks, and bust risk assessments
            - Position, height, weight, and archetype

            **How tier distribution works:**
            - Class strength (Generational → Weak) controls the overall quality curve
            - Player count scales the distribution proportionally
            - A single player in a Generational class will almost always be Tier 1
            - Natural randomness ensures no two classes are identical
            """
        )

# =============================================================================
# TAB 2 — DRAFT CLASS GENERATOR
# =============================================================================
with tab_gen:
    st.markdown("## 🎲 Draft Class Generator")
    st.caption("Configure your class and generate up to 60 players at once.")

    # ── Configuration Form ────────────────────────────────────────────────────
    with st.form("class_gen_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            class_type = st.selectbox(
                "Class Type",
                options=CLASS_TYPE_NAMES,
                index=CLASS_TYPE_NAMES.index("Average"),
                help="Controls the overall talent level of the class.",
            )
            # Show description
            type_desc = CLASS_TYPES[class_type]["description"]
            st.caption(type_desc)

        with col2:
            class_flavor = st.selectbox(
                "Class Flavor",
                options=CLASS_FLAVOR_NAMES,
                index=CLASS_FLAVOR_NAMES.index("Balanced"),
                help="Biases what types of players populate the class.",
            )
            flavor_desc = CLASS_FLAVORS[class_flavor]["description"]
            st.caption(flavor_desc)

        with col3:
            player_count = st.number_input(
                "Number of Players",
                min_value=1,
                max_value=60,
                value=30,
                step=1,
                help="How many players to generate (1–60).",
            )

        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            use_seed = st.checkbox("Use fixed random seed (for reproducibility)", value=False)
            seed_value = st.number_input("Seed value", value=42, disabled=not use_seed)

        submitted = st.form_submit_button("🎲 Generate Draft Class", use_container_width=True)

    # ── Generation ────────────────────────────────────────────────────────────
    if submitted:
        seed = int(seed_value) if use_seed else None
        with st.spinner(f"Generating {player_count} players..."):
            players = generate_draft_class(
                class_type=class_type,
                player_count=int(player_count),
                class_flavor=class_flavor,
                seed=seed,
            )
            summary = get_class_summary(players)

        st.session_state.draft_class = players
        st.session_state.class_summary = summary
        st.session_state.last_class_config = {
            "class_type": class_type,
            "class_flavor": class_flavor,
            "player_count": int(player_count),
        }
        st.success(
            f"✅ Generated **{len(players)} players** — "
            f"{summary['tier_breakdown'].get(1, 0)} Superstars, "
            f"{summary['tier_breakdown'].get(2, 0)} All-Stars, "
            f"{summary['tier_breakdown'].get(3, 0)} Starters, "
            f"{summary['tier_breakdown'].get(4, 0)} Role Players"
        )
        st.info("Go to the **Class Review** tab to explore your players.")

    # ── Tier preview ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🔍 Tier Distribution Preview")
    st.caption("See what kind of distribution you'd expect before generating.")

    prev_col1, prev_col2, prev_col3 = st.columns(3)
    with prev_col1:
        preview_type = st.selectbox("Preview Class Type", CLASS_TYPE_NAMES, key="prev_type")
    with prev_col2:
        preview_count = st.number_input(
            "Preview Player Count", min_value=1, max_value=60, value=30, key="prev_count"
        )
    with prev_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Preview Distribution"):
            preview_dist = scale_tier_distribution(preview_type, int(preview_count))
            total = sum(preview_dist.values())
            cols = st.columns(4)
            tier_labels = {1: "⭐ Superstar", 2: "🌟 All-Star", 3: "💼 Starter", 4: "📋 Role Player"}
            for i, tier in enumerate([1, 2, 3, 4]):
                count = preview_dist.get(tier, 0)
                pct = round(count / total * 100, 1) if total else 0
                with cols[i]:
                    st.metric(tier_labels[tier], count, f"{pct}%")

# =============================================================================
# TAB 3 — PLAYER BUILDER
# =============================================================================
with tab_builder:
    st.markdown("## 🔧 Single Player Builder")
    st.caption("Generate one custom player with full control over archetype and tier.")

    with st.form("player_builder_form"):
        col1, col2 = st.columns(2)

        with col1:
            pb_archetype = st.selectbox("Archetype", options=ARCHETYPE_NAMES)
            arch_info = ARCHETYPES[pb_archetype]
            st.caption(arch_info["description"])
            st.caption(f"Positions: {', '.join(arch_info['valid_positions'])}")

        with col2:
            pb_tier = st.select_slider(
                "Player Tier",
                options=[1, 2, 3, 4],
                value=2,
                format_func=lambda t: f"Tier {t} — {TIER_LABELS[t]}",
            )
            pb_bust = st.checkbox("Force Bust (underperforming prospect)", value=False)

        pb_submitted = st.form_submit_button("🔧 Build Player", use_container_width=True)

    if pb_submitted:
        with st.spinner("Building player..."):
            player = generate_player(
                tier=pb_tier,
                archetype_name=pb_archetype,
                bust_modifier=1.0 if pb_bust else 0.0,
                player_number=0,
            )
            # Give pick number 0 a cleaner display
            player["pick_number"] = "—"
            st.session_state.single_player = player

    if st.session_state.single_player:
        st.divider()
        st.markdown("### Generated Player")
        render_player_detail(st.session_state.single_player)

        st.divider()
        # Quick export for single player
        col_j, col_c = st.columns(2)
        with col_j:
            st.download_button(
                "⬇️ Download JSON",
                data=players_to_json([st.session_state.single_player]),
                file_name="player.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_c:
            st.download_button(
                "⬇️ Download CSV",
                data=players_to_csv([st.session_state.single_player]),
                file_name="player.csv",
                mime="text/csv",
                use_container_width=True,
            )

# =============================================================================
# TAB 4 — ARCHETYPE LIBRARY
# =============================================================================
with tab_arch:
    st.markdown("## 📚 Archetype Library")
    st.caption("Browse all available archetypes, their descriptions, and priority attributes.")

    for arch_name, arch_data in ARCHETYPES.items():
        with st.expander(f"**{arch_name}**", expanded=False):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"*{arch_data['description']}*")
                h_lo = _ht(arch_data['height_range_inches'][0])
                h_hi = _ht(arch_data['height_range_inches'][1])
                st.markdown(
                    f"**Positions:** {', '.join(arch_data['valid_positions'])}  \n"
                    f"**Height:** {h_lo} – {h_hi}  \n"
                    f"**Weight:** {arch_data['weight_range_lbs'][0]} – "
                    f"{arch_data['weight_range_lbs'][1]} lbs"
                )

            with col2:
                st.markdown("**Priority Attributes (Tier 3 baseline)**")
                priorities = arch_data.get("attribute_priorities", {})
                for attr, rng in list(priorities.items())[:8]:
                    st.markdown(
                        f'<span style="color:#AAAAAA; font-size:0.85em">{attr}: '
                        f'<span style="color:#FFBB33">{rng[0]}–{rng[1]}</span></span>',
                        unsafe_allow_html=True,
                    )

            st.markdown("**Badge Priorities**")
            badge_prio = arch_data.get("badge_priorities", {})
            for cat, badge_list in badge_prio.items():
                st.markdown(
                    f'<span style="color:#E94560">{cat}:</span> '
                    f'<span style="color:#CCCCCC">{", ".join(badge_list[:5])}</span>',
                    unsafe_allow_html=True,
                )

            # Show build name keywords if defined on this archetype
            kw = arch_data.get("build_name_keywords")
            if kw:
                st.markdown(
                    f'<span style="color:#888888; font-size:0.82em">🔑 Build name keywords: '
                    f'{", ".join(kw)}</span>',
                    unsafe_allow_html=True,
                )

    # ── 2K Labs Build Name Mapping ───────────────────────────────────────────
    _excel_path = find_excel_path()
    if _excel_path:
        render_build_mapper_section(_excel_path)
    else:
        st.divider()
        st.warning(
            f"⚠️ Build name mapping requires **Archs for Build.xlsx** in the project root. "
            f"File not found."
        )


# =============================================================================
# TAB 5 — CLASS REVIEW
# =============================================================================
with tab_review:
    st.markdown("## 📋 Generated Class Review")

    if not st.session_state.draft_class:
        st.info("No draft class generated yet. Go to **Draft Class Generator** to create one.")
    else:
        players = st.session_state.draft_class
        summary = st.session_state.class_summary
        config = st.session_state.last_class_config

        # Class header
        st.markdown(
            f"### {config.get('class_type', '')} Draft Class "
            f"— {config.get('class_flavor', '')} Flavor"
        )

        # Summary metrics
        render_tier_breakdown_chart(summary)

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Total Players", summary["total_players"])
        with col_b:
            st.metric("Avg Potential", summary["avg_potential"])
        with col_c:
            st.metric("Busts", summary["bust_count"])
        with col_d:
            st.metric("Bust Rate", f"{summary['bust_percentage']}%")

        # Archetype diversity
        st.markdown("**Archetype Diversity**")
        render_diversity_stats(summary)

        # Sleeper prospects
        st.markdown("**Sleeper Prospects**")
        render_sleeper_summary(summary)

        # Distribution charts
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Archetype Distribution**")
            render_archetype_distribution(summary)
        with chart_col2:
            st.markdown("**Position Distribution**")
            render_position_distribution(summary)

        st.divider()

        # Filters
        filtered_players = render_class_filters(players)
        st.caption(f"Showing {len(filtered_players)} of {len(players)} players")

        # View toggle
        view_mode = st.radio(
            "View Mode", ["Card List", "Full Table"], horizontal=True, label_visibility="collapsed"
        )

        if view_mode == "Full Table":
            render_class_summary_table(filtered_players)
        else:
            # Card list with expandable detail
            for player in filtered_players:
                tier = player["tier"]
                color = TIER_COLORS.get(tier, "#808080")
                pos_display = player["position"]
                if player.get("secondary_position"):
                    pos_display += f"/{player['secondary_position']}"

                bust_flag = " ⚠️ BUST RISK" if player["is_bust"] else ""
                label = (
                    f"#{player['pick_number']} {player['name']} — "
                    f"{pos_display} | {player['archetype']} | "
                    f"Tier {tier}: {player['tier_label'].split('/')[0].strip()}"
                    f"{bust_flag}"
                )
                with st.expander(label, expanded=False):
                    render_player_detail(player)

# =============================================================================
# TAB 6 — EXPORT CENTER
# =============================================================================
with tab_export:
    st.markdown("## 📦 Export Center")

    if not st.session_state.draft_class:
        st.info("Generate a draft class first to enable exports.")
    else:
        players = st.session_state.draft_class
        summary = st.session_state.class_summary
        config = st.session_state.last_class_config
        class_name = (
            f"{config.get('class_type', 'draft')}_class_"
            f"{config.get('player_count', len(players))}players"
        ).replace(" ", "_").lower()

        st.markdown("### Full Draft Class Export")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**JSON Export**")
            st.caption("Full player data including all attributes, tendencies, and badges.")
            st.download_button(
                "⬇️ Download Full Class (JSON)",
                data=players_to_json(players),
                file_name=f"{class_name}.json",
                mime="application/json",
                use_container_width=True,
            )

        with col2:
            st.markdown("**CSV Export**")
            st.caption(
                "Flat CSV with one row per player. All attributes and tendencies "
                "become columns. Good for spreadsheets."
            )
            st.download_button(
                "⬇️ Download Full Class (CSV)",
                data=players_to_csv(players),
                file_name=f"{class_name}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.divider()

        # Individual player export
        st.markdown("### Individual Player Export")
        player_options = {
            f"#{p['pick_number']} {p['name']}": p for p in players
        }
        selected_name = st.selectbox("Select Player", options=list(player_options.keys()))
        selected_player = player_options[selected_name]

        col3, col4 = st.columns(2)
        safe_name = selected_player["name"].replace(" ", "_").lower()
        with col3:
            st.download_button(
                f"⬇️ Download {selected_player['name']} (JSON)",
                data=players_to_json([selected_player]),
                file_name=f"{safe_name}.json",
                mime="application/json",
                use_container_width=True,
            )
        with col4:
            st.download_button(
                f"⬇️ Download {selected_player['name']} (CSV)",
                data=players_to_csv([selected_player]),
                file_name=f"{safe_name}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.divider()

        # Summary export
        st.markdown("### Class Summary Export")
        import json
        summary_export = {
            "config": config,
            "summary": {
                k: v for k, v in summary.items() if k != "top_picks"
            },
        }
        st.download_button(
            "⬇️ Download Class Summary (JSON)",
            data=json.dumps(summary_export, indent=2),
            file_name=f"{class_name}_summary.json",
            mime="application/json",
        )

        # PDF placeholder
        st.divider()
        st.markdown("### PDF Export")
        st.info(
            "📄 PDF export is planned for a future release. "
            "It will use ReportLab to generate printable scouting reports. "
            "For now, use JSON or CSV exports."
        )
