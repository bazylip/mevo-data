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


df = load_data(uploaded.read())
distances = compute_distances(df)
metrics = compute_overview_metrics(df, distances)

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
