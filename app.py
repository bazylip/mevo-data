import streamlit as st
from streamlit_folium import st_folium

from charts import (
    build_day_hour_heatmap,
    build_duration_histogram,
    build_frequency_chart,
    build_station_heatmap,
    build_top_stations_chart,
    build_top_stations_map,
)
from constants import MONTH_NAMES_SHORT, TRANSLATIONS
from data_processing import (
    compute_activity_heatmap,
    compute_day_hour_matrix,
    compute_distances,
    compute_duration_bins,
    compute_frequency,
    compute_fun_stats,
    compute_overview_metrics,
    compute_station_stats,
    parse_zip,
)

st.set_page_config(page_title="Mevo Wrapped", layout="wide", page_icon="🚲")

# --- Language ---
lang = st.query_params.get("lang", "pl")
if lang not in ("pl", "en"):
    lang = "pl"


def t(key):
    return TRANSLATIONS[key][lang]


st.markdown(
    """
    <style>
    .fun-card {
        background: #F0F0F0;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E0E0E0;
        margin-bottom: 12px;
    }
    .fun-card .emoji { font-size: 1.5rem; }
    .fun-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F15B4E;
    }
    .fun-card .label {
        font-size: 0.85rem;
        color: #777;
    }
    .tooltip-card {
        position: relative;
        cursor: help;
    }
    .tooltip-card .tooltip-text {
        visibility: hidden;
        background-color: #ffffff;
        color: #444;
        text-align: left;
        border-radius: 8px;
        padding: 8px 12px;
        border: 1px solid #ddd;
        position: absolute;
        z-index: 10;
        bottom: 105%;
        left: 50%;
        transform: translateX(-50%);
        min-width: 250px;
        font-size: 0.8rem;
        line-height: 1.4;
    }
    .tooltip-card:hover .tooltip-text {
        visibility: visible;
    }
    h2, h3 {
        color: #0B163F !important;
    }
    .station-radio [role="radiogroup"] {
        gap: 0.15rem;
    }
    .station-radio [role="radiogroup"] label {
        padding: 0.55rem 0.75rem !important;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

_title_col, _lang_col = st.columns([8, 1])
with _title_col:
    st.title("Mevo Wrapped")
with _lang_col:
    _pl_style = "opacity:1;background:#eee;border-radius:6px;padding:2px 6px;" if lang == "pl" else "opacity:0.4;padding:2px 6px;"
    _en_style = "opacity:1;background:#eee;border-radius:6px;padding:2px 6px;" if lang == "en" else "opacity:0.4;padding:2px 6px;"
    st.markdown(
        f'<div style="font-size:1.6rem;display:flex;gap:4px;justify-content:flex-end;padding-top:18px;">'
        f'<a href="?lang=pl" target="_self" style="text-decoration:none;{_pl_style}">🇵🇱</a>'
        f'<a href="?lang=en" target="_self" style="text-decoration:none;{_en_style}">🇬🇧</a>'
        f'</div>',
        unsafe_allow_html=True,
    )

import os

DEV_MODE = os.environ.get("DEV", "").lower() in ("1", "true")

if DEV_MODE:
    uploaded = None
else:
    uploaded = st.file_uploader(t("upload_label"), type="zip")
    if uploaded is None:
        st.markdown(
            t("how_to_download") + "\n"
            + t("instr_step1") + "\n"
            + t("instr_step2") + "\n"
            + t("instr_step3") + "\n"
            + t("instr_step4") + "\n"
            + t("instr_step5") + "\n"
            + t("instr_step6"),
            unsafe_allow_html=True,
        )
        st.stop()


@st.cache_data
def load_data(file_bytes):
    import io
    buf = io.BytesIO(file_bytes)
    buf.name = "mevo.zip"
    return parse_zip(buf)


if DEV_MODE:
    from pathlib import Path
    df = load_data(Path("mevo.zip").read_bytes())
else:
    df = load_data(uploaded.read())
distances = compute_distances(df)
metrics = compute_overview_metrics(df, distances)
heatmap_data = compute_activity_heatmap(df, month_names_short=MONTH_NAMES_SHORT[lang])

# --- Shareable Summary Card ---
total_km_card = metrics["total_distance_km"]
total_s_card = metrics["total_duration_s"]
total_h_card = int(total_s_card // 3600)
total_min_card = int((total_s_card % 3600) // 60)

# Build heatmap grid HTML
HEAT_RAMP = ["#F0F0F0", "#FDE8E6", "#F9A8A0", "#F67D73", "#F15B4E"]


def _heatmap_color(count):
    if count == 0:
        return HEAT_RAMP[0]
    elif count == 1:
        return HEAT_RAMP[1]
    elif count == 2:
        return HEAT_RAMP[2]
    elif count <= 4:
        return HEAT_RAMP[3]
    else:
        return HEAT_RAMP[4]


# Flatten heatmap days chronologically
HEATMAP_COLS = 22
CELL_PX = 14
GAP_PX = 2
STEP_PX = CELL_PX + GAP_PX

month_names_short = MONTH_NAMES_SHORT[lang]
heatmap_cells = ""
month_labels_html = ""
prev_month = None
day_index = 0
months_seen = 0
for week in heatmap_data["weeks"]:
    for day in week:
        if not day["in_range"]:
            continue
        m = day["date"].month
        if m != prev_month:
            months_seen += 1
            if months_seen % 3 == 1:
                row = day_index // HEATMAP_COLS
                y_pos = row * STEP_PX
                lbl = month_names_short[m]
                month_labels_html += f'<div class="month-lbl" style="top:{y_pos}px;">{lbl}</div>'
            prev_month = m
        color = _heatmap_color(day["count"])
        heatmap_cells += f'<div class="cell" style="background:{color};"></div>'
        day_index += 1

share_text = t("card_share_text").format(km=f"{total_km_card:.1f}")

import streamlit.components.v1 as components

card_component_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: transparent; display: flex; flex-direction: column; align-items: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  #card {{
    background: #ffffff;
    border-radius: 20px;
    padding: 40px 32px 32px;
    width: 420px;
    aspect-ratio: 9 / 16;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    color: #0B163F;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{ text-align: center; margin-bottom: 24px; }}
  .header .emoji {{ font-size: 2rem; margin-bottom: 4px; }}
  .header .title {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; color: #F15B4E; }}
  .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 28px; }}
  .stat {{ text-align: center; background: #fdf5f4; border-radius: 12px; padding: 16px 8px; }}
  .stat .num {{ font-size: 1.8rem; font-weight: 800; color: #F15B4E; white-space: nowrap; }}
  .stat .lbl {{ font-size: 0.8rem; color: #888; margin-top: 2px; }}
  .heatmap-section {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
  .heatmap-title {{ font-size: 0.85rem; font-weight: 600; color: #555; margin-bottom: 8px; text-align: center; }}
  .heatmap-wrap {{ position: relative; padding-left: 15px; margin: 0 auto; width: fit-content; }}
  .heatmap-wrap .month-lbl {{ position: absolute; left: -15px; font-size: 0.65rem; color: #999; font-weight: 600; line-height: {CELL_PX}px; }}
  .heatmap-grid {{ display: grid; grid-template-columns: repeat({HEATMAP_COLS}, {CELL_PX}px); gap: {GAP_PX}px; }}
  .heatmap-grid .cell {{ width: {CELL_PX}px; height: {CELL_PX}px; border-radius: 2px; }}
  .footer {{ text-align: center; margin-top: 20px; }}
  .footer span {{ font-size: 0.75rem; color: #bbb; }}
  .buttons {{ display: flex; gap: 12px; margin-top: 16px; justify-content: center; }}
  .buttons button {{
    border: none; border-radius: 8px; padding: 10px 24px;
    font-size: 0.9rem; cursor: pointer; font-weight: 600;
  }}
  .btn-share {{ background: #F15B4E; color: white; transition: background 0.2s; }}
  .btn-share:hover {{ opacity: 0.85; }}
</style>
</head>
<body>
  <div id="card">
    <div class="header">
      <div class="emoji">🚲</div>
      <div class="title">Mevo Wrapped</div>
    </div>
    <div class="stats">
      <div class="stat"><div class="num">{metrics['total_trips']}</div><div class="lbl">{t("card_trips")}</div></div>
      <div class="stat"><div class="num">{total_km_card:.1f} km</div><div class="lbl">{t("card_distance")}</div></div>
      <div class="stat"><div class="num">{total_h_card} h {total_min_card} min</div><div class="lbl">{t("card_time")}</div></div>
      <div class="stat"><div class="num">{metrics['unique_stations']}</div><div class="lbl">{t("card_stations")}</div></div>
    </div>
    <div class="heatmap-section">
      <div class="heatmap-title">{t("card_activity")}</div>
      <div class="heatmap-wrap">
        {month_labels_html}
        <div class="heatmap-grid">{heatmap_cells}</div>
      </div>
    </div>
    <div class="footer"><span>mevo-wrapped.streamlit.app</span></div>
  </div>
  <div class="buttons">
    <button class="btn-share" onclick="shareCard()">{t("card_share")}</button>
  </div>
  <script>
    function shareCard() {{
      var btn = document.querySelector('.btn-share');
      var shareText = '{share_text}';
      var shareUrl = 'https://mevo-wrapped.streamlit.app';
      btn.disabled = true;
      html2canvas(document.getElementById('card'), {{scale: 3, backgroundColor: null, useCORS: true}}).then(function(canvas) {{
        canvas.toBlob(function(blob) {{
          var file = new File([blob], 'mevo-wrapped.png', {{type: 'image/png'}});
          if (navigator.canShare && navigator.canShare({{files: [file]}})) {{
            navigator.share({{files: [file], text: shareText, url: shareUrl}}).catch(function(){{}}).finally(function() {{
              btn.disabled = false;
            }});
          }} else if (typeof ClipboardItem !== 'undefined') {{
            navigator.clipboard.write([new ClipboardItem({{'image/png': blob}})])
              .then(function() {{ showCopied(btn); }})
              .catch(function() {{ fallbackDownload(canvas, btn); }});
          }} else {{
            fallbackDownload(canvas, btn);
          }}
        }}, 'image/png');
      }});
    }}
    function showCopied(btn) {{
      btn.textContent = '{t("card_copied")}';
      btn.style.background = '#22c55e';
      btn.disabled = false;
      setTimeout(function() {{
        btn.textContent = '{t("card_share")}';
        btn.style.background = '#F15B4E';
      }}, 2000);
    }}
    function fallbackDownload(canvas, btn) {{
      var link = document.createElement('a');
      link.download = 'mevo-wrapped.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      showCopied(btn);
    }}
  </script>
</body>
</html>
"""

components.html(card_component_html, height=810)

# --- Overview: Row 1 ---
st.markdown("---")

total_km = metrics["total_distance_km"]

total_s = metrics["total_duration_s"]
total_h = int(total_s // 3600)
total_min = int((total_s % 3600) // 60)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(t("total_trips"), f"{metrics['total_trips']}")
with c2:
    st.metric(t("total_distance"), f"{total_km:.1f} km")
with c3:
    st.metric(t("total_time"), f"{total_h} h {total_min} min")
with c4:
    st.metric(t("unique_stations"), f"{metrics['unique_stations']}")

# --- Overview: Row 2 ---
avg_s = metrics["avg_duration_s"]
avg_min = int(avg_s // 60)
avg_sec = int(avg_s % 60)

avg_dist = metrics["avg_distance_km"]

date_range = f'{metrics["date_min"].strftime("%d.%m.%Y")} — {metrics["date_max"].strftime("%d.%m.%Y")}'

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.metric(t("avg_time"), f"{avg_min} min {avg_sec} s")
with c6:
    st.metric(t("avg_distance"), f"{avg_dist:.1f} km")
with c7:
    st.metric(t("days_with_trip"), f"{metrics['days_with_trips']}")
with c8:
    st.metric(t("date_range"), date_range)

# --- Frequency chart ---
st.markdown("---")
st.subheader(t("trip_frequency"))
freq_options = {t("days"): "day", t("weeks"): "week", t("months"): "month"}
freq_label = st.radio(
    "Group by:" if lang == "en" else "Grupuj po:",
    list(freq_options.keys()),
    index=2,
    horizontal=True,
    label_visibility="collapsed",
)
freq_df = compute_frequency(df, freq_options[freq_label])
st.plotly_chart(build_frequency_chart(freq_df, lang=lang), use_container_width=True, config={"staticPlot": True})

# --- Duration histogram ---
st.markdown("---")
st.subheader(t("trip_duration_dist"))
durations_min = compute_duration_bins(df)
st.plotly_chart(build_duration_histogram(durations_min, lang=lang), use_container_width=True, config={"staticPlot": True})

# --- Day-hour heatmap ---
st.markdown("---")
st.subheader(t("when_do_you_ride"))
matrix = compute_day_hour_matrix(df)
st.plotly_chart(build_day_hour_heatmap(matrix, lang=lang), use_container_width=True, config={"staticPlot": True})

# --- Heatmap map ---
st.markdown("---")
st.subheader(t("station_map"))
map_mode_label = st.radio(
    "Show:" if lang == "en" else "Pokaż:",
    [t("all_stations"), t("start_stations"), t("end_stations")],
    horizontal=True,
    label_visibility="collapsed",
)
map_mode_map = {t("all_stations"): "all", t("start_stations"): "start", t("end_stations"): "end"}
map_mode = map_mode_map[map_mode_label]
station_map = build_station_heatmap(df, mode=map_mode)
st_folium(station_map, height=500, use_container_width=True, returned_objects=[])

# --- Top stations ---
st.markdown("---")
st.subheader(t("top_stations"))
station_df = compute_station_stats(df)
top_n = min(10, len(station_df))
top_stations = station_df.head(top_n)

st.plotly_chart(build_top_stations_chart(station_df, n=top_n, lang=lang), use_container_width=True, config={"staticPlot": True})

col_radio, col_map = st.columns([2, 5])
with col_radio:
    station_options = [f"#{i+1} {top_stations.iloc[i]['code']}" for i in range(top_n)]
    st.markdown('<div class="station-radio">', unsafe_allow_html=True)
    selected_station = st.radio(
        t("select_station"),
        station_options,
        index=None,
        label_visibility="collapsed",
    )
    st.markdown('</div>', unsafe_allow_html=True)
with col_map:
    selected_idx = None
    if selected_station is not None:
        selected_idx = station_options.index(selected_station)
    top_map = build_top_stations_map(top_stations, selected_index=selected_idx, lang=lang)
    st_folium(top_map, height=400, use_container_width=True, returned_objects=[])

# --- Fun stats ---
st.markdown("---")
st.subheader(t("fun_stats"))
fun = compute_fun_stats(df, distances)


def fun_card(emoji, value, label, tooltip=None):
    tooltip_html = ""
    extra_class = ""
    if tooltip:
        tooltip_html = f'<span class="tooltip-text">{tooltip}</span>'
        extra_class = " tooltip-card"
    return f"""
    <div class="fun-card{extra_class}">
        <div class="emoji">{emoji}</div>
        <div class="value">{value}</div>
        <div class="label">{label}</div>
        {tooltip_html}
    </div>
    """


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**{t('ecology')}**", unsafe_allow_html=True)
    st.markdown(
        fun_card(
            "🌿", f"{fun['environmental']['co2_saved_kg']} kg", t("co2_saved"),
            tooltip=t("co2_tooltip").format(km=fun['environmental']['total_distance_km']),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "⛽", f"{fun['environmental']['fuel_saved_liters']} l", t("fuel_saved"),
            tooltip=t("fuel_tooltip").format(km=fun['environmental']['total_distance_km']),
        ),
        unsafe_allow_html=True,
    )
    # Calories with weight slider
    st.markdown(f"**{t('calories_label')}**", unsafe_allow_html=True)
    weight_kg = st.slider(t("weight_slider"), 40, 150, 75, key="weight_slider")
    total_hours = metrics["total_duration_s"] / 3600.0
    calories = round(6.8 * weight_kg * total_hours)
    st.markdown(
        fun_card(
            "🔥", f"{calories} kcal", t("calories_burned"),
            tooltip=t("calories_tooltip").format(w=weight_kg, h=f"{total_hours:.1f}"),
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(f"**{t('records')}**", unsafe_allow_html=True)
    longest_min = fun["records"]["longest_trip_duration_s"] / 60
    st.markdown(
        fun_card(
            "⏱️", f"{longest_min:.0f} min",
            f"{t('longest_trip')} ({fun['records']['longest_trip_start']} → {fun['records']['longest_trip_end']})",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "📅", f"{fun['records']['most_trips_in_day_count']}",
            f"{t('trips_in_one_day')} ({fun['records']['most_trips_in_day_date']})",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card("🔥", f"{fun['records']['longest_streak_days']} {t('days_unit')}", f"{t('longest_streak')} ({fun['records']['longest_streak_range']})"),
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(f"**{t('milestones')}**", unsafe_allow_html=True)
    st.markdown(
        fun_card("🎉", fun["milestones"]["first_trip_date"].strftime("%d.%m.%Y"), t("first_trip")),
        unsafe_allow_html=True,
    )
    if fun["milestones"]["hundredth_trip_date"]:
        st.markdown(
            fun_card("💯", fun["milestones"]["hundredth_trip_date"].strftime("%d.%m.%Y"), t("hundredth_trip")),
            unsafe_allow_html=True,
        )
    st.markdown(
        fun_card("📊", fun["milestones"]["busiest_month"], t("busiest_month")),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "📅",
            f"{fun['milestones']['most_active_week']}",
            f"{t('busiest_week')} ({fun['milestones']['most_active_week_count']} {t('trips_unit')})",
        ),
        unsafe_allow_html=True,
    )

# --- Footer ---
st.markdown("---")
st.caption(
    t("footer_disclaimer").format(
        null_end=metrics['null_end_count'],
        null_start=metrics['null_start_count'],
    )
)
