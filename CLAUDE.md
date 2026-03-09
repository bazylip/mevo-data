# Mevo Wrapped

Streamlit dashboard for visualizing personal Mevo (Gdańsk city bike) trip data. Polish UI, dark theme. Users upload their `mevo.zip` export and get stats, charts, and maps.

## Project Structure

```
app.py                  # Main Streamlit app — layout, sections, rendering
data_processing.py      # ZIP parsing, DataFrame creation, all metric computations (no Streamlit imports)
charts.py               # Plotly chart builders + Folium heatmap map builder
constants.py            # Polish labels, color palette, conversion factors, Plotly defaults
requirements.txt        # Dependencies
.streamlit/config.toml  # Dark theme config
```

## Data Flow

`mevo.zip` → `parse_zip()` → DataFrame → `compute_*()` functions → `build_*()` chart builders → `st.plotly_chart()` / `st_folium()`

## Key Data Details

- Source: `mevo.zip` containing 5 JSON files; **only `trips.json` is used**
- Each trip has: `_id`, `_tripStarted`, `_tripEnded`, `_tripDuration`, `_startStation`, `_endStation`
- Station objects have: `_id`, `_title` (code like "GDA066"), `_subtitle` (address), `_coords` (lat/lng)
- **25 trips have null `_startStation`**, **10 trips have null `_endStation`** — handled throughout
- Distance: haversine × 1.3 factor (no routing API), only computed when both stations present

## Dashboard Sections (top to bottom)

1. Instructions (shown before upload, hidden after)
2. Shareable summary card — 9:16 floating white card with 2×2 stats grid + GitHub-style activity heatmap (last 12 months, green ramp). Download (html2canvas PNG) + Share (Web Share API) buttons below
3. Summary stats: 2 rows × 4 metrics (trips, distance, time, stations / avg time, avg dist, days, date range)
3. Częstotliwość przejazdów — bar chart with day/week/month radio toggle
4. Mapa stacji — folium heatmap with start/end station radio toggle
5. Najczęściej odwiedzane stacje — horizontal bar chart + clickable popover buttons with mini maps
6. Rozkład czasu podróży — duration histogram with mean line
7. Kiedy jeździsz? — day×hour heatmap (Polish day names)
8. Ciekawostki — 3 columns: Ekologia (CO₂, fuel with hover tooltips), Rekordy (longest trip, most trips/day, streak), Kamienie milowe (first/100th trip, busiest month/week) + calorie calculator with weight slider
9. Footer with distance approximation disclaimer

## Design Decisions

- All Plotly charts use `config={"staticPlot": True}` to prevent scroll hijacking on mobile
- Folium maps use `CartoDB positron` (light) tiles
- Popover width forced via CSS: `div[data-baseweb="popover"] > div { min-width: 520px }`
- `data_processing.py` has zero Streamlit imports — pure Python + Pandas for testability
- Calories use MET formula (MET=6.8 × weight × hours) with user-adjustable weight slider
- CO₂/fuel tooltips explain calculation methodology on hover

## Running

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

## Conventions

- Polish UI text throughout
- Conventional commits (feat/fix/chore)
- Distances formatted as "X.Y km"
- Dates formatted as "DD.MM.YYYY"
