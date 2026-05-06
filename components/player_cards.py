"""
Player card UI components for Streamlit.
Renders compact player cards and expanded full-detail views.
"""

import streamlit as st
from data.fields import ATTRIBUTE_CATEGORIES, TENDENCY_CATEGORIES, ALL_BADGES
from utils.scouting import generate_scouting_summary, generate_development_notes, generate_2k_entry_notes
from utils.outlook import validate_player_profile


# Tier color map for visual hierarchy
TIER_COLORS = {
    1: "#FFD700",   # Gold — Superstar
    2: "#C0C0C0",   # Silver — All-Star
    3: "#CD7F32",   # Bronze — Starter
    4: "#808080",   # Gray — Role Player
}

TIER_EMOJIS = {
    1: "⭐",
    2: "🌟",
    3: "💼",
    4: "📋",
}

BADGE_LEVEL_COLORS = {
    "Legend":       "#FF4500",
    "Hall of Fame": "#9400D3",
    "Gold":         "#FFD700",
    "Silver":       "#C0C0C0",
    "Bronze":       "#CD7F32",
    "None":         "#2D2D2D",
}


def render_player_card_compact(player: dict, index: int):
    """Render a compact one-line player card for the class overview."""
    tier = player["tier"]
    color = TIER_COLORS.get(tier, "#808080")
    emoji = TIER_EMOJIS.get(tier, "")
    bust_flag = " ⚠️" if player["is_bust"] else ""

    pos_display = player["position"]
    if player.get("secondary_position"):
        pos_display += f"/{player['secondary_position']}"

    with st.container():
        col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 1, 1.5, 2])
        with col1:
            st.markdown(
                f'<span style="color:{color}; font-size:1.2em">{emoji}</span>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<span style="color:white; font-weight:bold">'
                f'#{player["pick_number"]} {player["name"]}{bust_flag}</span>',
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f'<span style="color:#AAAAAA">{pos_display} | {player["height_display"]}</span>',
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f'<span style="color:{color}">{player["tier_label"].split("/")[0]}</span>',
                unsafe_allow_html=True,
            )
        with col5:
            st.markdown(
                f'<span style="color:#AAAAAA; font-size:0.9em">{player["archetype"]}</span>',
                unsafe_allow_html=True,
            )


def render_player_detail(player: dict):
    """Render full player detail view in an expander."""
    tier = player["tier"]
    color = TIER_COLORS.get(tier, "#808080")
    pos_display = player["position"]
    if player.get("secondary_position"):
        pos_display += f"/{player['secondary_position']}"

    # Header
    st.markdown(
        f"""
        <div style="border-left: 4px solid {color}; padding-left: 12px; margin-bottom: 16px;">
            <h2 style="color:{color}; margin:0">#{player['pick_number']} {player['name']}</h2>
            <p style="color:#AAAAAA; margin:4px 0">{pos_display} | {player['height_display']} | {player['weight_lbs']} lbs</p>
            <p style="color:#CCCCCC; margin:0"><strong>Archetype:</strong> {player['archetype']} &nbsp;|&nbsp;
            <strong>Tier:</strong> <span style="color:{color}">{player['tier_label']}</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bust warning banner
    if player["is_bust"]:
        st.warning(
            "⚠️ **BUST RISK** — This prospect has high potential on paper but may "
            "significantly underperform expectations."
        )

    # Profile coherence warnings (dev-mode guard rail; should never fire post-fix)
    for w in validate_player_profile(player):
        st.error(f"⚠️ Profile inconsistency: {w}")

    # Summary cards row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Potential", player["attributes"].get("Potential", "—"))
    with col2:
        st.metric("Projected Role", player["projected_role"].split("/")[0])
    with col3:
        st.metric("Bust Risk", player["bust_risk"].split("—")[0].strip())
    with col4:
        st.metric("Development", player["development_outlook"])

    st.divider()

    # Scouting / Development / Entry Notes
    tab_scout, tab_attrs, tab_tend, tab_badges, tab_entry = st.tabs(
        ["📋 Scouting", "📊 Attributes", "🎯 Tendencies", "🏅 Badges", "🎮 2K Entry Notes"]
    )

    with tab_scout:
        st.markdown("#### Scouting Summary")
        st.write(generate_scouting_summary(player))
        st.markdown("#### Development Outlook")
        st.write(generate_development_notes(player))

    with tab_attrs:
        _render_attributes(player["attributes"])

    with tab_tend:
        _render_tendencies(player["tendencies"])

    with tab_badges:
        _render_badges(player["badges"])

    with tab_entry:
        st.markdown("#### Suggested 2K Entry Notes")
        st.code(generate_2k_entry_notes(player), language=None)
        st.info(
            "Use these notes as a reference when manually creating this player "
            "in 2K's Create-a-Player system."
        )


def _render_attributes(attributes: dict):
    """Render attributes grouped by category with progress bars."""
    from data.fields import ATTRIBUTE_CATEGORIES

    for category, fields in ATTRIBUTE_CATEGORIES.items():
        relevant = {f: attributes[f] for f in fields if f in attributes}
        if not relevant:
            continue

        st.markdown(f"**{category}**")
        cols = st.columns(2)
        for i, (attr, val) in enumerate(relevant.items()):
            with cols[i % 2]:
                color = _attr_color(val)
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; margin-bottom:4px">'
                    f'<span style="color:#CCCCCC; font-size:0.85em">{attr}</span>'
                    f'<span style="color:{color}; font-weight:bold; font-size:0.85em">{val}</span>'
                    f'</div>'
                    f'<div style="background:#2D2D2D; border-radius:3px; height:6px; margin-bottom:8px">'
                    f'<div style="background:{color}; width:{val}%; height:6px; border-radius:3px"></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("")


def _render_tendencies(tendencies: dict):
    """Render tendencies grouped by category."""
    from data.fields import TENDENCY_CATEGORIES

    for category, fields in TENDENCY_CATEGORIES.items():
        relevant = {f: tendencies[f] for f in fields if f in tendencies}
        if not relevant:
            continue

        st.markdown(f"**{category}**")
        cols = st.columns(3)
        for i, (tend, val) in enumerate(relevant.items()):
            with cols[i % 3]:
                color = _tendency_color(val)
                st.markdown(
                    f'<span style="color:#AAAAAA; font-size:0.8em">{tend}</span> '
                    f'<span style="color:{color}; font-weight:bold">{val}</span>',
                    unsafe_allow_html=True,
                )
        st.markdown("")


def _render_badges(badges: dict):
    """Render badges grouped by category with color-coded levels."""
    from data.fields import ALL_BADGES

    for category, badge_list in ALL_BADGES.items():
        relevant = {b: badges.get(b, "None") for b in badge_list}
        non_none = {b: l for b, l in relevant.items() if l != "None"}

        if not non_none:
            continue

        st.markdown(f"**{category}**")
        cols = st.columns(3)
        for i, (badge, level) in enumerate(non_none.items()):
            color = BADGE_LEVEL_COLORS.get(level, "#808080")
            with cols[i % 3]:
                st.markdown(
                    f'<span style="color:{color}; font-size:0.85em">■ {badge}: '
                    f'<strong>{level}</strong></span>',
                    unsafe_allow_html=True,
                )
        st.markdown("")


def _attr_color(val: int) -> str:
    """Color code an attribute value."""
    if val >= 85:
        return "#00C851"
    elif val >= 75:
        return "#FFBB33"
    elif val >= 60:
        return "#FF8800"
    else:
        return "#FF4444"


def _tendency_color(val: int) -> str:
    """Color code a tendency value."""
    if val >= 75:
        return "#00C851"
    elif val >= 50:
        return "#FFBB33"
    else:
        return "#AAAAAA"
