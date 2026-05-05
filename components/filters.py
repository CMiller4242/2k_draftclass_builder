"""
Filter sidebar components for the Generated Class Review page.
"""

import streamlit as st
from data.archetypes import ARCHETYPE_NAMES
from data.fields import POSITIONS


def render_class_filters(players: list) -> list:
    """
    Render filter controls and return the filtered player list.
    Filters live in the sidebar or an expander to keep the main view clean.
    """
    with st.expander("🔍 Filter Players", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            tier_options = [1, 2, 3, 4]
            selected_tiers = st.multiselect(
                "Filter by Tier",
                options=tier_options,
                default=tier_options,
                format_func=lambda t: {
                    1: "⭐ Superstar", 2: "🌟 All-Star",
                    3: "💼 Starter", 4: "📋 Role Player"
                }.get(t, str(t)),
            )

        with col2:
            all_archetypes = sorted(set(p["archetype"] for p in players))
            selected_archetypes = st.multiselect(
                "Filter by Archetype",
                options=all_archetypes,
                default=all_archetypes,
            )

        with col3:
            show_busts_only = st.checkbox("Show Busts Only", value=False)
            hide_busts = st.checkbox("Hide Busts", value=False)

    filtered = players

    if selected_tiers:
        filtered = [p for p in filtered if p["tier"] in selected_tiers]

    if selected_archetypes:
        filtered = [p for p in filtered if p["archetype"] in selected_archetypes]

    if show_busts_only:
        filtered = [p for p in filtered if p["is_bust"]]
    elif hide_busts:
        filtered = [p for p in filtered if not p["is_bust"]]

    return filtered
