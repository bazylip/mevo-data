FEEDBACK_URL = "https://forms.gle/Nu9awcianscEcfW57"
DISTANCE_FACTOR = 1.3
CO2_PER_KM_CAR = 120  # grams
FUEL_PER_KM = 0.07  # liters
GDANSK_CENTER = [54.372, 18.638]

DAY_NAMES = {
    "pl": ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}

MONTH_NAMES = {
    "pl": {1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień", 5: "Maj", 6: "Czerwiec",
           7: "Lipiec", 8: "Sierpień", 9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"},
    "en": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
           7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
}

MONTH_NAMES_SHORT = {
    "pl": {1: "sty", 2: "lut", 3: "mar", 4: "kwi", 5: "maj", 6: "cze",
           7: "lip", 8: "sie", 9: "wrz", 10: "paź", 11: "lis", 12: "gru"},
    "en": {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
           7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"},
}

# Aliases for backward compatibility
DAY_NAMES_PL = DAY_NAMES["pl"]
MONTH_NAMES_PL = MONTH_NAMES["pl"]
MONTH_NAMES_PL_SHORT = MONTH_NAMES_SHORT["pl"]

TRANSLATIONS = {
    # Upload / Instructions
    "upload_label": {"pl": "Wgraj plik w formacie .zip", "en": "Upload a .zip file"},
    "how_to_download": {"pl": "#### Jak pobrać dane?", "en": "#### How to download your data?"},
    "instr_step1": {
        "pl": '1. Wejdź na <a href="https://rowermevo.pl" target="_blank">rowermevo.pl</a>',
        "en": '1. Go to <a href="https://rowermevo.pl" target="_blank">rowermevo.pl</a>',
    },
    "instr_step2": {
        "pl": "2. Nie pobieraj aplikacji, zamiast tego zaloguj się bezpośrednio na stronie",
        "en": "2. Don\u2019t download the app \u2014 log in directly on the website instead",
    },
    "instr_step3": {
        "pl": "3. Przewiń w dół do sekcji **Twoje dane**",
        "en": "3. Scroll down to the **Your data** section",
    },
    "instr_step4": {
        "pl": "4. Kliknij **Tworzenie plików JSON** aby wygenerować dane",
        "en": "4. Click **Create JSON files** to generate your data",
    },
    "instr_step5": {
        "pl": "5. Pobierz archiwum ZIP z danymi",
        "en": "5. Download the ZIP archive with your data",
    },
    "instr_step6": {
        "pl": "6. Wgraj pobrany plik ZIP powyżej",
        "en": "6. Upload the downloaded ZIP file above",
    },
    # Summary card
    "card_trips": {"pl": "przejazdy", "en": "trips"},
    "card_distance": {"pl": "dystans", "en": "distance"},
    "card_time": {"pl": "czas jazdy", "en": "ride time"},
    "card_stations": {"pl": "stacje", "en": "stations"},
    "card_activity": {"pl": "Aktywność w ostatnim roku", "en": "Activity in the last year"},
    "card_share": {"pl": "Udostępnij", "en": "Share"},
    "card_copied": {"pl": "Skopiowano!", "en": "Copied!"},
    "card_share_text": {
        "pl": "Mam na koncie {km} km na Mevo! Sprawdź swoje wyniki na mevo-wrapped.streamlit.app",
        "en": "I\u2019ve ridden {km} km on Mevo! Check your stats at mevo-wrapped.streamlit.app",
    },
    # Overview metrics
    "total_trips": {"pl": "Liczba przejazdów", "en": "Total trips"},
    "total_distance": {"pl": "Łączny dystans", "en": "Total distance"},
    "total_time": {"pl": "Łączny czas jazdy", "en": "Total ride time"},
    "unique_stations": {"pl": "Unikalne stacje", "en": "Unique stations"},
    "avg_time": {"pl": "Śr. czas przejazdu", "en": "Avg. trip time"},
    "avg_distance": {"pl": "Śr. dystans", "en": "Avg. distance"},
    "days_with_trip": {"pl": "Dni z przejazdem", "en": "Days with a trip"},
    "date_range": {"pl": "Zakres dat", "en": "Date range"},
    # Section headers
    "trip_frequency": {"pl": "Częstotliwość przejazdów", "en": "Trip frequency"},
    "trip_duration_dist": {"pl": "Rozkład czasu podróży", "en": "Trip duration distribution"},
    "when_do_you_ride": {"pl": "Kiedy jeździsz?", "en": "When do you ride?"},
    "station_map": {"pl": "Mapa stacji", "en": "Station map"},
    "top_stations": {"pl": "Najczęściej odwiedzane stacje", "en": "Most visited stations"},
    "fun_stats": {"pl": "Ciekawostki", "en": "Fun stats"},
    # Radio options
    "days": {"pl": "Dni", "en": "Days"},
    "weeks": {"pl": "Tygodnie", "en": "Weeks"},
    "months": {"pl": "Miesiące", "en": "Months"},
    "all_stations": {"pl": "Wszystkie", "en": "All"},
    "start_stations": {"pl": "Stacje startowe", "en": "Start stations"},
    "end_stations": {"pl": "Stacje końcowe", "en": "End stations"},
    "select_station": {"pl": "Wybierz stację", "en": "Select station"},
    # Charts
    "hour": {"pl": "Godzina", "en": "Hour"},
    "day": {"pl": "Dzień", "en": "Day"},
    "trips_label": {"pl": "Podróże", "en": "Trips"},
    "trip_count": {"pl": "Liczba podróży", "en": "Number of trips"},
    "arrivals": {"pl": "Przyjazdy", "en": "Arrivals"},
    "departures": {"pl": "Wyjazdy", "en": "Departures"},
    "time_min": {"pl": "Czas", "en": "Time"},
    "count": {"pl": "Liczba", "en": "Count"},
    "mean_label": {"pl": "Średnia", "en": "Mean"},
    "trip_time_minutes": {"pl": "Czas podróży (minuty)", "en": "Trip duration (minutes)"},
    # Fun stats - Ecology
    "ecology": {"pl": "Ekologia", "en": "Ecology"},
    "co2_saved": {"pl": "CO₂ zaoszczędzone", "en": "CO₂ saved"},
    "co2_tooltip": {
        "pl": "Obliczono na podstawie {km} km przejechanych rowerem zamiast samochodem. Przyjęto średnią emisję samochodu: 120 g CO₂/km.",
        "en": "Calculated based on {km} km cycled instead of driving. Average car emission assumed: 120 g CO₂/km.",
    },
    "fuel_saved": {"pl": "Paliwa zaoszczędzonego", "en": "Fuel saved"},
    "fuel_tooltip": {
        "pl": "Obliczono na podstawie {km} km. Przyjęto średnie spalanie samochodu: 7 l/100 km.",
        "en": "Calculated based on {km} km. Average car consumption assumed: 7 l/100 km.",
    },
    "calories_label": {"pl": "Kalorie", "en": "Calories"},
    "weight_slider": {
        "pl": "Twoja waga (kg) — do obliczenia spalonych kalorii",
        "en": "Your weight (kg) — for calculating burned calories",
    },
    "calories_burned": {"pl": "Spalonych kalorii", "en": "Calories burned"},
    "calories_tooltip": {
        "pl": "Obliczono na podstawie MET=6.8 (umiarkowana jazda na rowerze) × {w} kg × {h} h jazdy.",
        "en": "Calculated using MET=6.8 (moderate cycling) × {w} kg × {h} h of riding.",
    },
    # Fun stats - Records
    "records": {"pl": "Rekordy", "en": "Records"},
    "longest_trip": {"pl": "Najdłuższa podróż", "en": "Longest trip"},
    "trips_in_one_day": {"pl": "Podróży w jeden dzień", "en": "Trips in one day"},
    "longest_streak": {"pl": "Najdłuższa seria", "en": "Longest streak"},
    "days_unit": {"pl": "dni", "en": "days"},
    # Fun stats - Milestones
    "milestones": {"pl": "Kamienie milowe", "en": "Milestones"},
    "first_trip": {"pl": "Pierwsza podróż", "en": "First trip"},
    "hundredth_trip": {"pl": "Setna podróż", "en": "100th trip"},
    "busiest_month": {"pl": "Najbardziej aktywny miesiąc", "en": "Busiest month"},
    "busiest_week": {"pl": "Najbardziej aktywny tydzień", "en": "Busiest week"},
    "trips_unit": {"pl": "przejazdów", "en": "trips"},
    "total_cost": {"pl": "Łączny koszt", "en": "Total cost"},
    # Feedback
    "feedback_button": {"pl": "Podziel się opinią", "en": "Share feedback"},
    # Footer
    "footer_disclaimer": {
        "pl": "⚠️ Dystans jest szacunkowy (odległość w linii prostej × 1,3). "
              "Pominięto {null_end} podróży bez stacji końcowej i {null_start} bez stacji początkowej w obliczeniach dystansu. "
              "Dane pochodzą z eksportu aplikacji Mevo.",
        "en": "⚠️ Distance is approximate (straight-line distance × 1.3). "
              "{null_end} trips without an end station and {null_start} without a start station were excluded from distance calculations. "
              "Data comes from the Mevo app export.",
    },
}

COLOR_PALETTE = {
    "primary": "#F15B4E",
    "accent": "#0B163F",
    "navy": "#0B163F",
    "warm": "#FF6B35",
    "green": "#00E676",
    "purple": "#B388FF",
}

CORAL_RAMP = ["#FFFFFF", "#FDE8E6", "#F9A8A0", "#F15B4E"]

PLOTLY_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#1A1A2E"},
    "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
}
