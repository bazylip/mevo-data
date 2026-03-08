import numpy as np
import folium
from folium.plugins import HeatMap
import plotly.graph_objects as go

from constants import COLOR_PALETTE, DAY_NAMES_PL, GDANSK_CENTER, PLOTLY_LAYOUT_DEFAULTS


def _layout_defaults(**overrides):
    layout = {**PLOTLY_LAYOUT_DEFAULTS, **overrides}
    return layout


def build_station_heatmap(df, mode="start"):
    """Build a folium heatmap showing start or end station density."""
    m = folium.Map(
        location=GDANSK_CENTER,
        zoom_start=12,
        tiles="CartoDB positron",
    )

    heat_data = []
    if mode == "start":
        subset = df[df["has_start_station"]]
        for _, row in subset.iterrows():
            heat_data.append([row["start_lat"], row["start_lng"]])
    else:
        subset = df[df["has_end_station"]]
        for _, row in subset.iterrows():
            heat_data.append([row["end_lat"], row["end_lng"]])

    if heat_data:
        HeatMap(heat_data, radius=18, blur=12, max_zoom=15).add_to(m)

    return m


def build_day_hour_heatmap(matrix):
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(range(24)),
            y=DAY_NAMES_PL,
            colorscale="Viridis",
            hovertemplate="Dzień: %{y}<br>Godzina: %{x}:00<br>Podróże: %{z}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title="Godzina",
            yaxis_title="",
            height=350,
            yaxis={"autorange": "reversed"},
            xaxis={"dtick": 1},
        )
    )
    return fig


def build_duration_histogram(durations_minutes):
    mean_val = durations_minutes.mean()

    fig = go.Figure(
        data=go.Histogram(
            x=durations_minutes,
            nbinsx=25,
            marker_color=COLOR_PALETTE["primary"],
            hovertemplate="Czas: %{x:.0f} min<br>Liczba: %{y}<extra></extra>",
        )
    )
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color=COLOR_PALETTE["accent"],
        annotation_text=f"Średnia: {mean_val:.1f} min",
        annotation_font_color=COLOR_PALETTE["accent"],
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title="Czas podróży (minuty)",
            yaxis_title="Liczba podróży",
            height=350,
        )
    )
    return fig


def build_top_stations_chart(station_df, n=10):
    top = station_df.head(n).iloc[::-1]
    labels = [f"{code} — {addr[:30]}" for code, addr in zip(top["code"], top["address"])]

    fig = go.Figure(
        data=go.Bar(
            x=top["total_count"],
            y=labels,
            orientation="h",
            marker_color=COLOR_PALETTE["primary"],
            hovertemplate="%{y}<br>Podróże: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title="Liczba podróży",
            yaxis_title="",
            height=max(300, n * 35),
        )
    )
    return fig


def build_frequency_chart(freq_df):
    fig = go.Figure(
        data=go.Bar(
            x=freq_df["label"],
            y=freq_df["trips"],
            marker_color=COLOR_PALETTE["primary"],
            hovertemplate="%{x}<br>Podróże: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        **_layout_defaults(
            xaxis_title="",
            yaxis_title="Liczba podróży",
            height=350,
            xaxis={"tickangle": -45},
        )
    )
    return fig
