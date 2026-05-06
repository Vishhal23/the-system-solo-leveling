"""
THE SYSTEM — Hunter Dashboard
═════════════════════════════
A Streamlit web interface to track stats, history, and daily quests.
"""

import sys
import os
from pathlib import Path

# Add the project root to sys.path so we can import from core/db/config
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import USER_ID
from db.models import get_user_stats, get_task_history, get_total_tasks, get_todays_quests
from core.leveling import xp_for_level

# ── Theming & Setup ─────────────────────────────────────
st.set_page_config(
    page_title="The System - Hunter Status",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Solo Leveling aesthetic
st.markdown(
    """
    <style>
    /* Dark Theme with Neon Blue/Purple accents */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    h1, h2, h3 {
        color: #58a6ff;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #79c0ff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
    }
    hr {
        border-color: #30363d;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Data Loading ────────────────────────────────────────

@st.cache_data(ttl=5) # Refresh every 5 seconds
def load_data():
    stats = get_user_stats(USER_ID)
    history = get_task_history(USER_ID, limit=50)
    total_tasks = get_total_tasks(USER_ID)
    todays_quests = get_todays_quests(USER_ID)
    return stats, history, total_tasks, todays_quests

stats, history, total_tasks, todays_quests = load_data()

if not stats:
    st.error("⚠️ Hunter profile not found. Have you initialized the database?")
    st.stop()

# ── Header ──────────────────────────────────────────────
st.markdown("<h1>⚔️ STATUS WINDOW</h1>", unsafe_allow_html=True)
st.markdown("---")

# ── Top Metrics ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Level</div>
            <div class="metric-value">{stats['level']}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    job_class = stats.get('job_class', 'None')
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Job Class</div>
            <div class="metric-value">{job_class}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Total Quests</div>
            <div class="metric-value">{total_tasks}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Hunter Name</div>
            <div class="metric-value" style="font-size:1.5rem; margin-top:10px;">{stats['username']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── XP Progress Bar ─────────────────────────────────────
from core.leveling import xp_to_next_level
current_xp_in_level, required_xp = xp_to_next_level(stats["total_xp"], stats["level"])
progress = min(current_xp_in_level / required_xp, 1.0) if required_xp > 0 else 1.0

st.markdown(f"**Experience Points (XP):** {current_xp_in_level} / {required_xp}")
st.progress(progress)
st.markdown("<br>", unsafe_allow_html=True)


# ── Main Content Area ───────────────────────────────────
left_col, right_col = st.columns([1.5, 1])

with left_col:
    st.markdown("<h3>🎯 Daily Quests</h3>", unsafe_allow_html=True)
    
    if not todays_quests:
        st.info("No daily quests assigned for today yet.")
    else:
        for q in todays_quests:
            status = "✅ Completed" if q["completed"] else "❌ Incomplete"
            penalty = "⚠️ PENALTY APPLIED" if q["penalty_sent"] else ""
            color = "#3fb950" if q["completed"] else "#f85149"
            
            st.markdown(
                f"""
                <div style="background-color: #161b22; border-left: 4px solid {color}; padding: 15px; margin-bottom: 10px; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong style="font-size: 1.1rem;">{q['quest_name']}</strong>
                        <span style="color: {color};">{status}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #8b949e; margin-top: 5px;">
                        Deadline: {q['deadline']} {penalty}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("<br><h3>📜 Recent History</h3>", unsafe_allow_html=True)
    if history:
        df = pd.DataFrame(history)
        df = df[['task_name', 'rank', 'xp_awarded', 'stat_type', 'completed_at']]
        df.columns = ['Task Name', 'Rank', 'XP', 'Stat', 'Date']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No quest history found.")

with right_col:
    st.markdown("<h3>📈 Stat Distribution</h3>", unsafe_allow_html=True)
    
    # Radar Chart
    categories = ['Strength', 'Intelligence', 'Agility', 'Endurance', 'Charisma']
    values = [
        stats['strength'],
        stats['intelligence'],
        stats['agility'],
        stats['endurance'],
        stats['charisma']
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(88, 166, 255, 0.5)',
        line=dict(color='#58a6ff'),
        name='Hunter Stats'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values) + 5, 20)],
                tickfont=dict(color='#8b949e'),
                gridcolor='#30363d'
            ),
            angularaxis=dict(
                tickfont=dict(color='#c9d1d9', size=14),
                gridcolor='#30363d'
            ),
            bgcolor='#0d1117'
        ),
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        margin=dict(l=40, r=40, t=20, b=20),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
