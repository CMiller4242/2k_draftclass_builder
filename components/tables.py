"""
Table rendering components for class overview and attribute comparison.
"""

import streamlit as st
import pandas as pd
from components.player_cards import TIER_COLORS


def render_class_summary_table(players: list):
    """Render a sortable DataFrame of the full draft class."""
    if not players:
        return

    rows = []
    for p in players:
        attrs = p.get("attributes", {})
        rows.append({
            "Pick": p["pick_number"],
            "Name": p["name"],
            "Pos": p["position"],
            "Height": p["height_display"],
            "Wt": p["weight_lbs"],
            "Archetype": p["archetype"],
            "Tier": p["tier"],
            "Tier Label": p["tier_label"].split(" /")[0],
            "Potential": attrs.get("Potential", 0),
            "Bust?": "⚠️" if p["is_bust"] else "",
            "Role": p["projected_role"],
        })

    df = pd.DataFrame(rows)
    df = df.set_index("Pick")

    # Color rows by tier
    def color_tier(val):
        colors = {1: "#3D2E00", 2: "#2E2E3D", 3: "#1E2E1E", 4: "#2D2D2D"}
        return f"background-color: {colors.get(val, '#1A1A1A')}"

    st.dataframe(
        df,
        use_container_width=True,
        height=min(600, 35 * len(rows) + 40),
        column_config={
            "Tier": st.column_config.NumberColumn("Tier", width="small"),
            "Potential": st.column_config.ProgressColumn(
                "Potential", min_value=0, max_value=99, format="%d"
            ),
        },
    )


def render_tier_breakdown_chart(summary: dict):
    """Display tier breakdown as metrics."""
    tier_breakdown = summary.get("tier_breakdown", {})
    total = summary.get("total_players", 0)

    labels = {
        1: "⭐ Superstar",
        2: "🌟 All-Star",
        3: "💼 Starter",
        4: "📋 Role Player",
    }

    cols = st.columns(4)
    for i, tier in enumerate([1, 2, 3, 4]):
        count = tier_breakdown.get(tier, 0)
        pct = round(count / total * 100, 1) if total > 0 else 0
        with cols[i]:
            st.metric(labels[tier], count, f"{pct}%")


def render_diversity_stats(summary: dict):
    """Display archetype diversity metrics inline."""
    unique   = summary.get("unique_archetypes", 0)
    total    = summary.get("total_players", 0)
    score    = summary.get("diversity_score", 0.0)
    most_rep = summary.get("most_repeated_archetype", "—")
    most_ct  = summary.get("most_repeated_count", 0)

    score_pct = f"{score * 100:.0f}%"
    available = 18   # total archetypes in the system

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Archetypes", f"{unique} / {available}")
    with col2:
        st.metric("Diversity Score", score_pct,
                  help="unique archetypes ÷ total players (max 100%)")
    with col3:
        st.metric("Most Repeated", most_rep,
                  delta=f"{most_ct}×" if most_ct > 1 else "1× (no repeats)",
                  delta_color="off")


def render_archetype_distribution(summary: dict):
    """Display archetype distribution as a bar chart."""
    arch_dist = summary.get("archetype_distribution", {})
    if not arch_dist:
        return

    df = pd.DataFrame(
        list(arch_dist.items()), columns=["Archetype", "Count"]
    ).sort_values("Count", ascending=False)

    st.bar_chart(df.set_index("Archetype"))


def render_position_distribution(summary: dict):
    """Display position distribution."""
    pos_dist = summary.get("position_distribution", {})
    if not pos_dist:
        return

    df = pd.DataFrame(
        list(pos_dist.items()), columns=["Position", "Count"]
    ).sort_values("Count", ascending=False)

    st.bar_chart(df.set_index("Position"))
