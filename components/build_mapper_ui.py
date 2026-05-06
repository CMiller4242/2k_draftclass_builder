"""
UI components for the 2K Labs Build Name Mapping section.
Renders inside the Archetype Library tab as an expandable section.
"""

import streamlit as st
import pandas as pd
from utils.build_mapper import map_all_builds, get_builds_for_archetype, find_excel_path


def render_build_mapper_section(excel_path: str):
    """
    Render the full build-name mapping section.
    Call this inside any tab; it handles its own layout.
    """
    st.markdown("---")
    st.markdown("## 🗂️ 2K Labs Build Name Mapping")
    st.caption(
        "Maps every unique build name from the 2K Labs spreadsheet to one or "
        "more archetype templates via keyword matching.  "
        "A build name can match multiple archetypes — e.g. "
        "**'2-Way 3-Level Cleaner'** maps to Two-Way Wing + 3-Level Scorer + Glass Cleaner."
    )

    with st.spinner("Loading and mapping build names…"):
        results = map_all_builds(excel_path)

    # ── Summary metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Build Names", results["total"])
    with col2:
        st.metric("Mapped", results["mapped_count"],
                  delta=f"{results['mapped_count'] / results['total'] * 100:.1f}%")
    with col3:
        st.metric("Unmapped", results["unmapped_count"],
                  delta=f"-{results['unmapped_count'] / results['total'] * 100:.1f}%",
                  delta_color="inverse")
    with col4:
        avg_archs = (
            sum(len(r["archetypes"]) for r in results["mapped"]) / results["mapped_count"]
            if results["mapped_count"] else 0
        )
        st.metric("Avg Archetypes / Build", f"{avg_archs:.1f}")

    st.markdown("")

    # ── View mode ─────────────────────────────────────────────────────────────
    view_tab1, view_tab2, view_tab3 = st.tabs([
        "🔍 Browse by Archetype",
        "📋 Full Mapping Table",
        "❓ Unmapped Build Names",
    ])

    # --- Tab 1: Browse by archetype ------------------------------------------
    with view_tab1:
        st.markdown(
            "Select an archetype to see every 2K Labs build name that maps to it."
        )
        from data.archetypes import ARCHETYPE_NAMES
        selected_arch = st.selectbox(
            "Archetype", options=ARCHETYPE_NAMES, key="mapper_arch_select"
        )
        arch_builds = get_builds_for_archetype(selected_arch, excel_path)
        st.caption(f"**{len(arch_builds)}** build names map to **{selected_arch}**")

        if arch_builds:
            # Search/filter
            search = st.text_input(
                "Filter build names", placeholder="e.g. Glass, Bully…",
                key="mapper_arch_filter", label_visibility="collapsed"
            )
            filtered = [b for b in arch_builds
                        if not search or search.lower() in b.lower()]
            st.caption(f"Showing {len(filtered)} of {len(arch_builds)}")

            df = pd.DataFrame({"Build Name": filtered})
            st.dataframe(df, use_container_width=True,
                         height=min(400, 35 * len(filtered) + 38))
        else:
            st.info(f"No build names mapped to **{selected_arch}** yet. "
                    "Check KEYWORD_ARCHETYPE_MAP in utils/build_mapper.py to add keywords.")

    # --- Tab 2: Full mapping table -------------------------------------------
    with view_tab2:
        st.markdown(
            "Every mapped build name with its matched archetype(s). "
            "Use the search box to filter."
        )
        search_all = st.text_input(
            "Search build names or archetypes",
            placeholder="e.g. Crasher, Two-Way Wing…",
            key="mapper_full_search", label_visibility="collapsed"
        )

        rows = [
            {
                "Build Name": r["build_name"],
                "Matched Archetypes": ", ".join(r["archetypes"]),
                "# Matches": len(r["archetypes"]),
            }
            for r in results["mapped"]
        ]
        df_all = pd.DataFrame(rows)

        if search_all:
            mask = (
                df_all["Build Name"].str.contains(search_all, case=False, na=False)
                | df_all["Matched Archetypes"].str.contains(search_all, case=False, na=False)
            )
            df_all = df_all[mask]

        st.caption(f"Showing {len(df_all)} of {results['mapped_count']} mapped build names")
        st.dataframe(
            df_all,
            use_container_width=True,
            height=min(500, 35 * len(df_all) + 38),
            column_config={
                "# Matches": st.column_config.NumberColumn(width="small"),
            },
        )

        # Download the mapping as CSV
        csv_bytes = df_all.to_csv(index=False).encode()
        st.download_button(
            "⬇️ Download Full Mapping (CSV)",
            data=csv_bytes,
            file_name="build_name_mapping.csv",
            mime="text/csv",
        )

    # --- Tab 3: Unmapped names -----------------------------------------------
    with view_tab3:
        unmapped = results["unmapped"]
        st.markdown(
            f"**{len(unmapped)}** build names did not match any keyword. "
            "Review these to identify patterns worth adding to "
            "`KEYWORD_ARCHETYPE_MAP` in `utils/build_mapper.py`."
        )

        search_un = st.text_input(
            "Filter unmapped names", placeholder="Search…",
            key="mapper_unmapped_filter", label_visibility="collapsed"
        )
        filtered_un = [n for n in unmapped
                       if not search_un or search_un.lower() in n.lower()]
        st.caption(f"Showing {len(filtered_un)} of {len(unmapped)}")

        if filtered_un:
            df_un = pd.DataFrame({"Unmapped Build Name": filtered_un})
            st.dataframe(df_un, use_container_width=True,
                         height=min(400, 35 * len(filtered_un) + 38))

            csv_un = df_un.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download Unmapped List (CSV)",
                data=csv_un,
                file_name="unmapped_build_names.csv",
                mime="text/csv",
            )
        else:
            st.success("No unmapped names match your filter.")
