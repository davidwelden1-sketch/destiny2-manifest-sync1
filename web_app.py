"""Destiny 2 Build Lab — initial interactive research dashboard.

Run locally: pip install -r requirements-web.txt && streamlit run web_app.py
All numerical inputs are hypothetical unless independently measured.
"""
import streamlit as st
from simulator.ttk import WeaponProfile, optimal_ttk
from simulator.survivability import effective_resistance, effective_health
from simulator.ability_timing import cooldown_seconds

st.set_page_config(page_title="Destiny 2 Build Lab", page_icon="🛡️", layout="wide")
st.title("Destiny 2 Build Lab")
st.caption("Experimental research dashboard · Not a certified build recommendation engine")
character = st.selectbox("Class", ["Hunter", "Titan", "Warlock"])
activity = st.selectbox("Activity", ["PvE", "PvP"])
st.info(f"Research context: {character} · {activity}. The current calculators use user-entered hypothetical inputs.")
tab_ttk, tab_survival, tab_ability, tab_project = st.tabs(
    ["PvP TTK", "Survivability", "Ability timing", "Project status"]
)
with tab_ttk:
    st.subheader("Constant-rate weapon TTK model")
    rpm = st.number_input("Rounds per minute", min_value=1.0, value=140.0)
    crit = st.number_input("Precision damage", min_value=0.01, value=80.0)
    body = st.number_input("Body damage", min_value=0.01, value=50.0)
    health = st.number_input("Target effective health", min_value=0.01, value=230.0)
    buff = st.number_input("Damage multiplier", min_value=0.01, value=1.0)
    try:
        result = optimal_ttk(WeaponProfile(rpm, crit, body), health, buff)
        st.metric("Calculated optimal TTK", f"{result['ttk_seconds']:.3f} s")
        st.metric("Precision shots", result["shots"])
        st.caption(result["model"])
    except ValueError as exc:
        st.error(str(exc))
with tab_survival:
    st.subheader("Hypothetical resistance stacking")
    health_pool = st.number_input("Health pool", min_value=1.0, value=200.0)
    shields = st.number_input("Extra shields", min_value=0.0, value=0.0)
    dr_a = st.slider("Resistance A (%)", 0, 95, 20)
    dr_b = st.slider("Resistance B (%)", 0, 95, 30)
    policy = st.selectbox("Assumed stacking policy", ["multiplicative", "highest"])
    reductions = [dr_a / 100, dr_b / 100]
    st.metric("Effective resistance", f"{effective_resistance(reductions, policy):.1%}")
    st.metric("Modelled effective health", f"{effective_health(health_pool, shields, reductions, policy):,.1f}")
    st.warning("These inputs and stacking rules are not independently validated for any particular Destiny 2 effects.")
with tab_ability:
    st.subheader("Cooldown calculation")
    base = st.number_input("Base cooldown (seconds)", min_value=0.01, value=60.0)
    rate = st.number_input("Regeneration rate multiplier", min_value=0.01, value=1.0)
    result = cooldown_seconds(base, rate)
    st.metric("Modelled cooldown", f"{result['seconds']:.2f} s")
    st.caption("This calculation does not account for in-game caps, tiers or event-driven ability regeneration.")
with tab_project:
    st.subheader("Four-phase development")
    st.write("1. Weapon legality: exact-hash socket screening; obtainability not fully certified.")
    st.write("2. Simulation: initial TTK, DR and timing models; calibration pending.")
    st.write("3. Synergy discovery: preliminary Artifact-first candidate screening.")
    st.write("4. Certification: source-aware evidence gates; no fully certified builds yet.")
    st.link_button("View source repository", "https://github.com/davidwelden1-sketch/destiny2-manifest-sync1")
