import streamlit as st
from streamlit_folium import st_folium

from charts import (
    build_day_hour_heatmap,
    build_duration_histogram,
    build_frequency_chart,
    build_station_heatmap,
    build_top_stations_chart,
)
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

st.markdown(
    """
    <style>
    .fun-card {
        background: linear-gradient(135deg, #1A1D23, #252830);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #333;
        margin-bottom: 12px;
    }
    .fun-card .emoji { font-size: 1.5rem; }
    .fun-card .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00D4FF;
    }
    .fun-card .label {
        font-size: 0.85rem;
        color: #999;
    }
    .tooltip-card {
        position: relative;
        cursor: help;
    }
    .tooltip-card .tooltip-text {
        visibility: hidden;
        background-color: #252830;
        color: #ccc;
        text-align: left;
        border-radius: 8px;
        padding: 8px 12px;
        border: 1px solid #444;
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
    .station-item {
        background: linear-gradient(135deg, #1A1D23, #252830);
        border-radius: 10px;
        padding: 12px 16px;
        border: 1px solid #333;
        margin-bottom: 8px;
        cursor: pointer;
    }
    .station-item .rank {
        font-size: 1.3rem;
        font-weight: 700;
        color: #00D4FF;
        margin-right: 12px;
    }
    .station-item .code {
        font-weight: 600;
        color: #FAFAFA;
        font-size: 1rem;
    }
    .station-item .count {
        color: #00D4FF;
        font-weight: 600;
    }
    .station-item .address {
        color: #888;
        font-size: 0.85rem;
    }
    div[data-baseweb="popover"] > div {
        min-width: 520px !important;
        max-width: 560px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Mevo Wrapped")

import os

DEV_MODE = os.environ.get("DEV", "").lower() in ("1", "true")

if DEV_MODE:
    uploaded = None
else:
    uploaded = st.file_uploader("Wgraj plik mevo.zip", type="zip")
    if uploaded is None:
        st.markdown(
            "#### Jak pobrać dane?\n"
            '1. Wejdź na <a href="https://rowermevo.pl" target="_blank">rowermevo.pl</a>\n'
            "2. Nie pobieraj aplikacji, zamiast tego zaloguj się bezpośrednio na stronie\n"
            "3. Kliknij **Profil** (prawy górny róg)\n"
            "4. Przewiń w dół do sekcji **Twoje dane**\n"
            "5. Kliknij **Tworzenie plików JSON** aby wygenerować dane\n"
            "6. Pobierz archiwum ZIP z danymi\n"
            "7. Wgraj pobrany plik ZIP powyżej",
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
heatmap_data = compute_activity_heatmap(df)

# --- Shareable Summary Card ---
total_km_card = metrics["total_distance_km"]
total_s_card = metrics["total_duration_s"]
total_h_card = int(total_s_card // 3600)
total_min_card = int((total_s_card % 3600) // 60)

# Build heatmap grid HTML
GREEN_RAMP = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]


def _heatmap_color(count):
    if count == 0:
        return GREEN_RAMP[0]
    elif count == 1:
        return GREEN_RAMP[1]
    elif count == 2:
        return GREEN_RAMP[2]
    elif count <= 4:
        return GREEN_RAMP[3]
    else:
        return GREEN_RAMP[4]


# Flatten heatmap days chronologically
from constants import MONTH_NAMES_PL_SHORT

HEATMAP_COLS = 22
CELL_PX = 14
GAP_PX = 2
STEP_PX = CELL_PX + GAP_PX

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
                lbl = MONTH_NAMES_PL_SHORT[m]
                month_labels_html += f'<div class="month-lbl" style="top:{y_pos}px;">{lbl}</div>'
            prev_month = m
        color = _heatmap_color(day["count"])
        heatmap_cells += f'<div class="cell" style="background:{color};"></div>'
        day_index += 1

share_text = f"Przejechałem {total_km_card:.1f} km na Mevo! Sprawdź swoje wyniki na mevo-wrapped.streamlit.app"

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
    color: #1a1a2e;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{ text-align: center; margin-bottom: 24px; }}
  .header .emoji {{ font-size: 2rem; margin-bottom: 4px; }}
  .header .title {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }}
  .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 28px; }}
  .stat {{ text-align: center; background: #f8f9fa; border-radius: 12px; padding: 16px 8px; }}
  .stat .num {{ font-size: 1.8rem; font-weight: 800; color: #1a1a2e; white-space: nowrap; }}
  .stat .lbl {{ font-size: 0.8rem; color: #888; margin-top: 2px; }}
  .heatmap-section {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
  .heatmap-title {{ font-size: 0.85rem; font-weight: 600; color: #555; margin-bottom: 8px; text-align: center; }}
  .heatmap-wrap {{ position: relative; padding-left: 30px; margin: 0 auto; width: fit-content; }}
  .heatmap-wrap .month-lbl {{ position: absolute; left: 0; font-size: 0.65rem; color: #999; font-weight: 600; line-height: {CELL_PX}px; }}
  .heatmap-grid {{ display: grid; grid-template-columns: repeat({HEATMAP_COLS}, {CELL_PX}px); gap: {GAP_PX}px; }}
  .heatmap-grid .cell {{ width: {CELL_PX}px; height: {CELL_PX}px; border-radius: 2px; }}
  .footer {{ text-align: center; margin-top: 20px; }}
  .footer span {{ font-size: 0.75rem; color: #bbb; }}
  .buttons {{ display: flex; gap: 12px; margin-top: 16px; justify-content: center; }}
  .buttons button {{
    border: none; border-radius: 8px; padding: 10px 24px;
    font-size: 0.9rem; cursor: pointer; font-weight: 600;
  }}
  .btn-dl {{ background: #1a1a2e; color: white; }}
  .btn-share {{ background: #00D4FF; color: #1a1a2e; }}
  .btn-dl:hover {{ opacity: 0.85; }}
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
      <div class="stat"><div class="num">{metrics['total_trips']}</div><div class="lbl">przejazdy</div></div>
      <div class="stat"><div class="num">{total_km_card:.1f} km</div><div class="lbl">dystans</div></div>
      <div class="stat"><div class="num">{total_h_card} h {total_min_card} min</div><div class="lbl">czas jazdy</div></div>
      <div class="stat"><div class="num">{metrics['unique_stations']}</div><div class="lbl">stacje</div></div>
    </div>
    <div class="heatmap-section">
      <div class="heatmap-title">Aktywność w ostatnim roku</div>
      <div class="heatmap-wrap">
        {month_labels_html}
        <div class="heatmap-grid">{heatmap_cells}</div>
      </div>
    </div>
    <div class="footer"><span>mevo-wrapped.streamlit.app</span></div>
  </div>
  <div class="buttons">
    <button class="btn-dl" onclick="downloadCard()">Pobierz</button>
    <button class="btn-share" onclick="shareCard()">Udostępnij</button>
  </div>
  <script>
    function downloadCard() {{
      html2canvas(document.getElementById('card'), {{scale: 3, backgroundColor: null, useCORS: true}}).then(function(canvas) {{
        var link = document.createElement('a');
        link.download = 'mevo-wrapped.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
      }});
    }}
    function shareCard() {{
      var text = '{share_text}';
      if (navigator.share) {{
        navigator.share({{title: 'Mevo Wrapped', text: text, url: 'https://mevo-wrapped.streamlit.app'}}).catch(function(){{}});
      }} else {{
        navigator.clipboard.writeText(text).then(function() {{
          var btn = document.querySelector('.btn-share');
          btn.textContent = 'Skopiowano!';
          setTimeout(function() {{ btn.textContent = 'Udostępnij'; }}, 2000);
        }});
      }}
    }}
  </script>
</body>
</html>
"""

components.html(card_component_html, height=860)

# --- Overview: Row 1 ---
st.markdown("---")

total_km = metrics["total_distance_km"]

total_s = metrics["total_duration_s"]
total_h = int(total_s // 3600)
total_min = int((total_s % 3600) // 60)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Liczba przejazdów", f"{metrics['total_trips']}")
with c2:
    st.metric("Łączny dystans", f"{total_km:.1f} km")
with c3:
    st.metric("Łączny czas jazdy", f"{total_h} h {total_min} min")
with c4:
    st.metric("Unikalne stacje", f"{metrics['unique_stations']}")

# --- Overview: Row 2 ---
avg_s = metrics["avg_duration_s"]
avg_min = int(avg_s // 60)
avg_sec = int(avg_s % 60)

avg_dist = metrics["avg_distance_km"]

date_range = f'{metrics["date_min"].strftime("%d.%m.%Y")} — {metrics["date_max"].strftime("%d.%m.%Y")}'

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.metric("Śr. czas przejazdu", f"{avg_min} min {avg_sec} s")
with c6:
    st.metric("Śr. dystans", f"{avg_dist:.1f} km")
with c7:
    st.metric("Dni z przejazdem", f"{metrics['days_with_trips']}")
with c8:
    st.metric("Zakres dat", date_range)

# --- Frequency chart ---
st.markdown("---")
st.subheader("Częstotliwość przejazdów")
freq_options = {"Dni": "day", "Tygodnie": "week", "Miesiące": "month"}
freq_label = st.radio(
    "Grupuj po:",
    list(freq_options.keys()),
    index=2,
    horizontal=True,
    label_visibility="collapsed",
)
freq_df = compute_frequency(df, freq_options[freq_label])
st.plotly_chart(build_frequency_chart(freq_df), use_container_width=True, config={"staticPlot": True})

# --- Heatmap map ---
st.markdown("---")
st.subheader("Mapa stacji")
map_mode_label = st.radio(
    "Pokaż:",
    ["Stacje startowe", "Stacje końcowe"],
    horizontal=True,
    label_visibility="collapsed",
)
map_mode = "start" if map_mode_label == "Stacje startowe" else "end"
station_map = build_station_heatmap(df, mode=map_mode)
st_folium(station_map, height=500, use_container_width=True, returned_objects=[])

# --- Top stations ---
st.markdown("---")
st.subheader("Najczęściej odwiedzane stacje")
station_df = compute_station_stats(df)
top_n = min(10, len(station_df))
top_stations = station_df.head(top_n)

st.plotly_chart(build_top_stations_chart(station_df, n=top_n), use_container_width=True, config={"staticPlot": True})

cols_per_row = 5
rows_needed = (top_n + cols_per_row - 1) // cols_per_row
for row_idx in range(rows_needed):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        i = row_idx * cols_per_row + col_idx
        if i >= top_n:
            break
        stn = top_stations.iloc[i]
        with cols[col_idx]:
            with st.popover(f"**#{i+1}** {stn['code']}"):
                st.markdown(f"**{stn['code']}**")
                st.markdown(f"{stn['address']}")
                st.markdown(f"Starty: **{int(stn['start_count'])}** | Końce: **{int(stn['end_count'])}** | Łącznie: **{int(stn['total_count'])}**")
                mini_map = __import__("folium").Map(
                    location=[stn["lat"], stn["lng"]],
                    zoom_start=13,
                    tiles="CartoDB positron",
                )
                __import__("folium").Marker(
                    location=[stn["lat"], stn["lng"]],
                    popup=stn["code"],
                ).add_to(mini_map)
                st_folium(mini_map, height=400, width=460, returned_objects=[])

# --- Duration histogram ---
st.markdown("---")
st.subheader("Rozkład czasu podróży")
durations_min = compute_duration_bins(df)
st.plotly_chart(build_duration_histogram(durations_min), use_container_width=True, config={"staticPlot": True})

# --- Day-hour heatmap ---
st.markdown("---")
st.subheader("Kiedy jeździsz?")
matrix = compute_day_hour_matrix(df)
st.plotly_chart(build_day_hour_heatmap(matrix), use_container_width=True, config={"staticPlot": True})

# --- Fun stats ---
st.markdown("---")
st.subheader("Ciekawostki")
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
    st.markdown("**Ekologia**", unsafe_allow_html=True)
    st.markdown(
        fun_card(
            "🌿", f"{fun['environmental']['co2_saved_kg']} kg", "CO₂ zaoszczędzone",
            tooltip=(
                f"Obliczono na podstawie {fun['environmental']['total_distance_km']} km przejechanych rowerem "
                f"zamiast samochodem. Przyjęto średnią emisję samochodu: 120 g CO₂/km."
            ),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "⛽", f"{fun['environmental']['fuel_saved_liters']} l", "Paliwa zaoszczędzonego",
            tooltip=(
                f"Obliczono na podstawie {fun['environmental']['total_distance_km']} km. "
                f"Przyjęto średnie spalanie samochodu: 7 l/100 km."
            ),
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown("**Rekordy**", unsafe_allow_html=True)
    longest_min = fun["records"]["longest_trip_duration_s"] / 60
    st.markdown(
        fun_card(
            "⏱️", f"{longest_min:.0f} min",
            f"Najdłuższa podróż ({fun['records']['longest_trip_start']} → {fun['records']['longest_trip_end']})",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "📅", f"{fun['records']['most_trips_in_day_count']}",
            f"Podróży w jeden dzień ({fun['records']['most_trips_in_day_date']})",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card("🔥", f"{fun['records']['longest_streak_days']} dni", "Najdłuższa seria"),
        unsafe_allow_html=True,
    )
with col3:
    st.markdown("**Kamienie milowe**", unsafe_allow_html=True)
    st.markdown(
        fun_card("🎉", fun["milestones"]["first_trip_date"].strftime("%d.%m.%Y"), "Pierwsza podróż"),
        unsafe_allow_html=True,
    )
    if fun["milestones"]["hundredth_trip_date"]:
        st.markdown(
            fun_card("💯", fun["milestones"]["hundredth_trip_date"].strftime("%d.%m.%Y"), "Setna podróż"),
            unsafe_allow_html=True,
        )
    st.markdown(
        fun_card("📊", fun["milestones"]["busiest_month"], "Najbardziej aktywny miesiąc"),
        unsafe_allow_html=True,
    )
    st.markdown(
        fun_card(
            "📅",
            f"{fun['milestones']['most_active_week']}",
            f"Najbardziej aktywny tydzień ({fun['milestones']['most_active_week_count']} przejazdów)",
        ),
        unsafe_allow_html=True,
    )

# Calories with weight slider
st.markdown("**Kalorie**", unsafe_allow_html=True)
weight_kg = st.slider("Twoja waga (kg)", 40, 150, 75, key="weight_slider")
# MET ~6.8 for moderate cycling, kcal/h = MET * weight
total_hours = metrics["total_duration_s"] / 3600.0
calories = round(6.8 * weight_kg * total_hours)
st.markdown(
    fun_card(
        "🔥", f"{calories} kcal", "Spalonych kalorii",
        tooltip=f"Obliczono na podstawie MET=6.8 (umiarkowana jazda na rowerze) × {weight_kg} kg × {total_hours:.1f} h jazdy.",
    ),
    unsafe_allow_html=True,
)

# --- Footer ---
st.markdown("---")
st.caption(
    "⚠️ Dystans jest szacunkowy (odległość w linii prostej × 1,3). "
    f"Pominięto {metrics['null_end_count']} podróży bez stacji końcowej i {metrics['null_start_count']} bez stacji początkowej w obliczeniach dystansu. "
    "Dane pochodzą z eksportu aplikacji Mevo."
)
