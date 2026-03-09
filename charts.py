import numpy as np
import folium
from folium.plugins import HeatMap
import plotly.graph_objects as go

from constants import COLOR_PALETTE, CORAL_RAMP, DAY_NAMES, DAY_NAMES_PL, GDANSK_CENTER, PLOTLY_LAYOUT_DEFAULTS, TRANSLATIONS


def _layout_defaults(**overrides):
    layout = {**PLOTLY_LAYOUT_DEFAULTS, **overrides}
    return layout


def build_station_heatmap(df, mode="all"):
    """Build a folium heatmap showing start, end, or all station density."""
    m = folium.Map(
        location=GDANSK_CENTER,
        zoom_start=12,
        tiles="CartoDB positron",
    )

    heat_data = []
    if mode in ("start", "all"):
        subset = df[df["has_start_station"]]
        for _, row in subset.iterrows():
            heat_data.append([row["start_lat"], row["start_lng"]])
    if mode in ("end", "all"):
        subset = df[df["has_end_station"]]
        for _, row in subset.iterrows():
            heat_data.append([row["end_lat"], row["end_lng"]])

    if heat_data:
        HeatMap(heat_data, radius=18, blur=12, max_zoom=15).add_to(m)

    return m


def build_day_hour_heatmap(matrix, lang="pl"):
    coral_scale = [[0, "#E8E7E7"], [0.15, "#F9B8B2"], [0.4, "#F58A7E"], [0.7, "#F26254"], [1, "#D94437"]]
    day_lbl = TRANSLATIONS["day"][lang]
    hour_lbl = TRANSLATIONS["hour"][lang]
    trips_lbl = TRANSLATIONS["trips_label"][lang]
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(range(24)),
            y=DAY_NAMES[lang],
            colorscale=coral_scale,
            xgap=2,
            ygap=2,
            hovertemplate=f"{day_lbl}: %{{y}}<br>{hour_lbl}: %{{x}}:00<br>{trips_lbl}: %{{z}}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title=hour_lbl,
            yaxis_title="",
            height=350,
            yaxis={"autorange": "reversed"},
            xaxis={"dtick": 1},
        )
    )
    return fig


def build_duration_histogram(durations_minutes, lang="pl"):
    mean_val = durations_minutes.mean()
    time_lbl = TRANSLATIONS["time_min"][lang]
    count_lbl = TRANSLATIONS["count"][lang]
    mean_lbl = TRANSLATIONS["mean_label"][lang]

    fig = go.Figure(
        data=go.Histogram(
            x=durations_minutes,
            nbinsx=25,
            marker_color=COLOR_PALETTE["primary"],
            hovertemplate=f"{time_lbl}: %{{x:.0f}} min<br>{count_lbl}: %{{y}}<extra></extra>",
        )
    )
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color=COLOR_PALETTE["accent"],
        annotation_text=f"{mean_lbl}: {mean_val:.1f} min",
        annotation_font_color=COLOR_PALETTE["accent"],
        annotation_position="top right",
        annotation_yshift=10,
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title=TRANSLATIONS["trip_time_minutes"][lang],
            yaxis_title=TRANSLATIONS["trip_count"][lang],
            height=350,
        )
    )
    return fig


def build_top_stations_chart(station_df, n=10, lang="pl"):
    top = station_df.head(n).iloc[::-1]
    labels = [f"{code} — {addr[:30]}" for code, addr in zip(top["code"], top["address"])]
    arrivals = TRANSLATIONS["arrivals"][lang]
    departures = TRANSLATIONS["departures"][lang]

    fig = go.Figure(
        data=[
            go.Bar(
                x=top["end_count"],
                y=labels,
                orientation="h",
                marker_color=COLOR_PALETTE["navy"],
                name=arrivals,
                hovertemplate=f"%{{y}}<br>{arrivals}: %{{x}}<extra></extra>",
            ),
            go.Bar(
                x=top["start_count"],
                y=labels,
                orientation="h",
                marker_color=COLOR_PALETTE["primary"],
                name=departures,
                hovertemplate=f"%{{y}}<br>{departures}: %{{x}}<extra></extra>",
            ),
        ]
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title=TRANSLATIONS["trip_count"][lang],
            yaxis_title="",
            height=max(300, n * 35),
            barmode="stack",
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        )
    )
    return fig


def build_top_stations_map(top_stations_df, selected_index=None, lang="pl"):
    """Build a folium map with top 10 stations as markers. Selected station highlighted."""
    m = folium.Map(
        location=GDANSK_CENTER,
        zoom_start=12,
        tiles="CartoDB positron",
    )
    departures = TRANSLATIONS["departures"][lang]
    arrivals = TRANSLATIONS["arrivals"][lang]

    for i, row in top_stations_df.iterrows():
        is_selected = selected_index is not None and i == selected_index
        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=10 if is_selected else 7,
            color=COLOR_PALETTE["primary"] if is_selected else "#999",
            fill=True,
            fill_color=COLOR_PALETTE["primary"] if is_selected else "#999",
            fill_opacity=0.9 if is_selected else 0.3,
            opacity=0.9 if is_selected else 0.3,
            popup=f"<b>{row['code']}</b><br>{row['address']}<br>{departures}: {int(row['start_count'])}<br>{arrivals}: {int(row['end_count'])}",
        ).add_to(m)

    if selected_index is not None and selected_index < len(top_stations_df):
        sel = top_stations_df.iloc[selected_index]
        m.location = [sel["lat"], sel["lng"]]
        m.zoom_start = 17

    return m


def build_frequency_chart(freq_df, lang="pl"):
    trips_lbl = TRANSLATIONS["trips_label"][lang]
    fig = go.Figure(
        data=go.Bar(
            x=freq_df["label"],
            y=freq_df["trips"],
            marker_color=COLOR_PALETTE["primary"],
            hovertemplate=f"%{{x}}<br>{trips_lbl}: %{{y}}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title="",
            yaxis_title=TRANSLATIONS["trip_count"][lang],
            height=350,
            xaxis={"tickangle": -45, "nticks": 15},
        )
    )
    return fig
