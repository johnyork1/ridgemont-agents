import streamlit as st
import pandas as pd
import json
from pathlib import Path

# ============================================================================
# DATA ACCESS - Reads from local data folder
# ============================================================================
DATA_DIR = Path(__file__).parent / "data"

# Act configuration — add new acts here as they grow
ACTS = {
    "FROZEN_CLOUD": {
        "name": "Frozen Cloud Music",
        "icon": "❄️",
        "publisher": "Frozen Cloud Music",
        "default_artist": "Frozen Cloud",
    },
    "PARK_BELLEVUE": {
        "name": "Park Bellevue Collective",
        "icon": "🏛️",
        "publisher": "Park Bellevue Collective",
        "default_artist": "Park Bellevue",
    },
    "BAJAN_SUN": {
        "name": "Bajan Sun Publishing",
        "icon": "☀️",
        "publisher": "Bajan Sun Publishing",
        "default_artist": "Bajan Sun",
    },
}

def load_catalog(act_id=None):
    """Load catalog, optionally filtered to a specific act."""
    catalog_path = DATA_DIR / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path, 'r') as f:
            full_catalog = json.load(f)
            songs = full_catalog.get("songs", [])
            if act_id and act_id != "ALL":
                songs = [s for s in songs if s.get("act_id") == act_id]
            return songs
    return []

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(page_title="Ridgemont Catalog Portal", page_icon="🎵", layout="wide")

# Logo (use Frozen Cloud logo if available, otherwise text)
logo_path = Path(__file__).parent / "logo.gif"
col_logo, col_title = st.columns([0.5, 5])
with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), width=80)
with col_title:
    st.markdown("<h1 style='margin-top: 10px;'>Ridgemont Catalog Portal</h1>", unsafe_allow_html=True)
st.caption("Publishing Catalog Portal • Read-Only")

# ============================================================================
# ACT SELECTOR (Sidebar)
# ============================================================================
act_options = {"All Acts": "ALL"}
for act_id, act_info in ACTS.items():
    act_options[f"{act_info['icon']} {act_info['name']}"] = act_id

selected_label = st.sidebar.selectbox("Select Act", list(act_options.keys()))
selected_act = act_options[selected_label]

# Load songs for selected act
songs = load_catalog(selected_act)

# Display act info
if selected_act != "ALL" and selected_act in ACTS:
    act = ACTS[selected_act]
    st.sidebar.markdown(f"**{act['icon']} {act['name']}**")
    st.sidebar.caption(f"Publisher: {act['publisher']}")
    st.sidebar.caption(f"{len(songs)} songs")
else:
    st.sidebar.caption(f"Showing all acts • {len(songs)} songs")

st.sidebar.markdown("---")

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Dashboard", "All Songs", "Deployment Status", "Financials"])

# ============================================================================
# DASHBOARD
# ============================================================================
if page == "Dashboard":
    st.header("Catalog Overview")

    # Metrics
    total_songs = len(songs)
    released_songs = sum(1 for s in songs if s.get('status') == 'released')
    mastered_songs = sum(1 for s in songs if s.get('status') == 'mastered')
    total_revenue = sum(s.get('revenue', {}).get('total_earned', 0) for s in songs)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Songs", total_songs)
    col2.metric("Released", released_songs)
    col3.metric("Mastered", mastered_songs)
    col4.metric("Total Revenue", f"${total_revenue:,.2f}")

    st.markdown("---")

    # Status Breakdown
    st.subheader("Status Breakdown")
    status_counts = {}
    for s in songs:
        status = s.get('status', 'unknown').title()
        status_counts[status] = status_counts.get(status, 0) + 1

    if status_counts:
        cols = st.columns(min(len(status_counts), 6))
        for i, (status, count) in enumerate(sorted(status_counts.items())):
            cols[i % len(cols)].metric(status, count)

    st.markdown("---")

    # Recent Songs
    st.subheader("Recent Songs")
    if songs:
        recent = songs[-10:]
        table_data = []
        for s in recent:
            row = {
                "Title": s['title'],
                "Artist": s.get('artist', '-'),
                "Status": s.get('status', '-').title(),
            }
            if selected_act == "ALL":
                row["Act"] = ACTS.get(s.get('act_id', ''), {}).get('name', s.get('act_id', '-'))
            table_data.append(row)
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
    else:
        st.info("No songs in catalog yet.")

# ============================================================================
# ALL SONGS
# ============================================================================
elif page == "All Songs":
    st.header("Complete Catalog")

    if songs:
        # Filters
        artist_options = ["All"] + sorted(set(s.get('artist', '') for s in songs if s.get('artist')))

        col1, col2, col3 = st.columns(3)
        with col1:
            artist_filter = st.selectbox("Filter by Artist or Group", artist_options)
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "idea", "demo", "mixing", "mastered", "copyright", "released"])
        with col3:
            search = st.text_input("Search by Title or Code")

        # Apply filters
        filtered = songs
        if artist_filter != "All":
            filtered = [s for s in filtered if s.get('artist') == artist_filter]
        if status_filter != "All":
            filtered = [s for s in filtered if s.get('status') == status_filter]
        if search:
            search_lower = search.lower()
            filtered = [s for s in filtered if search_lower in s.get('title', '').lower() or search_lower in s.get('legacy_code', '').lower()]

        st.write(f"**Showing {len(filtered)} of {len(songs)} songs**")

        # Display columns
        if status_filter == "copyright":
            display_cols = ['song_id', 'legacy_code', 'title', 'artist', 'copyright_number']
            col_names = ['Song ID', 'Code', 'Title', 'Artist', 'Copyright #']
        else:
            display_cols = ['song_id', 'legacy_code', 'title', 'artist', 'status']
            col_names = ['Song ID', 'Code', 'Title', 'Artist', 'Status']

        # Add Act column when showing all acts
        if selected_act == "ALL":
            for s in filtered:
                s['_act_name'] = ACTS.get(s.get('act_id', ''), {}).get('name', s.get('act_id', '-'))
            display_cols.insert(0, '_act_name')
            col_names.insert(0, 'Act')

        df = pd.DataFrame(filtered)
        available_cols = [c for c in display_cols if c in df.columns]
        display_df = df[available_cols]
        col_labels = [col_names[display_cols.index(c)] for c in available_cols]
        display_df.columns = col_labels
        st.dataframe(display_df, use_container_width=True, height=500)
    else:
        st.info("No songs match filters")

# ============================================================================
# DEPLOYMENT STATUS
# ============================================================================
elif page == "Deployment Status":
    st.header("Deployment Status")
    st.caption("View where songs are distributed and streaming")

    if not songs:
        st.info("No songs in catalog yet.")
    else:
        ALL_DISTRIBUTORS = ["DistroKid", "TuneCore", "CD Baby", "Amuse", "AWAL", "Ditto"]
        ALL_SYNC_LIBS = ["Songtradr", "Music Gateway", "Pond5", "Disco", "Taxi", "Musicbed", "Artlist"]
        ALL_STREAMING = ["Spotify", "Apple Music", "Amazon", "YouTube", "Tidal", "Deezer", "Pandora"]

        # Summary metrics
        songs_with_distribution = sum(1 for s in songs if s.get('deployments', {}).get('distribution'))
        songs_with_sync = sum(1 for s in songs if s.get('deployments', {}).get('sync_libraries'))
        songs_with_streaming = sum(1 for s in songs if s.get('deployments', {}).get('streaming'))

        col1, col2, col3 = st.columns(3)
        col1.metric("On Distributors", songs_with_distribution)
        col2.metric("On Sync Libraries", songs_with_sync)
        col3.metric("On Streaming", songs_with_streaming)

        st.markdown("---")

        # Deployment table
        st.subheader("All Songs - Deployment Details")

        table_data = []
        for s in songs:
            deps = s.get('deployments', {})
            dist_list = deps.get('distribution', [])
            sync_list = deps.get('sync_libraries', [])
            stream_list = deps.get('streaming', [])

            def format_with_checks(platforms):
                if not platforms:
                    return "—"
                return " ".join([f"✅ {p}" for p in platforms])

            row = {
                "Title": s['title'],
                "Status": s.get('status', '-').title(),
                "Distribution": format_with_checks(dist_list),
                "Sync Libraries": format_with_checks(sync_list),
                "Streaming": format_with_checks(stream_list),
            }
            if selected_act == "ALL":
                row["Act"] = ACTS.get(s.get('act_id', ''), {}).get('name', '-')
            table_data.append(row)

        st.dataframe(pd.DataFrame(table_data), use_container_width=True, height=400)

        # Platform Coverage
        st.markdown("---")
        st.subheader("Platform Coverage")

        platform_counts = {}
        for s in songs:
            deps = s.get('deployments', {})
            all_plats = deps.get('distribution', []) + deps.get('sync_libraries', []) + deps.get('streaming', [])
            for p in all_plats:
                platform_counts[p] = platform_counts.get(p, 0) + 1

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Distribution**")
            for p in ALL_DISTRIBUTORS:
                count = platform_counts.get(p, 0)
                if count > 0:
                    st.write(f"✅ {p}: {count} songs")

        with col2:
            st.markdown("**Sync Libraries**")
            for p in ALL_SYNC_LIBS:
                count = platform_counts.get(p, 0)
                if count > 0:
                    st.write(f"✅ {p}: {count} songs")

        with col3:
            st.markdown("**Streaming**")
            for p in ALL_STREAMING:
                count = platform_counts.get(p, 0)
                if count > 0:
                    st.write(f"✅ {p}: {count} songs")

        if not platform_counts:
            st.info("No deployment data yet. Songs will appear here once deployed to platforms.")

# ============================================================================
# FINANCIALS
# ============================================================================
elif page == "Financials":
    st.header("Revenue Summary")

    total_revenue = sum(s.get('revenue', {}).get('total_earned', 0) for s in songs)
    total_expenses = sum(
        sum(e.get('amount', 0) for e in s.get('revenue', {}).get('expenses', []))
        for s in songs
    )
    net_revenue = total_revenue - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("Net Revenue", f"${net_revenue:,.2f}")

    st.markdown("---")
    st.subheader("Revenue by Song")

    songs_with_revenue = [
        {
            'title': s['title'],
            'artist': s.get('artist', 'Unknown'),
            'revenue': s.get('revenue', {}).get('total_earned', 0),
            'expenses': sum(e.get('amount', 0) for e in s.get('revenue', {}).get('expenses', []))
        }
        for s in songs
    ]

    songs_with_revenue.sort(key=lambda x: x['revenue'], reverse=True)

    if songs_with_revenue:
        df = pd.DataFrame(songs_with_revenue)
        df.columns = ['Title', 'Artist', 'Revenue', 'Expenses']
        df['Revenue'] = df['Revenue'].apply(lambda x: f"${x:,.2f}")
        df['Expenses'] = df['Expenses'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No revenue data yet")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
if selected_act != "ALL" and selected_act in ACTS:
    st.caption(f"© 2026 {ACTS[selected_act]['name']} • Read-Only Portal")
else:
    st.caption("© 2026 Ridgemont Studio • Read-Only Portal")
