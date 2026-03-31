#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py  -  Streamlit frontend dla radar percentylowego
Uruchomienie: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.lines
from mplsoccer import PyPizza
import urllib.request
import tempfile
import os
import re as _re
import io
import unicodedata
import plotly.graph_objects as go

# =====================================================================
#  KONFIGURACJA
# =====================================================================
MAIN_APP_DIR = 'Main App'
LOGO_CSV     = 'Wyscout_Logo_Dict.csv'
MIN_MINUTES_DEFAULT = 900
MIN_GROUP_SIZE_WARNING = 5

# =====================================================================
#  CZCIONKA - Poppins
# =====================================================================
def get_font(weight='normal', size=10):
    try:
        fp = fm.FontProperties(family='Poppins', weight=weight, size=size)
        fm.findfont(fp, fallback_to_default=False)
        return fp
    except Exception:
        return fm.FontProperties(family='DejaVu Sans', weight=weight, size=size)

# =====================================================================
#  MAPPINGI STATYSTYK
# =====================================================================
MAPPING = {
    "Non-penalty goals per 90":             "Non-Pen Goals",
    "npxG per 90":                          "npxG",
    "Goal conversion, %":                   "Goals/Shot on Target %",
    "Shots per 90":                         "Shots",
    "npxG per shot":                        "npxG",
    "Touches in box per 90":               "Touches in Pen Box",
    "xA per 90":                            "xA",
    "Assists per 90":                       "Assists",
    "Second assists per 90":               "Second Assists",
    "Third assists per 90":                "Third Assists",
    "Smart passes per 90":                 "Smart Passes",
    "Shot assists per 90":                 "Shot Assists",
    "Accurate passes, %":                  "Pass %",
    "Accurate short / medium passes, %":   "Short & Med Pass %",
    "Accurate long passes, %":             "Long Pass %",
    "Progressive passes per 90":           "Prog Passes",
    "Progressive runs per 90":             "Prog Carries",
    "Successful dribbles, %":              "Successful Dribbles %",
    "Accelerations per 90":               "Acceleration with Ball",
    "Aerial duels won, %":                 "Aerial Win %",
    "Successful defensive actions per 90": "Def Actions",
    "pAdj Tkl+Int per 90":                "pAdj Tkl+Int",
}

GK_MAPPING = {
    "Shots against per 90":    "Shots Against",
    "Conceded goals per 90":   "Goals Conceded",
    "Save rate, %":            "Save %",
    "Prevented goals per 90":  "Prevented Goals",
    "Exits per 90":            "Exits",
    "Accurate long passes, %": "Long Pass %",
    "Passes per 90":           "Passes",
}

MAPPING2 = {
    "Aerial duels won, %":                  "Aerial Win %",
    "_pAdj_TklInt":                         "Tackles & Int\n(pAdj)",
    "Progressive passes per 90":            "Prog. Passes",
    "Progressive runs per 90":              "Prog. Carries",
    "Accelerations per 90":                 "Acceleration\nwith Ball",
    "Successful dribbles, %":               "Dribble\nSuccess %",
    "Touches in box per 90":               "Touches in\nPen Box",
    "Shots per 90":                         "Shots",
    "_npxG_per_shot":                       "npxG\nper Shot",
    "Goal conversion, %":                   "Goals/Shot on\nTarget %",
    "Non-penalty goals per 90":             "Non-Pen Goals",
    "xG per 90":                            "npxG",
    "Smart passes per 90":                  "Smart Passes",
    "Second assists per 90":               "Second Assists",
    "Assists per 90":                       "Assists",
    "xA per 90":                            "Expected\nAssists (xA)",
    "Shot assists per 90":                  "Shot Assists",
    "Accurate crosses, %":                  "Cross\nCompletion %",
    "Accurate smart passes, %":             "Smart Pass %",
    "Accurate long passes, %":              "Long Pass %",
    "Accurate short / medium passes, %":    "Short & Med\nPass %",
}

GK_MAPPING2 = {
    "Shots against per 90":             "Shots Against",
    "Conceded goals per 90":            "Goals Conceded",
    "Save rate, %":                     "Save %",
    "_goals_prevented_pct":             "Goals\nPrevented %",
    "Prevented goals per 90":           "Prevented\nGoals",
    "Exits per 90":                     "Coming\nOff Line",
    "Accurate long passes, %":          "Long Pass\nCmp %",
    "Accurate forward passes, %":       "% Passes\nBeing Lateral",
    "Accurate short / medium passes, %":"% Passes\nBeing Short",
    "Passes per 90":                    "Passes",
    "Received passes per 90":           "Received\nPasses",
}

CB_POSITIONS = {'CB', 'LCB', 'RCB'}

CB_MAPPING2 = {
    "Fouls suffered per 90":               "Fouls Drawn",
    "_cards_per_90":                       "Cards",
    "Fouls per 90":                        "Fouls",
    "xA per 90":                           "Expected\nAssists",
    "Accelerations per 90":                "Acceleration\nwith Ball",
    "Successful dribbles, %":              "Dribble\nSuccess %",
    "Progressive runs per 90":             "Prog.\nCarries",
    "Progressive passes per 90":           "Prog.\nPasses",
    "_assists_2nd3rd":                     "Assists &\n2nd/3rd Assists",
    "Accurate long passes, %":             "Long Pass %",
    "Aerial duels won, %":                 "Aerial Win %",
    "Aerial duels per 90":                 "Aerial Duels\nWon",
    "PAdj Interceptions":                  "Interceptions\n(pAdj)",
    "Shots blocked per 90":                "Shot Blocks",
    "Defensive duels won, %":              "Defensive\nDuels Won %",
    "PAdj Sliding tackles":                "Tackles\n(pAdj)",
    "Successful defensive actions per 90": "Defensive\nActions",
}

FB_POSITIONS = {'LB', 'RB', 'LWB', 'RWB', 'WB'}

FB_MAPPING2 = {
    "Fouls suffered per 90":               "Fouls Drawn",
    "_cards_per_90":                       "Cards",
    "Fouls per 90":                        "Fouls",
    "xA per 90":                           "Expected\nAssists",
    "Accelerations per 90":                "Acceleration\nwith Ball",
    "Successful dribbles, %":              "Dribble\nSuccess %",
    "Progressive runs per 90":             "Prog.\nCarries",
    "Progressive passes per 90":           "Prog.\nPasses",
    "_assists_2nd3rd":                     "Assists &\n2nd/3rd Assists",
    "Accurate long passes, %":             "Long Pass %",
    "Crosses per 90":                      "Crosses",
    "Accurate crosses, %":                 "Cross\nCompletion %",
    "Aerial duels won, %":                 "Aerial Win %",
    "Aerial duels per 90":                 "Aerial Duels\nWon",
    "PAdj Interceptions":                  "Interceptions\n(pAdj)",
    "Shots blocked per 90":                "Shot Blocks",
    "Defensive duels won, %":              "Defensive\nDuels Won %",
    "PAdj Sliding tackles":                "Tackles\n(pAdj)",
    "Successful defensive actions per 90": "Defensive\nActions",
}

# =====================================================================
#  STAT CATEGORIES FOR COMPARISON TAB
# =====================================================================
COMPARE_CATEGORIES = {
    "📊 Overview": [
        "Goals per 90", "xG per 90", "Assists per 90", "xA per 90",
        "Passes per 90", "Accurate passes, %",
        "Progressive passes per 90", "Progressive runs per 90",
        "Successful dribbles, %", "Aerial duels won, %",
        "Successful defensive actions per 90", "Duels won, %",
    ],
    "⚽ Goalscoring": [
        "Goals per 90", "Non-penalty goals per 90", "xG per 90",
        "Shots per 90", "Shots on target, %", "Goal conversion, %",
        "Head goals per 90", "Touches in box per 90",
        "Successful attacking actions per 90",
    ],
    "🎯 Chance Creation": [
        "xA per 90", "Assists per 90", "Shot assists per 90",
        "Key passes per 90", "Second assists per 90", "Third assists per 90",
        "Deep completions per 90", "Passes to penalty area per 90",
        "Accurate passes to penalty area, %",
    ],
    "📤 Passing": [
        "Passes per 90", "Accurate passes, %",
        "Forward passes per 90", "Accurate forward passes, %",
        "Short / medium passes per 90", "Accurate short / medium passes, %",
        "Long passes per 90", "Accurate long passes, %",
        "Progressive passes per 90", "Accurate progressive passes, %",
        "Passes to final third per 90", "Accurate passes to final third, %",
        "Through passes per 90", "Smart passes per 90",
        "Average pass length, m",
    ],
    "🏃 Carrying & Dribbling": [
        "Progressive runs per 90", "Accelerations per 90",
        "Dribbles per 90", "Successful dribbles, %",
        "Offensive duels per 90", "Offensive duels won, %",
        "Fouls suffered per 90",
    ],
    "🔀 Crossing": [
        "Crosses per 90", "Accurate crosses, %",
        "Crosses from left flank per 90", "Accurate crosses from left flank, %",
        "Crosses from right flank per 90", "Accurate crosses from right flank, %",
        "Deep completed crosses per 90",
    ],
    "🛡️ Defending": [
        "Successful defensive actions per 90",
        "Defensive duels per 90", "Defensive duels won, %",
        "PAdj Interceptions", "PAdj Sliding tackles",
        "Shots blocked per 90", "Fouls per 90",
        "Yellow cards per 90", "Red cards per 90",
    ],
    "🤼 Duels & Aerial": [
        "Duels per 90", "Duels won, %",
        "Aerial duels per 90", "Aerial duels won, %",
        "Offensive duels per 90", "Offensive duels won, %",
        "Defensive duels per 90", "Defensive duels won, %",
    ],
    "🧤 Goalkeeping": [
        "Save rate, %", "Conceded goals per 90", "Shots against per 90",
        "Prevented goals per 90", "xG against per 90",
        "Exits per 90", "Back passes received as GK per 90",
        "Accurate long passes, %", "Passes per 90",
    ],
}

# =====================================================================
#  STYL
# =====================================================================
BG_DARK        = "#0d1117"   # Streamlit UI  (dark)
BG_PIZZA       = "#FFFFFF"   # Radar card    (white)
LINE_COLOR     = "#E5E5E5"   # grid lines    (light grey)
OUTER_CIRCLE   = "#BBBBBB"   # outer ring
TEXT_PRIMARY   = "#1A1A1A"   # dark text on white radar
TEXT_SECONDARY = "#555555"

SLICE_COLORS = {
    'elite':   '#1D3F6E',   # dark navy   ≥ 90
    'above':   '#2D7A4F',   # forest green 65-89
    'average': '#E07B2A',   # warm orange  34-64
    'below':   '#B83232',   # deep red     < 34
}

def slice_color(v):
    if pd.isna(v):    return LINE_COLOR
    if v >= 90:       return SLICE_COLORS['elite']
    if v >= 65:       return SLICE_COLORS['above']
    if v >= 34:       return SLICE_COLORS['average']
    return SLICE_COLORS['below']

def wrap_label(label, max_len=14):
    if '\n' in label:
        return label
    if len(label) <= max_len:
        return label
    words = label.split()
    lines, cur = [], ''
    for w in words:
        if cur and len(cur) + len(w) + 1 > max_len:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur: lines.append(cur)
    return '\n'.join(lines)

# =====================================================================
#  NORMALIZACJA SEZONOW
# =====================================================================
def _normalize_season(raw):
    raw = raw.strip()
    m = _re.match(r'^(\d{2})-(\d{2})$', raw)
    if m: return raw
    m = _re.match(r'^(\d{4})[-/](\d{2})$', raw)
    if m: return m.group(1)[2:] + '-' + m.group(2)
    m = _re.match(r'^(\d{4})$', raw)
    if m:
        y = int(m.group(1))
        return f"{y%100:02d}-{(y+1)%100:02d}"
    return raw

def _extract_season(fname):
    base = os.path.splitext(fname)[0]
    m = _re.search(r'(\d{4}[-/]\d{2}|\d{2}-\d{2}|\d{4})$', base.strip())
    return _normalize_season(m.group(1)) if m else None

def _normalize_league_name(name: str) -> str:
    """
    Ujednolicenie nazwy ligi:
    - NFC unicode (ã jako jeden znak, nie a + combining tilde)
    - strip + normalizacja whitespace
    Nie usuwa akcentow — tylko zapewnia ze ta sama litera
    zapisana roznym encodingiem daje identyczny string.
    """
    name = unicodedata.normalize('NFC', name)
    name = ' '.join(name.split())
    return name

def _league_key(name: str) -> str:
    """
    Klucz do deduplikacji — lowercase + bez akcentow.
    Dzieki temu 'Brasileirao' i 'Brasileirao' (z ã) to ta sama liga.
    """
    nfc = unicodedata.normalize('NFC', name.strip().lower())
    return unicodedata.normalize('NFKD', nfc).encode('ascii', 'ignore').decode()

def _extract_league(fname):
    base = os.path.splitext(fname)[0]
    raw = _re.sub(r'\s*(\d{4}[-/]\d{2}|\d{2}-\d{2}|\d{4})\s*$', '', base).strip()
    return _normalize_league_name(raw)

def _season_display(s):
    m = _re.match(r'^(\d{2})-(\d{2})$', s)
    if m:
        y1 = int(m.group(1))
        cent = 19 if y1 > 50 else 20
        return f"{cent}{m.group(1)}/{m.group(2)}"
    return s

# =====================================================================
#  SKANOWANIE FOLDERU
# =====================================================================
@st.cache_data
def scan_main_app(folder):
    if not os.path.isdir(folder):
        return {}
    seasons = {}
    for fname in os.listdir(folder):
        if not fname.lower().endswith('.csv'):
            continue
        season = _extract_season(fname)
        if season is None:
            continue
        seasons.setdefault(season, []).append(os.path.join(folder, fname))
    return seasons

@st.cache_data
def load_season(folder, season_key):
    seasons = scan_main_app(folder)
    if season_key not in seasons:
        return pd.DataFrame()

    frames = []
    for fpath in sorted(seasons[season_key]):
        fname = os.path.basename(fpath)
        league_name = _extract_league(fname)
        try:
            df_tmp = pd.read_csv(fpath)
            df_tmp.columns = df_tmp.columns.str.strip()
            if 'Unnamed: 0' in df_tmp.columns:
                df_tmp = df_tmp.drop(columns=['Unnamed: 0'])
            df_tmp['Competition'] = league_name
            frames.append(df_tmp)
        except Exception as e:
            st.warning(f"Blad wczytywania {fname}: {e}")

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df.columns = df.columns.str.strip()

    if 'Minutes played' not in df.columns:
        return df

    # Kolumny obliczane
    extras = {}
    if 'PAdj Sliding tackles' in df.columns and 'PAdj Interceptions' in df.columns:
        extras['_pAdj_TklInt'] = (
            pd.to_numeric(df['PAdj Sliding tackles'], errors='coerce').fillna(0) +
            pd.to_numeric(df['PAdj Interceptions'],   errors='coerce').fillna(0)
        )
    if 'xG per 90' in df.columns and 'Shots per 90' in df.columns:
        shots = pd.to_numeric(df['Shots per 90'], errors='coerce').replace(0, np.nan)
        xg    = pd.to_numeric(df['xG per 90'],    errors='coerce')
        extras['_npxG_per_shot'] = xg / shots
    if 'Prevented goals' in df.columns and 'xG against' in df.columns:
        xga = pd.to_numeric(df['xG against'], errors='coerce').replace(0, np.nan)
        pg  = pd.to_numeric(df['Prevented goals'], errors='coerce')
        extras['_goals_prevented_pct'] = pg / xga * 100
    if 'Yellow cards per 90' in df.columns and 'Red cards per 90' in df.columns:
        extras['_cards_per_90'] = (
            pd.to_numeric(df['Yellow cards per 90'], errors='coerce').fillna(0) +
            pd.to_numeric(df['Red cards per 90'],    errors='coerce').fillna(0)
        )
    if 'Assists per 90' in df.columns:
        a  = pd.to_numeric(df['Assists per 90'],        errors='coerce').fillna(0)
        a2 = pd.to_numeric(df.get('Second assists per 90', 0), errors='coerce').fillna(0)
        a3 = pd.to_numeric(df.get('Third assists per 90',  0), errors='coerce').fillna(0)
        extras['_assists_2nd3rd'] = a + a2 + a3
    if extras:
        df = pd.concat([df, pd.DataFrame(extras, index=df.index)], axis=1)

    return df

# =====================================================================
#  GRUPY POZYCJI
# =====================================================================
HARDCODED_GROUPS = {
    'GK':    (['GK'],                                               'Goalkeepers'),
    'CF':    (['CF'],                                               'CF'),
    'LW':    (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'RW':    (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'LWF':   (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'RWF':   (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'LAMF':  (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'RAMF':  (['LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'],         'Wingers'),
    'AMF':   (['AMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'],          'Attacking Midfielders'),
    'LCMF':  (['LCMF', 'RCMF', 'LCMF3', 'RCMF3', 'AMF', 'DMF', 'LDMF', 'RDMF'], 'Central Midfielders'),
    'RCMF':  (['LCMF', 'RCMF', 'LCMF3', 'RCMF3', 'AMF', 'DMF', 'LDMF', 'RDMF'], 'Central Midfielders'),
    'LCMF3': (['LCMF', 'RCMF', 'LCMF3', 'RCMF3', 'AMF', 'DMF', 'LDMF', 'RDMF'], 'Central Midfielders'),
    'RCMF3': (['LCMF', 'RCMF', 'LCMF3', 'RCMF3', 'AMF', 'DMF', 'LDMF', 'RDMF'], 'Central Midfielders'),
    'DMF':   (['DMF', 'LDMF', 'RDMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'], 'Defensive Midfielders'),
    'LDMF':  (['DMF', 'LDMF', 'RDMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'], 'Defensive Midfielders'),
    'RDMF':  (['DMF', 'LDMF', 'RDMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'], 'Defensive Midfielders'),
    'LB':    (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'RB':    (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'LWB':   (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'RWB':   (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'LB5':   (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'RB5':   (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'LWB5':  (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'RWB5':  (['LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'], 'FBs & WBs'),
    'CB':    (['CB', 'LCB', 'RCB', 'LCB3', 'RCB3'], 'Center Backs'),
    'LCB':   (['CB', 'LCB', 'RCB', 'LCB3', 'RCB3'], 'Center Backs'),
    'RCB':   (['CB', 'LCB', 'RCB', 'LCB3', 'RCB3'], 'Center Backs'),
    'LCB3':  (['CB', 'LCB', 'RCB', 'LCB3', 'RCB3'], 'Center Backs'),
    'RCB3':  (['CB', 'LCB', 'RCB', 'LCB3', 'RCB3'], 'Center Backs'),
}

def get_comparison_positions(position):
    if position in HARDCODED_GROUPS:
        return HARDCODED_GROUPS[position]
    return [position], position

def build_group(df, league, position, min_minutes):
    league_col = next(
        (c for c in ['League', 'league', 'competition', 'Competition'] if c in df.columns), None
    )
    pos_col = next(
        (c for c in ['Primary position', 'Position', 'position', 'Pos'] if c in df.columns), None
    )
    if league_col is None or pos_col is None:
        return pd.DataFrame(), league_col, pos_col, df, pd.Series(dtype=bool), position

    df = df.copy()
    df[league_col] = df[league_col].astype(str).str.strip()
    df['_main_pos'] = df[pos_col].astype(str).str.split(',').str[0].str.strip()
    df['_minutes']  = pd.to_numeric(df['Minutes played'], errors='coerce').fillna(0)

    mask_league  = df[league_col].astype(str).apply(_league_key) == _league_key(league)
    comp_positions, comp_group = get_comparison_positions(position)
    mask_pos     = df['_main_pos'].isin(comp_positions)
    mask_minutes = df['_minutes'] >= min_minutes

    return df[mask_league & mask_pos & mask_minutes].copy(), league_col, pos_col, df, mask_league, comp_group

# =====================================================================
#  PERCENTYLE
# =====================================================================
LOWER_IS_BETTER = {
    'Conceded goals per 90',
    'Shots against per 90',
    'Fouls per 90',
    '_cards_per_90',
}

def compute_percentiles(group, stat_cols):
    result = group.copy()
    for col in stat_cols:
        series = pd.to_numeric(result[col], errors='coerce')
        valid_n = int(series.notna().sum())
        if valid_n == 0:
            result[col + '_pct'] = np.nan
            continue
        if col in LOWER_IS_BETTER:
            def _pct(x, s=series, n=valid_n):
                if pd.isna(x): return np.nan
                return int((s >= x).sum()) / n * 100.0
        else:
            def _pct(x, s=series, n=valid_n):
                if pd.isna(x): return np.nan
                return int((s <= x).sum()) / n * 100.0
        result[col + '_pct'] = series.apply(_pct)
    return result

# =====================================================================
#  LOGO
# =====================================================================
@st.cache_data
def load_logo_dict(logo_csv):
    if not os.path.exists(logo_csv):
        return {}
    try:
        df = pd.read_csv(logo_csv)
        df.columns = df.columns.str.strip()
        df['Team'] = df['Team'].str.strip()
        url_col = [c for c in df.columns if 'logo' in c.lower() or 'url' in c.lower()]
        if not url_col:
            return {}
        return dict(zip(df['Team'], df[url_col[0]]))
    except Exception:
        return {}

def fetch_logo(url, size=0.30):
    if not url or not isinstance(url, str):
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
        suffix = '.png' if 'png' in url.lower() else '.jpg'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        img = mpimg.imread(tmp_path)
        os.unlink(tmp_path)
        oi = OffsetImage(img, zoom=size, dpi_cor=False)
        oi.image.axes = None
        return oi
    except Exception:
        return None

def place_logo_in_center(ax, logo_img):
    if logo_img is None:
        return
    try:
        logo_img.set_zoom(1.1)
        ab = AnnotationBbox(
            logo_img,
            (0, -38),
            frameon=False,
            pad=0,
            zorder=10,
        )
        ax.add_artist(ab)
    except Exception:
        pass

# =====================================================================
#  RYSOWANIE RADARU - zwraca Figure zamiast plt.show()
# =====================================================================
def draw_radar(player, full_name, player_minutes, team, pct_vals, labels, n,
               league, position, comp_group, min_min, logo_img):

    fp_label   = get_font(weight='medium',  size=7.0)
    fp_value   = get_font(weight='bold',    size=7.5)
    fp_title   = get_font(weight='bold',    size=14)
    fp_sub     = get_font(weight='normal',  size=7.5)
    fp_legend  = get_font(weight='normal',  size=7)
    fp_legbold = get_font(weight='bold',    size=7.5)

    wrapped_labels = [wrap_label(l) for l in labels]
    colors    = [slice_color(v) for v in pct_vals]
    plot_vals = [0.0 if pd.isna(v) else round(v, 1) for v in pct_vals]

    baker = PyPizza(
        params=wrapped_labels,
        background_color=BG_PIZZA,
        straight_line_color="#FFFFFF",
        straight_line_lw=1.2,
        last_circle_color=OUTER_CIRCLE,
        last_circle_lw=1.5,
        other_circle_color=LINE_COLOR,
        other_circle_lw=0.8,
        inner_circle_size=38,
    )

    # Compact figure — fits in one viewport without scrolling
    fig, ax = baker.make_pizza(
        plot_vals,
        figsize=(7.0, 7.8),
        color_blank_space="same",
        blank_alpha=0.18,          # soft visible ring on white bg
        kwargs_slices=dict(
            facecolor=colors,
            edgecolor="#FFFFFF",
            linewidth=1.5,
            alpha=1.0,
            zorder=2,
        ),
        kwargs_params=dict(
            color=TEXT_PRIMARY,
            fontsize=7.0,
            fontproperties=fp_label,
            va="center",
            linespacing=1.3,
        ),
        kwargs_values=dict(
            color="#FFFFFF",
            fontsize=7.5,
            fontproperties=fp_value,
            zorder=3,
            bbox=dict(
                edgecolor="none",
                facecolor="#E07B2A",  # placeholder, overridden per slice below
                boxstyle="round,pad=0.25",
                alpha=1.0,
            ),
        ),
    )

    # White figure background (radar "card" look)
    fig.patch.set_facecolor("#FFFFFF")

    # Per-slice colored value boxes
    for i, text in enumerate(baker.get_value_texts()):
        if pd.isna(pct_vals[i]):
            text.set_text("N/A")
            text.set_fontsize(6)
        else:
            text.set_text("{:.0f}".format(pct_vals[i]))
        text.set_fontproperties(fp_value)
        text.set_color("#FFFFFF")
        text.set_bbox(dict(
            edgecolor="none",
            facecolor=colors[i],
            boxstyle="round,pad=0.25",
            alpha=1.0,
        ))

    if logo_img is not None:
        place_logo_in_center(ax, logo_img)
    else:
        ax.text(0, 0, "⚽",
                ha="center", va="center",
                color=TEXT_SECONDARY,
                fontproperties=get_font(weight='normal', size=10),
                zorder=6)

    # ── Title & subtitle ─────────────────────────────────────────────
    # Extra top padding so the top pizza label doesn't hit the subtitle
    fig.text(0.5, 0.975, full_name, ha="center", va="top",
             color=TEXT_PRIMARY, fontproperties=fp_title)

    display_pos = position if position == comp_group else "{} ({})".format(position, comp_group)
    subtitle = "{league}   ·   {pos}   ·   {n} players   ·   {pm} min".format(
        league=league, pos=display_pos, n=n,
        pm=int(player_minutes) if player_minutes is not None else min_min
    )
    if team:
        subtitle = team + "   ·   " + subtitle
    fig.text(0.5, 0.942, subtitle, ha="center", va="top",
             color=TEXT_SECONDARY, fontproperties=fp_sub)

    fig.add_artist(matplotlib.lines.Line2D(
        [0.10, 0.90], [0.930, 0.930],
        transform=fig.transFigure,
        color="#DDDDDD", linewidth=0.7,
    ))

    # ── Legend — horizontal row at bottom ───────────────────────────
    legend_items = [
        (SLICE_COLORS['elite'],   'Elite',         '>= 90'),
        (SLICE_COLORS['above'],   'Above Average', '65–89'),
        (SLICE_COLORS['average'], 'Average',       '34–64'),
        (SLICE_COLORS['below'],   'Below Average', '< 34'),
    ]

    n_items = len(legend_items)
    item_w  = 0.23
    start_x = 0.5 - (n_items * item_w) / 2 + 0.01
    sq_w, sq_h = 0.018, 0.022
    y_sq    = 0.035
    y_bold  = 0.050
    y_light = 0.027

    for i, (color, bold_text, light_text) in enumerate(legend_items):
        x = start_x + i * item_w
        sq = mpatches.FancyBboxPatch(
            (x, y_sq), sq_w, sq_h,
            boxstyle="round,pad=0.002",
            facecolor=color, edgecolor="none",
            transform=fig.transFigure, zorder=5,
        )
        fig.add_artist(sq)
        fig.text(x + sq_w + 0.010, y_bold, bold_text,
                 ha="left", va="center", color=TEXT_PRIMARY,
                 fontproperties=fp_legbold, transform=fig.transFigure)
        fig.text(x + sq_w + 0.010, y_light, light_text,
                 ha="left", va="center", color=TEXT_SECONDARY,
                 fontproperties=fp_legend, transform=fig.transFigure)

    # Leave 13% at top for title+subtitle gap, 9% at bottom for legend
    plt.tight_layout(rect=[0.02, 0.08, 0.98, 0.875])

    return fig

# =====================================================================
#  STREAMLIT UI
# =====================================================================
st.set_page_config(
    page_title="Football Scout Radar",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styl - ciemne tlo UI, bialy radar
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e8edf2; }
    .stSidebar { background-color: #111820; border-right: 1px solid #1e2a38; }
    .stSidebar .stSelectbox label,
    .stSidebar .stSlider label,
    .stSidebar .stNumberInput label { color: #8899aa; font-size: 13px; }
    h1, h2, h3 { color: #e8edf2; }
    .stButton > button {
        background-color: #1D3F6E;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-size: 15px;
        width: 100%;
    }
    .stButton > button:hover { background-color: #163060; }
</style>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────
tab_radar, tab_compare, tab_similar, tab_scatter, tab_search = st.tabs([
    "📊 Percentile Radar", "⚖️ Player Comparison", "🔍 Player Similarity",
    "📈 Scatter Plot", "🔎 Player Search"
])

# =====================================================================
#  SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("## 🔧 Radar Filters")

    if not os.path.isdir(MAIN_APP_DIR):
        st.error(f"❌ Folder **'{MAIN_APP_DIR}'** not found.")
        st.stop()

    seasons = scan_main_app(MAIN_APP_DIR)
    if not seasons:
        st.error(f"❌ No CSV files found in **'{MAIN_APP_DIR}'**.")
        st.stop()

    sorted_seasons   = sorted(seasons.keys(), reverse=True)
    season_labels    = [_season_display(k) for k in sorted_seasons]
    sel_season_label = st.selectbox("Season", season_labels)
    season_key       = sorted_seasons[season_labels.index(sel_season_label)]

    df_raw = load_season(MAIN_APP_DIR, season_key)
    if df_raw.empty:
        st.error("No data for selected season.")
        st.stop()

    league_col = next(
        (c for c in ['Competition', 'League', 'league', 'competition'] if c in df_raw.columns), None
    )
    if league_col is None:
        st.error("No league column found.")
        st.stop()

    # Deduplikacja przez klucz bez akcentow (np. Brasileirao == Brasileirao z akcentem)
    _seen_keys = {}
    for _lg in sorted(df_raw[league_col].dropna().astype(str).str.strip().unique().tolist()):
        _k = _league_key(_lg)
        if _k not in _seen_keys:
            _seen_keys[_k] = _lg
    available_leagues = sorted(_seen_keys.values())
    selected_league   = st.selectbox("League", available_leagues)

    min_minutes = st.number_input(
        "Min. minutes", min_value=0, max_value=5000,
        value=MIN_MINUTES_DEFAULT, step=100
    )

    pos_col     = next(
        (c for c in ['Primary position', 'Position', 'position', 'Pos'] if c in df_raw.columns), None
    )
    df_league   = df_raw[df_raw[league_col].astype(str).apply(_league_key) == _league_key(selected_league)].copy()
    df_league['_main_pos'] = df_league[pos_col].astype(str).str.split(',').str[0].str.strip()
    df_league['_minutes']  = pd.to_numeric(df_league['Minutes played'], errors='coerce').fillna(0)
    df_eligible = df_league[df_league['_minutes'] >= min_minutes]

    if df_eligible.empty:
        st.warning("No players meet the minimum minutes criteria.")
        st.stop()

    has_fullname = 'Full name' in df_eligible.columns
    name_col     = 'Full name' if has_fullname else 'Player'
    _pnames      = df_eligible.sort_values('Minutes played', ascending=False)[name_col].dropna()
    player_names_unique = list(dict.fromkeys(_pnames.tolist()))

    selected_player = st.selectbox("Player", player_names_unique)

    player_row_raw = df_eligible[df_eligible[name_col] == selected_player]
    if player_row_raw.empty:
        player_row_raw = df_eligible[df_eligible[name_col].str.lower() == selected_player.lower()]
    if player_row_raw.empty:
        st.error("Player not found.")
        st.stop()

    selected_position          = str(player_row_raw.iloc[0]['_main_pos'])
    comp_positions, comp_group = get_comparison_positions(selected_position)
    group, lc, pc, df_full, mask_l, comp_group = build_group(
        df_raw, selected_league, selected_position, min_minutes
    )
    n_players = len(group)
    st.markdown(f"**Position:** `{selected_position}` → *{comp_group}*")
    st.markdown(f"**Players in group:** `{n_players}`")
    if n_players < MIN_GROUP_SIZE_WARNING:
        st.warning(f"⚠️ Very small group ({n_players} players).")

    st.markdown("---")
    generate_btn = st.button("🎯 Generate Radar")


# =====================================================================
#  RADAR TAB
# =====================================================================
with tab_radar:
    st.title("⚽ Percentile Radar")
    st.markdown(
        "<p style='color:#8899aa;margin-top:-15px;'>"
        "Player analysis – percentile rankings within positional group</p>",
        unsafe_allow_html=True)

    if not generate_btn:
        st.markdown("""
        <div style='text-align:center; margin-top:80px; color:#8899aa;'>
            <h3>👈 Select filters and click <strong style='color:#1D3F6E;'>Generate Radar</strong></h3>
            <p>Season → League → Player</p>
        </div>
        """, unsafe_allow_html=True)
    elif min_minutes < 300:
        st.warning("⚠️ Wartość nie może być mniejsza niż 300.")
    else:
        with st.spinner("Generating radar..."):
            if selected_position == 'GK':
                active_mapping = GK_MAPPING2 if '_goals_prevented_pct' in group.columns else GK_MAPPING
            elif selected_position in CB_POSITIONS and '_cards_per_90' in group.columns:
                active_mapping = CB_MAPPING2
            elif selected_position in FB_POSITIONS and '_cards_per_90' in group.columns:
                active_mapping = FB_MAPPING2
            elif '_pAdj_TklInt' in group.columns:
                active_mapping = MAPPING2
            else:
                active_mapping = MAPPING

            stat_cols = [c for c in active_mapping if c in group.columns]
            missing   = [c for c in active_mapping if c not in group.columns]

            if not stat_cols:
                st.error("No stat columns found for this position.")
            else:
                if missing:
                    st.info(f"Skipped: {missing}")
                group = compute_percentiles(group, stat_cols)

                if has_fullname:
                    row = group[group['Full name'] == selected_player]
                    if row.empty:
                        row = group[group['Full name'].str.lower() == selected_player.lower()]
                else:
                    row = group[group['Player'] == selected_player]
                    if row.empty:
                        row = group[group['Player'].str.lower() == selected_player.lower()]

                if row.empty:
                    st.error(f"Player not found: {selected_player}")
                else:
                    pct_vals       = [row[c + '_pct'].iloc[0] for c in stat_cols]
                    labels         = [active_mapping[c] for c in stat_cols]
                    _tc_radar = next((c for c in ['Team within selected timeframe', 'Team'] if c in row.columns), None)
                    team      = row[_tc_radar].iloc[0] if _tc_radar else None
                    full_name      = (row['Full name'].iloc[0]
                                      if has_fullname and pd.notna(row['Full name'].iloc[0])
                                      else selected_player)
                    player_minutes = row['Minutes played'].iloc[0] if 'Minutes played' in row.columns else None

                    logo_dict = load_logo_dict(LOGO_CSV)
                    logo_img  = None
                    if team and team in logo_dict:
                        logo_img = fetch_logo(logo_dict[team], size=0.30)

                    fig = draw_radar(
                        selected_player, full_name, player_minutes, team,
                        pct_vals, labels, n_players,
                        selected_league, selected_position, comp_group,
                        min_minutes, logo_img
                    )

                    col_l, col_c, col_r = st.columns([1, 3, 1])
                    with col_c:
                        st.pyplot(fig, use_container_width=True)
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', dpi=180,
                                    bbox_inches='tight', facecolor=BG_DARK)
                        buf.seek(0)
                        safe_name = _re.sub(r'[^\w\s-]', '', full_name).strip().replace(' ', '_')
                        st.download_button(
                            label="⬇️ Download PNG", data=buf,
                            file_name=f"radar_{safe_name}_{selected_league}_{sel_season_label}.png",
                            mime="image/png",
                        )
                    plt.close(fig)


# =====================================================================
#  COMPARISON TAB — spider / radar chart
# =====================================================================
def _get_league_players(df, lc, league, min_min=0):
    df2 = df[df[lc].astype(str).apply(_league_key) == _league_key(league)].copy()
    if 'Minutes played' in df2.columns:
        df2['_mn'] = pd.to_numeric(df2['Minutes played'], errors='coerce').fillna(0)
        df2 = df2[df2['_mn'] >= min_min].sort_values('_mn', ascending=False)
    nc  = 'Full name' if 'Full name' in df2.columns else 'Player'
    pc  = next((c for c in ['Primary position', 'Position', 'Pos'] if c in df2.columns), None)
    tc  = next((c for c in ['Team within selected timeframe', 'Team'] if c in df2.columns), None)
    ns  = df2[nc].fillna('').astype(str).str.strip()
    ps  = df2[pc].fillna('').astype(str).str.split(',').str[0].str.strip() if pc else pd.Series('', index=df2.index)
    ts  = df2[tc].fillna('').astype(str).str.strip() if tc else pd.Series('', index=df2.index)
    df2['_label'] = ns + '  [' + ps + ' · ' + ts + ']'
    return df2.drop_duplicates(subset='_label', keep='first').reset_index(drop=True)


def draw_spider_plotly(p1_name, p2_name, p1_pct, p2_pct, p1_raw, p2_raw,
                        labels, p1_color="#00BFFF", p2_color="#FF6B35"):
    """
    Plotly radar dla Player Comparison.
    - p1_pct / p2_pct : percentyle 0-100 liczone vs grupa pozycyjna (jak glowny radar)
    - p1_raw / p2_raw : surowe wartosci (wyswietlane w tooltipie po najechaniu na kropke)
    - labels          : nazwy statystyk
    Obie skale sa percentylowe — gracz z 60 podaniami/90 dostaje ok. 50-ty centyl,
    nie zaklada calego radaru.
    """
    n = len(labels)
    if n < 3:
        return None

    def safe(v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return 0.0
        return float(v)

    def make_hover(raw_vals, pct_vals, name, color):
        texts = []
        for raw, pct in zip(raw_vals, pct_vals):
            no_data = pct is None or (isinstance(pct, float) and np.isnan(pct))
            if no_data:
                texts.append(f"<b style=\'color:{color}\'>{name}</b><br>Brak danych")
            else:
                raw_s = (f"{float(raw):.2f}".rstrip("0").rstrip(".")
                         if raw is not None and not (isinstance(raw, float) and np.isnan(raw))
                         else "N/A")
                texts.append(
                    f"<b style=\'color:{color}\'>{name}</b><br>"
                    f"Percentyl: <b>{float(pct):.0f}</b><br>"
                    f"Wartość: {raw_s}"
                )
        return texts

    def hex_rgba(hx, alpha):
        hx = hx.lstrip("#")
        r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    theta  = labels + [labels[0]]
    r1     = [safe(v) for v in p1_pct] + [safe(p1_pct[0])]
    r2     = [safe(v) for v in p2_pct] + [safe(p2_pct[0])]
    hover1 = make_hover(p1_raw, p1_pct, p1_name, p1_color) +              [make_hover(p1_raw, p1_pct, p1_name, p1_color)[0]]
    hover2 = make_hover(p2_raw, p2_pct, p2_name, p2_color) +              [make_hover(p2_raw, p2_pct, p2_name, p2_color)[0]]

    fig = go.Figure()

    for r, hover, name, color in [
        (r1, hover1, p1_name, p1_color),
        (r2, hover2, p2_name, p2_color),
    ]:
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            fillcolor=hex_rgba(color, 0.15),
            name=name,
            line=dict(color=color, width=2.5),
            mode="lines+markers",
            marker=dict(
                size=9,
                color=color,
                line=dict(color="#0d1117", width=1.5),
            ),
            hovertext=hover,
            hoverinfo="text",
            hoverlabel=dict(
                bgcolor="#1a2a3a",
                font=dict(color="white", size=12),
                bordercolor=color,
            ),
        ))

    # Siatka co 10 (10 pierscionkow) — pelna widocznosc
    tickvals = list(range(10, 101, 10))
    ticktext = [str(v) for v in tickvals]

    fig.update_layout(
        polar=dict(
            bgcolor="#0d1117",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=tickvals,
                ticktext=ticktext,
                tickfont=dict(color="#5a6a7a", size=8),
                gridcolor="#2a3a4e",
                linecolor="#2a3a4e",
                gridwidth=0.7,
            ),
            angularaxis=dict(
                tickfont=dict(color="#c8d8e8", size=10),
                gridcolor="#2a3a4e",
                linecolor="#2a3a4e",
                gridwidth=0.7,
                rotation=90,
                direction="clockwise",
            ),
        ),
        paper_bgcolor="#0d1117",
        font=dict(color="#c8d8e8", family="sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.18,
            xanchor="center", x=0.5,
            font=dict(size=13, color="#c8d8e8"),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=620,
        margin=dict(t=30, b=90, l=70, r=70),
    )

    return fig


# =====================================================================
#  POMOCNICZA: wybor mappingu na podstawie pozycji
# =====================================================================
def _pick_cmp_mapping(pos):
    """Zwraca mapping statystyk dla Player Comparison — ta sama logika co glowny radar."""
    if pos == 'GK':
        return GK_MAPPING2
    if pos in CB_POSITIONS:
        return CB_MAPPING2
    if pos in FB_POSITIONS:
        return FB_MAPPING2
    return MAPPING2


# =====================================================================
#  COMPARISON TAB
# =====================================================================
with tab_compare:
    st.title("⚖️ Player Comparison")
    st.markdown(
        "<p style=\'color:#8899aa;margin-top:-15px;\'>"
        "Porównaj dwóch graczy — wartości percentylowe vs ich grupa pozycyjna</p>",
        unsafe_allow_html=True)

    cmp_min = st.number_input("Min. minutes", min_value=0, max_value=5000,
                               value=0, step=100, key="cmp_min")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("### 🔵 Player 1")
        cmp_l1   = st.selectbox("League", available_leagues, key="cmp_l1")
        df_cmp1  = _get_league_players(df_raw, league_col, cmp_l1, cmp_min)
        p1_label = st.selectbox("Player", df_cmp1["_label"].tolist(), key="cmp_p1")
        p1_row   = df_cmp1[df_cmp1["_label"] == p1_label].iloc[0]

    with col_p2:
        st.markdown("### 🟠 Player 2")
        cmp_l2   = st.selectbox("League", available_leagues, key="cmp_l2")
        df_cmp2  = _get_league_players(df_raw, league_col, cmp_l2, cmp_min)
        _def2    = min(1, len(df_cmp2) - 1)
        p2_label = st.selectbox("Player", df_cmp2["_label"].tolist(),
                                  index=_def2, key="cmp_p2")
        p2_row   = df_cmp2[df_cmp2["_label"] == p2_label].iloc[0]

    st.markdown("---")

    p1_short = p1_label.split("  [")[0]
    p2_short = p2_label.split("  [")[0]

    # Wyciagnij pozycje obu graczy
    _pc = next((c for c in ["Primary position", "Position", "Pos"]
                if c in df_cmp1.columns), None)
    p1_pos = str(p1_row[_pc]).split(",")[0].strip() if _pc else "AMF"
    p2_pos = str(p2_row[_pc]).split(",")[0].strip() if _pc else "AMF"

    # Mapping statystyk wg pozycji Gracza 1 (ta sama logika co glowny radar)
    active_mapping = _pick_cmp_mapping(p1_pos)
    stat_cols      = [c for c in active_mapping if c in df_raw.columns]

    if len(stat_cols) < 3:
        st.error("Za mało statystyk dostępnych w danych dla tej pozycji.")
    else:
        # Buduj grupy pozycyjne dla kazdego gracza osobno
        p1_group, _, _, _, _, _ = build_group(df_raw, cmp_l1, p1_pos, cmp_min)
        p2_group, _, _, _, _, _ = build_group(df_raw, cmp_l2, p2_pos, cmp_min)

        # Fallback: jesli za malo graczy w grupie uzyj calej ligi
        if len(p1_group) < 5:
            p1_group = df_cmp1.copy()
        if len(p2_group) < 5:
            p2_group = df_cmp2.copy()

        # Oblicz percentyle kazdego gracza wzgledem jego grupy
        p1_group_pct = compute_percentiles(p1_group, stat_cols)
        p2_group_pct = compute_percentiles(p2_group, stat_cols)

        # Znajdz wiersze graczy
        nc = "Full name" if "Full name" in p1_group_pct.columns else "Player"
        p1_pct_rows = p1_group_pct[
            p1_group_pct[nc].astype(str).str.strip() == p1_short.strip()
        ]
        p2_pct_rows = p2_group_pct[
            p2_group_pct[nc].astype(str).str.strip() == p2_short.strip()
        ]

        if p1_pct_rows.empty or p2_pct_rows.empty:
            missing = []
            if p1_pct_rows.empty: missing.append(p1_short)
            if p2_pct_rows.empty: missing.append(p2_short)
            st.error(
                f"Nie znaleziono gracza w grupie percentylowej: {', '.join(missing)}. "
                "Spróbuj zmniejszyć Min. minutes."
            )
        else:
            p1_pct_row = p1_pct_rows.iloc[0]
            p2_pct_row = p2_pct_rows.iloc[0]

            stat_labels  = [active_mapping[c] for c in stat_cols]
            p1_pct_vals  = [pd.to_numeric(p1_pct_row.get(c + "_pct", np.nan), errors="coerce")
                            for c in stat_cols]
            p2_pct_vals  = [pd.to_numeric(p2_pct_row.get(c + "_pct", np.nan), errors="coerce")
                            for c in stat_cols]
            p1_raw_vals  = [pd.to_numeric(p1_row.get(c, np.nan), errors="coerce")
                            for c in stat_cols]
            p2_raw_vals  = [pd.to_numeric(p2_row.get(c, np.nan), errors="coerce")
                            for c in stat_cols]

            p1_n = len(p1_group)
            p2_n = len(p2_group)

            st.caption(
                f"📊 Profil statystyczny: pozycja **{p1_pos}** · "
                f"🔵 {p1_short} vs {p1_n} graczy ({cmp_l1}) · "
                f"🟠 {p2_short} vs {p2_n} graczy ({cmp_l2})"
            )

            fig_cmp = draw_spider_plotly(
                p1_short, p2_short,
                p1_pct_vals, p2_pct_vals,
                p1_raw_vals, p2_raw_vals,
                stat_labels,
                p1_color="#00BFFF",
                p2_color="#FF6B35",
            )

            if fig_cmp:
                st.plotly_chart(fig_cmp, use_container_width=True)

            with st.expander("📋 Raw numbers"):
                def _fmt(v):
                    if v is None or (isinstance(v, float) and np.isnan(v)):
                        return "—"
                    return f"{float(v):.2f}".rstrip("0").rstrip(".")

                tbl = pd.DataFrame({
                    "Stat": stat_labels,
                    f"🔵 {p1_short}": [_fmt(v) for v in p1_raw_vals],
                    f"🔵 Pct": [
                        f"{v:.0f}" if not (isinstance(v, float) and np.isnan(v)) else "—"
                        for v in p1_pct_vals
                    ],
                    f"🟠 {p2_short}": [_fmt(v) for v in p2_raw_vals],
                    f"🟠 Pct": [
                        f"{v:.0f}" if not (isinstance(v, float) and np.isnan(v)) else "—"
                        for v in p2_pct_vals
                    ],
                })
                st.dataframe(tbl, use_container_width=True, hide_index=True)


# =====================================================================
#  PLAYER SIMILARITY — funkcje pomocnicze
# =====================================================================

def _get_sim_stat_cols(pos, df):
    """
    Zwraca liste kolumn statystyk dla pozycji — ta sama logika co radary.
    Sprawdza dostepnosc w df.
    """
    mapping = _pick_cmp_mapping(pos)
    return [c for c in mapping if c in df.columns]


@st.cache_data(show_spinner=False)
def _build_positional_pool(df_raw_hash, season_key, position, min_minutes):
    """
    Zwraca DataFrame z percentylami dla calej grupy pozycyjnej
    we wszystkich ligach (cross-league pool).
    Cachowany — liczy sie raz per konfiguracja.
    """
    # Uzywamy df_raw przekazanego globalnie — hash to klucz cache
    df = df_raw.copy()
    pos_col = next(
        (c for c in ['Primary position', 'Position', 'position', 'Pos']
         if c in df.columns), None
    )
    if pos_col is None:
        return pd.DataFrame()

    df['_main_pos'] = df[pos_col].astype(str).str.split(',').str[0].str.strip()
    df['_minutes']  = pd.to_numeric(df.get('Minutes played', 0), errors='coerce').fillna(0)

    comp_positions, _ = get_comparison_positions(position)
    pool = df[
        df['_main_pos'].isin(comp_positions) &
        (df['_minutes'] >= min_minutes)
    ].copy()

    stat_cols = _get_sim_stat_cols(position, pool)
    if not stat_cols or len(pool) < 5:
        return pool

    return compute_percentiles(pool, stat_cols)


# =====================================================================
#  LIGA — TIERY (comprehensive, dynamiczny fallback)
# =====================================================================
# Tier 1 = top 5 lig, im wyzszy numer tym nizszy poziom.
# Ligi spoza slownika: tier przypisywany dynamicznie na podstawie
# fuzzy match albo = 3 (neutral middle).
LEAGUE_TIERS: dict[str, int] = {
    # Tier 1 — top 5
    "Premier League":1, "La Liga":1, "Bundesliga":1,
    "Serie A":1, "Ligue 1":1,
    # Tier 2
    "Championship":2, "Segunda División":2, "2. Bundesliga":2,
    "Serie B":2, "Ligue 2":2, "Eredivisie":2,
    "Primeira Liga":2, "Jupiler Pro League":2, "Belgian Pro League":2,
    "Scottish Premiership":2, "Süper Lig":2, "Ekstraklasa":2,
    "Czech First League":2, "Russian Premier League":2,
    "Ukrainian Premier League":2, "Swiss Super League":2,
    "Austrian Bundesliga":2, "Danish Superliga":2,
    "Allsvenskan":2, "Eliteserien":2, "Veikkausliiga":2,
    "Greek Super League":2, "Croatian Football League":2,
    "Serbian SuperLiga":2, "Romanian First Division":2,
    "Hungarian OTP Bank Liga":2,
    # Tier 3
    "League One":3, "3. Liga":3, "Serie C":3,
    "Ligue 2 BKT":3, "Segunda División B":3,
    "Slovak Super Liga":3, "Bulgarian First League":3,
    "Slovenian PrvaLiga":3, "Belarusian Premier League":3,
    "Kazakhstani Premier League":3,
    # Tier 4
    "League Two":4, "National League":4,
    # Tier 5
    "Regional leagues":5,
}

@st.cache_data(show_spinner=False)
def _build_dynamic_tier_map(league_list: tuple) -> dict:
    """
    Buduje mape tier dla wszystkich lig w danych.
    Nieznane ligi: fuzzy match przez _league_key, fallback = tier 3.
    Cachowane — liczy sie raz na sesje.
    """
    tier_map = {}
    # Buduj klucze dla znanych lig
    known_keys = {_league_key(k): v for k, v in LEAGUE_TIERS.items()}
    for lg in league_list:
        if lg in LEAGUE_TIERS:
            tier_map[lg] = LEAGUE_TIERS[lg]
            continue
        key = _league_key(lg)
        if key in known_keys:
            tier_map[lg] = known_keys[key]
            continue
        # Heurystyki dla nieznanych lig
        lg_lower = lg.lower()
        if any(x in lg_lower for x in ['u17','u19','u21','u23','youth','junior','reserve']):
            tier_map[lg] = 5
        elif any(x in lg_lower for x in ['2nd','second','2. ','division 2','liga 2','league 2']):
            tier_map[lg] = 3
        elif any(x in lg_lower for x in ['3rd','third','3. ','division 3']):
            tier_map[lg] = 4
        else:
            tier_map[lg] = 3  # neutral default
    return tier_map


def compute_similarity_scores(
    target_row, pool_pct, stat_cols, name_col,
    stat_weights=None,
    apply_league_weight=False,
    apply_age_weight=False,
    target_league=None,
    dynamic_tier_map=None,
):
    """
    Weighted Euclidean distance na wektorach percentylowych.

    League weighting: liga traktowana jako dodatkowy wymiar przestrzeni
    (skala 0-100 oparta na tiers). Gracz z identycznej ligi = 100,
    z ligi o 4 tiery nizszej = 0. Waga = 2 statystyki.

    Age weighting: wiek traktowany jako dodatkowy wymiar (skala 0-100).
    Roznica 0 lat = 100, roznica 15+ lat = 0. Waga = 2 statystyki.

    Podejscie bez kar/bonusow — dodatkowe wymiary w przestrzeni Euklidesowej.
    """
    pct_cols  = [c + '_pct' for c in stat_cols]
    available = [c for c in pct_cols if c in pool_pct.columns]
    if not available:
        return pd.Series(dtype=float)

    n = len(available)

    # ── Wagi statystyk ────────────────────────────────────────────────
    if stat_weights:
        raw_cols = [c.replace('_pct', '') for c in available]
        w = np.array([float(stat_weights.get(c, 1.0)) for c in raw_cols], dtype=float)
    else:
        w = np.ones(n, dtype=float)
    w_sum = w.sum()
    w = w / w_sum * n if w_sum > 0 else np.ones(n, dtype=float)

    # ── Wektory percentylowe ──────────────────────────────────────────
    target_vec = np.array([
        pd.to_numeric(target_row.get(c, 50), errors='coerce') or 50
        for c in available
    ], dtype=float)
    target_vec = np.where(np.isnan(target_vec), 50.0, target_vec)

    matrix = pool_pct[available].apply(
        pd.to_numeric, errors='coerce'
    ).fillna(50.0).values.astype(float)

    # ── Dodatkowe wymiary ─────────────────────────────────────────────
    # Kazdy dodatkowy wymiar ma wage = 2 statystyki (tzn. liczy sie jak 2 staty)
    extra_target = []
    extra_matrix = []
    extra_weights = []

    # Wymiar ligowy
    if apply_league_weight and target_league is not None and dynamic_tier_map:
        lc_pool = next(
            (c for c in ['Competition', 'League', 'league', 'competition']
             if c in pool_pct.columns), None
        )
        if lc_pool is not None:
            t_tier = dynamic_tier_map.get(target_league, 3)
            cand_tiers = pool_pct[lc_pool].astype(str).apply(
                lambda x: dynamic_tier_map.get(x, 3)
            ).values.astype(float)
            # Skala: tier_diff 0→100, tier_diff 4→0
            t_tier_scaled   = max(0.0, (5 - t_tier) / 4.0 * 100.0)
            cand_tier_scaled = np.clip((5 - cand_tiers) / 4.0 * 100.0, 0.0, 100.0)
            extra_target.append(t_tier_scaled)
            extra_matrix.append(cand_tier_scaled)
            extra_weights.append(2.0)  # waga = 2 statystyki

    # Wymiar wiekowy
    if apply_age_weight:
        age_col = next(
            (c for c in ['Age', 'age', 'Birth year'] if c in pool_pct.columns), None
        )
        if age_col:
            target_age = pd.to_numeric(target_row.get(age_col, np.nan), errors='coerce')
            if not (target_age is None or np.isnan(target_age)):
                cand_ages = pd.to_numeric(
                    pool_pct[age_col], errors='coerce'
                ).fillna(target_age).values
                # Skala: roznica 0 lat → 100, 15+ lat → 0
                age_diff = np.abs(cand_ages - float(target_age))
                age_sim_scaled = np.clip((1.0 - age_diff / 15.0) * 100.0, 0.0, 100.0)
                # target sam ze soba = 100
                extra_target.append(100.0)
                extra_matrix.append(age_sim_scaled)
                extra_weights.append(2.0)

    # ── Polacz wektory ────────────────────────────────────────────────
    if extra_target:
        t_ext = np.array(extra_target, dtype=float)
        m_ext = np.column_stack(extra_matrix)  # (m, k)
        w_ext = np.array(extra_weights, dtype=float)

        # Diffs dla statystyk
        stat_diffs = (matrix - target_vec) ** 2 * w
        # Diffs dla dodatkowych wymiarow
        ext_diffs  = (m_ext - t_ext) ** 2 * w_ext

        distances = np.sqrt(stat_diffs.sum(axis=1) + ext_diffs.sum(axis=1))
        max_dist  = 100.0 * np.sqrt(w.sum() + w_ext.sum())
    else:
        diffs     = (matrix - target_vec) ** 2
        distances = np.sqrt((diffs * w).sum(axis=1))
        max_dist  = 100.0 * np.sqrt(w.sum())

    similarity = np.clip(100.0 * (1.0 - distances / max_dist), 0.0, 100.0)
    return pd.Series(similarity, index=pool_pct.index)



# =====================================================================
#  SIMILARITY TAB
# =====================================================================
with tab_similar:
    st.title("🔍 Player Similarity")
    st.markdown(
        "<p style='color:#8899aa;margin-top:-15px;'>"
        "Znajdź graczy o najbardziej zbliżonym profilu statystycznym — "
        "percentyle pozycyjne + odległość euklidesowa (metoda StatsBomb/SciSports)</p>",
        unsafe_allow_html=True
    )

    # ── Kontrolki ─────────────────────────────────────────────────────
    sim_col1, sim_col2, sim_col3 = st.columns([2, 1, 1])

    with sim_col1:
        sim_league = st.selectbox("Liga gracza", available_leagues, key="sim_league")

    with sim_col2:
        sim_min = st.number_input(
            "Min. minut (pool)", min_value=0, max_value=5000,
            value=500, step=100, key="sim_min"
        )

    with sim_col3:
        _topn_opts = [5, 10, 15, 20, 25, 30, "Wszystkie"]
        _topn_sel  = st.selectbox("Liczba wyników", _topn_opts, index=1, key="sim_topn")
        sim_top_n  = None if _topn_sel == "Wszystkie" else int(_topn_sel)

    # Zakres poola
    sim_scope = st.radio(
        "Zakres porównania",
        ["🌍 Wszystkie ligi", "🏟️ Tylko ta sama liga"],
        horizontal=True, key="sim_scope"
    )

    # Wybor gracza
    df_sim_league = _get_league_players(df_raw, league_col, sim_league, sim_min)
    sim_player_label = st.selectbox(
        "Gracz", df_sim_league['_label'].tolist(), key="sim_player"
    )
    sim_player_row = df_sim_league[df_sim_league['_label'] == sim_player_label].iloc[0]

    # Pozycja
    _pc_sim = next(
        (c for c in ['Primary position', 'Position', 'Pos'] if c in df_sim_league.columns),
        None
    )
    sim_pos = str(sim_player_row[_pc_sim]).split(',')[0].strip() if _pc_sim else 'AMF'
    sim_name = sim_player_label.split('  [')[0]

    comp_pos_list, comp_group_name = get_comparison_positions(sim_pos)

    st.caption(
        f"Pozycja: **{sim_pos}** · Grupa: *{comp_group_name}* · "
        f"Statystyki: {len(_get_sim_stat_cols(sim_pos, df_raw))}"
    )

    st.markdown("---")

    # ── Opcje dodatkowe ───────────────────────────────────────────────
    opt_c1, opt_c2 = st.columns(2)
    with opt_c1:
        apply_lw = st.checkbox(
            "🏟️ Apply league weighting",
            value=True, key="sim_apply_lw",
            help="Gracze z lig o podobnym poziomie (wg tierów ligowych) "
                 "traktowani jako bardziej podobni. "
                 "Liga = dodatkowy wymiar w przestrzeni Euklidesowej."
        )
    with opt_c2:
        apply_aw = st.checkbox(
            "🎂 Apply age weighting",
            value=True, key="sim_apply_aw",
            help="Gracze w podobnym wieku traktowani jako bardziej podobni. "
                 "Wiek = dodatkowy wymiar w przestrzeni Euklidesowej."
        )

    # ── Wagi statystyk ────────────────────────────────────────────────
    stat_cols_sim = _get_sim_stat_cols(sim_pos, df_raw)
    stat_weights_sim = {}
    if stat_cols_sim:
        mapping_for_weights = _pick_cmp_mapping(sim_pos)
        with st.expander("⚖️ Wagi statystyk (opcjonalne)", expanded=False):
            st.caption(
                "1.0 = standardowa waga · 3.0 = trzykrotnie ważniejsza · "
                "0.0 = ignoruj tę statystykę"
            )
            w_cols_ui = st.columns(3)
            for i, c in enumerate(stat_cols_sim):
                lbl = mapping_for_weights.get(c, c).replace("\n", " ")
                val = w_cols_ui[i % 3].number_input(
                    lbl, min_value=0.0, max_value=5.0,
                    value=1.0, step=0.5, key=f"sw_{c}"
                )
                stat_weights_sim[c] = val

    # ── Obliczenia ────────────────────────────────────────────────────

    if len(stat_cols_sim) < 3:
        st.error("Za mało statystyk dostępnych dla tej pozycji w danych.")
    else:
        # Buduj pool
        pos_col_g = next(
            (c for c in ['Primary position', 'Position', 'position', 'Pos']
             if c in df_raw.columns), None
        )
        df_pool = df_raw.copy()
        df_pool['_main_pos'] = df_pool[pos_col_g].astype(str).str.split(',').str[0].str.strip()
        df_pool['_minutes']  = pd.to_numeric(
            df_pool.get('Minutes played', 0), errors='coerce'
        ).fillna(0)

        mask_pos  = df_pool['_main_pos'].isin(comp_pos_list)
        mask_min  = df_pool['_minutes'] >= sim_min

        if sim_scope == "🏟️ Tylko ta sama liga":
            mask_scope = df_pool[league_col].astype(str).apply(_league_key) == _league_key(sim_league)
        else:
            mask_scope = pd.Series(True, index=df_pool.index)

        pool = df_pool[mask_pos & mask_min & mask_scope].copy()

        # Buduj dynamiczna mape tierow dla wszystkich lig w danych
        all_leagues_in_data = tuple(sorted(df_raw[league_col].dropna().astype(str).unique()))
        dynamic_tier_map = _build_dynamic_tier_map(all_leagues_in_data)

        if len(pool) < 5:
            st.warning(
                f"Zbyt mały pool ({len(pool)} graczy). "
                "Zmniejsz Min. minut lub wybierz 'Wszystkie ligi'."
            )
        else:
            with st.spinner(f"Obliczam podobieństwo dla {len(pool)} graczy…"):
                pool_pct = compute_percentiles(pool, stat_cols_sim)

                # Znajdz wiersz gracza w poolu percentylowym
                nc_sim = 'Full name' if 'Full name' in pool_pct.columns else 'Player'
                target_mask = pool_pct[nc_sim].astype(str).str.strip() == sim_name.strip()

                if not target_mask.any():
                    # fallback: szukaj case-insensitive
                    target_mask = (
                        pool_pct[nc_sim].astype(str).str.strip().str.lower()
                        == sim_name.strip().lower()
                    )

                if not target_mask.any():
                    st.error(
                        f"Nie znaleziono **{sim_name}** w poolu. "
                        "Zmniejsz Min. minut."
                    )
                else:
                    target_pct_row = pool_pct[target_mask].iloc[0]

                    # Oblicz podobienstwo dla wszystkich
                    _stat_w = stat_weights_sim if any(
                        v != 1.0 for v in stat_weights_sim.values()
                    ) else None
                    scores = compute_similarity_scores(
                        target_pct_row, pool_pct, stat_cols_sim, nc_sim,
                        stat_weights=_stat_w,
                        apply_league_weight=apply_lw,
                        apply_age_weight=apply_aw,
                        target_league=sim_league,
                        dynamic_tier_map=dynamic_tier_map,
                    )
                    pool_pct = pool_pct.copy()
                    pool_pct['_similarity'] = scores

                    # Wyklucz samego gracza
                    result = pool_pct[~target_mask].copy()
                    result = result.sort_values('_similarity', ascending=False) if sim_top_n is None else result.sort_values('_similarity', ascending=False).head(sim_top_n)

                    # ── Tabela wynikow ────────────────────────────────
                    tc_sim  = next((c for c in ['Team within selected timeframe', 'Team'] if c in result.columns), None)
                    lc_sim  = next(
                        (c for c in ['Competition', 'League', 'league', 'competition']
                         if c in result.columns), None
                    )
                    mn_sim  = 'Minutes played' if 'Minutes played' in result.columns else None
                    age_sim = next(
                        (c for c in ['Age', 'age'] if c in result.columns), None
                    )

                    # Age gracza docelowego
                    target_age_val = None
                    if age_sim:
                        _ta = pd.to_numeric(target_pct_row.get(age_sim, np.nan), errors='coerce')
                        if not np.isnan(_ta):
                            target_age_val = int(_ta)

                    rows = []
                    for rank, (_, r) in enumerate(result.iterrows(), 1):
                        name  = str(r.get(nc_sim, '—')).strip()
                        team  = str(r.get(tc_sim, '—')).strip() if tc_sim else '—'
                        lg    = str(r.get(lc_sim, '—')).strip() if lc_sim else '—'
                        mins  = int(r.get(mn_sim, 0)) if mn_sim else 0
                        pos_v = str(r.get('_main_pos', '—')).strip()
                        sim_v = float(r['_similarity'])
                        age_v = None
                        if age_sim:
                            _a = pd.to_numeric(r.get(age_sim, np.nan), errors='coerce')
                            age_v = int(_a) if not np.isnan(_a) else None
                        rows.append({
                            '#':          rank,
                            'Gracz':      name,
                            'Drużyna':    team,
                            'Liga':       lg,
                            'Poz.':       pos_v,
                            'Wiek':       age_v if age_v is not None else '—',
                            'Minuty':     mins,
                            'Similarity': sim_v,
                        })

                    df_results = pd.DataFrame(rows)
                    # Zaokrągl Similarity do 1 miejsca po przecinku
                    df_results['Similarity'] = df_results['Similarity'].round(1)

                    _age_info = f", wiek: {target_age_val}" if target_age_val else ""
                    st.markdown(
                        f"### Najbardziej podobni do **{sim_name}** "
                        f"({comp_group_name}{_age_info}, min. {sim_min} min, "
                        f"pool: {len(pool)} graczy)"
                    )

                    # Native st.dataframe z column_config — virtual scrolling,
                    # zero lagów nawet przy 5k+ wierszy
                    _sim_col_cfg = {
                        'Similarity': st.column_config.ProgressColumn(
                            'Similarity', format='%.1f%%',
                            min_value=0, max_value=100,
                        ),
                        'Minuty': st.column_config.NumberColumn('Minuty', format='%d'),
                        '#': st.column_config.NumberColumn('#', width='small'),
                    }
                    if 'Wiek' in df_results.columns:
                        _sim_col_cfg['Wiek'] = st.column_config.NumberColumn('Wiek', format='%d')

                    st.dataframe(
                        df_results,
                        use_container_width=True,
                        hide_index=True,
                        height=600,
                        column_config=_sim_col_cfg,
                    )

                    # ── Mini radary dla top 3 ─────────────────────────
                    st.markdown("### 🕸️ Porównanie profilowe — Top 3")

                    top3 = result.head(3)
                    mapping_sim = _pick_cmp_mapping(sim_pos)
                    sim_stat_labels = [
                        mapping_sim[c].replace('\n', ' ') for c in stat_cols_sim
                    ]

                    # Percentyle gracza docelowego
                    t_pct = [
                        pd.to_numeric(
                            target_pct_row.get(c + '_pct', np.nan), errors='coerce'
                        )
                        for c in stat_cols_sim
                    ]
                    t_raw = [
                        pd.to_numeric(target_pct_row.get(c, np.nan), errors='coerce')
                        for c in stat_cols_sim
                    ]

                    radar_cols = st.columns(min(3, len(top3)))

                    for idx, (col_widget, (_, cand)) in enumerate(
                        zip(radar_cols, top3.iterrows())
                    ):
                        cand_name = str(cand.get(nc_sim, f'Gracz {idx+1}')).strip()
                        cand_sim  = float(cand['_similarity'])
                        cand_team = str(cand.get(tc_sim, '')).strip() if tc_sim else ''
                        cand_lg   = str(cand.get(lc_sim, '')).strip() if lc_sim else ''

                        c_pct = [
                            pd.to_numeric(cand.get(c + '_pct', np.nan), errors='coerce')
                            for c in stat_cols_sim
                        ]
                        c_raw = [
                            pd.to_numeric(cand.get(c, np.nan), errors='coerce')
                            for c in stat_cols_sim
                        ]

                        fig_mini = draw_spider_plotly(
                            sim_name, cand_name,
                            t_pct, c_pct,
                            t_raw, c_raw,
                            sim_stat_labels,
                            p1_color="#00BFFF",
                            p2_color="#FF6B35",
                        )

                        with col_widget:
                            st.markdown(
                                f"**#{idx+1} {cand_name}**  \n"
                                f"<span style='color:#8899aa;font-size:12px'>"
                                f"{cand_team} · {cand_lg}</span>  \n"
                                f"<span style='color:#00BFFF;font-weight:bold'>"
                                f"Similarity: {cand_sim:.1f}%</span>",
                                unsafe_allow_html=True
                            )
                            if fig_mini:
                                fig_mini.update_layout(height=420, margin=dict(t=20, b=60, l=40, r=40))
                                st.plotly_chart(
                                    fig_mini, use_container_width=True,
                                    key=f"sim_radar_{idx}"
                                )

                    # ── Tabela percentylowa porownawcza ───────────────
                    with st.expander("📋 Pełna tabela percentylowa"):
                        pct_rows = []
                        for c in stat_cols_sim:
                            lbl = mapping_sim.get(c, c).replace('\n', ' ')
                            t_p = pd.to_numeric(
                                target_pct_row.get(c + '_pct', np.nan), errors='coerce'
                            )
                            t_r = pd.to_numeric(
                                target_pct_row.get(c, np.nan), errors='coerce'
                            )

                            row_d = {
                                'Statystyka': lbl,
                                f'{sim_name} (raw)': f"{t_r:.2f}".rstrip('0').rstrip('.')
                                    if not np.isnan(t_r) else '—',
                                f'{sim_name} (pct)': f"{t_p:.0f}"
                                    if not np.isnan(t_p) else '—',
                            }
                            for _, cand in top3.iterrows():
                                cn = str(cand.get(nc_sim, '?')).strip()
                                c_r = pd.to_numeric(cand.get(c, np.nan), errors='coerce')
                                c_p = pd.to_numeric(
                                    cand.get(c + '_pct', np.nan), errors='coerce'
                                )
                                row_d[f'{cn} (raw)'] = (
                                    f"{c_r:.2f}".rstrip('0').rstrip('.')
                                    if not np.isnan(c_r) else '—'
                                )
                                row_d[f'{cn} (pct)'] = (
                                    f"{c_p:.0f}" if not np.isnan(c_p) else '—'
                                )
                            pct_rows.append(row_d)

                        st.dataframe(
                            pd.DataFrame(pct_rows),
                            use_container_width=True,
                            hide_index=True
                        )

# =====================================================================
#  SCATTER PLOT TAB
# =====================================================================

# Explicit zbiory pozycji dla scatter — NIEZALEZNE od HARDCODED_GROUPS.
# HARDCODED_GROUPS ma szerokie pos_listy (np. LCMF zawiera DMF) bo
# sluzy do percentyli. Tu chcemy ostre granice dla filtra i koloru.
SCATTER_POS_ALLOWED = {
    'Goalkeepers':  {'GK'},
    'CF':           {'CF'},
    'Wingers':      {'LW', 'RW', 'LWF', 'RWF', 'LAMF', 'RAMF'},
    'CM/AM':        {'AMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'},
    'DM/CM':        {'DMF', 'LDMF', 'RDMF', 'LCMF', 'RCMF', 'LCMF3', 'RCMF3'},
    'FBs & WBs':    {'LB', 'RB', 'LWB', 'RWB', 'LB5', 'RB5', 'LWB5', 'RWB5'},
    'Center Backs': {'CB', 'LCB', 'RCB', 'LCB3', 'RCB3'},
}
_SCATTER_POS_OPTIONS = list(SCATTER_POS_ALLOWED.keys())

# Odwrotny slownik: pozycja -> etykieta scatter
_POS_TO_SCATTER_GROUP = {
    pos: grp
    for grp, pos_set in SCATTER_POS_ALLOWED.items()
    for pos in pos_set
}

# Predefiniowane kombinacje osi — klasyczne scouting pary
SCATTER_PRESETS = {
    "⚽ Goals vs xG (finishing quality)":
        ("Non-penalty goals per 90",  "xG per 90"),
    "🎯 xG vs xA (offensive threat)":
        ("xG per 90",                 "xA per 90"),
    "📤 Progressive Passes vs Carries":
        ("Progressive passes per 90", "Progressive runs per 90"),
    "🥅 Shots vs npxG per Shot (volume vs quality)":
        ("Shots per 90",              "_npxG_per_shot"),
    "🛡️ Defensive Actions vs Aerial Win %":
        ("Successful defensive actions per 90", "Aerial duels won, %"),
    "📊 Passes per 90 vs Accuracy":
        ("Passes per 90",             "Accurate passes, %"),
    "🔀 Crosses vs Accuracy":
        ("Crosses per 90",            "Accurate crosses, %"),
    "🏃 Dribbles vs Success %":
        ("Dribbles per 90",           "Successful dribbles, %"),
    "🤼 Duels vs Win %":
        ("Duels per 90",              "Duels won, %"),
    "🧤 GK: Save Rate vs xG Against":
        ("Save rate, %",              "xG against per 90"),
    "🧤 GK: Prevented Goals vs Exits":
        ("Prevented goals per 90",    "Exits per 90"),
}

# Wszystkie staty dostepne na osiach — ze wszystkich mappingow + COMPARE_CATEGORIES
def _all_scatter_stats(df):
    """Zwraca liste wszystkich sensownych kolumn numerycznych dostepnych w df."""
    candidates = set()
    for cat_stats in COMPARE_CATEGORIES.values():
        candidates.update(cat_stats)
    for m in [MAPPING, MAPPING2, GK_MAPPING, GK_MAPPING2, CB_MAPPING2, FB_MAPPING2]:
        candidates.update(m.keys())
    # Dodaj computed columns
    candidates.update(['_pAdj_TklInt', '_npxG_per_shot', '_goals_prevented_pct',
                        '_cards_per_90', '_assists_2nd3rd'])
    # Tylko kolumny ktore sa w df i maja wartosci numeryczne
    available = []
    for c in sorted(candidates):
        if c in df.columns:
            if pd.to_numeric(df[c], errors='coerce').notna().sum() > 5:
                available.append(c)
    return available

def _stat_label(col):
    """Krótka etykieta dla kolumny — z mappingow lub skrocona nazwa."""
    for m in [MAPPING2, MAPPING, GK_MAPPING2, GK_MAPPING, CB_MAPPING2, FB_MAPPING2]:
        if col in m:
            return m[col].replace('\n', ' ')
    return col.replace(' per 90', ' p90').replace(', %', ' %').replace('_', ' ')

with tab_scatter:
    st.title("📈 Scatter Plot")
    st.markdown(
        "<p style='color:#8899aa;margin-top:-15px;'>"
        "Eksploruj zależności między statystykami — "
        "zaznacz gracza, filtruj pozycje i ligi</p>",
        unsafe_allow_html=True
    )

    # ── Filtry górne ────────────────────────────────────────────────
    sc_c1, sc_c2, sc_c3 = st.columns([2, 1, 1])

    with sc_c1:
        sc_leagues = st.multiselect(
            "Liga(i)", available_leagues,
            default=[available_leagues[0]] if available_leagues else [],
            key="sc_leagues"
        )
    with sc_c2:
        sc_min = st.number_input(
            "Min. minut", min_value=0, max_value=5000,
            value=500, step=100, key="sc_min"
        )
    with sc_c3:
        sc_color_by = st.selectbox(
            "Kolor punktów",
            ["Pozycja", "Liga", "Drużyna"],
            key="sc_color_by"
        )

    # Filtr pozycji — etykiety tylko dla scatter (niezalezne od HARDCODED_GROUPS)
    all_pos_groups = _SCATTER_POS_OPTIONS
    sc_pos_groups = st.multiselect(
        "Grupy pozycji (puste = wszystkie)",
        all_pos_groups,
        default=[],
        key="sc_pos"
    )

    st.markdown("---")

    # ── Wybór osi ───────────────────────────────────────────────────
    preset_col, custom_col = st.columns([1, 2])

    with preset_col:
        sc_preset = st.selectbox(
            "Preset par",
            ["— własny wybór —"] + list(SCATTER_PRESETS.keys()),
            key="sc_preset"
        )

    all_sc_stats = _all_scatter_stats(df_raw)
    stat_labels_map = {c: f"{_stat_label(c)}  [{c}]" for c in all_sc_stats}
    label_to_col    = {v: k for k, v in stat_labels_map.items()}

    # Domyslne osie z presetu
    if sc_preset != "— własny wybór —" and sc_preset in SCATTER_PRESETS:
        default_x, default_y = SCATTER_PRESETS[sc_preset]
        default_x = default_x if default_x in all_sc_stats else all_sc_stats[0]
        default_y = default_y if default_y in all_sc_stats else all_sc_stats[1]
    else:
        default_x = all_sc_stats[0] if all_sc_stats else None
        default_y = all_sc_stats[1] if len(all_sc_stats) > 1 else None

    with custom_col:
        ax_col1, ax_col2, ax_col3 = st.columns(3)
        with ax_col1:
            x_label = st.selectbox(
                "Oś X", list(stat_labels_map.values()),
                index=list(stat_labels_map.keys()).index(default_x)
                      if default_x in stat_labels_map else 0,
                key="sc_x"
            )
        with ax_col2:
            y_label = st.selectbox(
                "Oś Y", list(stat_labels_map.values()),
                index=list(stat_labels_map.keys()).index(default_y)
                      if default_y in stat_labels_map else 1,
                key="sc_y"
            )
        with ax_col3:
            size_opts = ["— brak —"] + list(stat_labels_map.values())
            sc_size_label = st.selectbox(
                "Rozmiar (opcja)", size_opts,
                index=0, key="sc_size"
            )

    x_col    = label_to_col.get(x_label)
    y_col    = label_to_col.get(y_label)
    size_col = label_to_col.get(sc_size_label) if sc_size_label != "— brak —" else None

    if not x_col or not y_col:
        st.error("Wybierz statystyki dla obu osi.")
    elif not sc_leagues:
        st.info("Wybierz co najmniej jedną ligę.")
    else:
        # ── Budowanie datasetu ───────────────────────────────────────
        pos_col_sc = next(
            (c for c in ['Primary position', 'Position', 'position', 'Pos']
             if c in df_raw.columns), None
        )
        nc_sc = 'Full name' if 'Full name' in df_raw.columns else 'Player'
        tc_sc = next((c for c in ['Team within selected timeframe', 'Team'] if c in df_raw.columns), None)

        df_sc = df_raw.copy()
        df_sc['_main_pos'] = (df_sc[pos_col_sc].astype(str)
                              .str.split(',').str[0].str.strip()
                              if pos_col_sc else 'N/A')
        df_sc['_minutes']  = pd.to_numeric(
            df_sc.get('Minutes played', 0), errors='coerce'
        ).fillna(0)

        # Filtr ligowy
        mask_lg = df_sc[league_col].astype(str).apply(_league_key).isin(
            [_league_key(l) for l in sc_leagues]
        )
        df_sc = df_sc[mask_lg & (df_sc['_minutes'] >= sc_min)].copy()

        # Filtr pozycji — uzywa SCATTER_POS_ALLOWED (ostre granice, bez bledu)
        if sc_pos_groups:
            allowed_pos = set()
            for grp in sc_pos_groups:
                allowed_pos.update(SCATTER_POS_ALLOWED.get(grp, set()))
            df_sc = df_sc[df_sc['_main_pos'].isin(allowed_pos)]

        # Oznacz grupe pozycyjna — uzywa _POS_TO_SCATTER_GROUP (CM/AM bez DM!)
        df_sc['_pos_group'] = df_sc['_main_pos'].map(_POS_TO_SCATTER_GROUP).fillna(df_sc['_main_pos'])

        # Konwertuj osie
        df_sc['_x']    = pd.to_numeric(df_sc[x_col],    errors='coerce')
        df_sc['_y']    = pd.to_numeric(df_sc[y_col],    errors='coerce')
        if size_col:
            df_sc['_sz'] = pd.to_numeric(df_sc[size_col], errors='coerce').fillna(0)
        df_sc = df_sc.dropna(subset=['_x', '_y'])

        if df_sc.empty:
            st.warning("Brak danych dla wybranych filtrów.")
        else:
            # ── Highlight gracza ─────────────────────────────────────
            sc_hl_col, sc_label_col = st.columns([2, 1])
            with sc_hl_col:
                all_players_sc = sorted(
                    df_sc[nc_sc].dropna().astype(str).str.strip().unique().tolist()
                )
                sc_highlight = st.multiselect(
                    "Zaznacz gracza/y",
                    all_players_sc, default=[], key="sc_hl"
                )
            with sc_label_col:
                sc_show_labels = st.checkbox(
                    "Pokaż etykiety", value=False, key="sc_labels"
                )

            # ── Paleta kolorów ───────────────────────────────────────
            PALETTE = [
                "#00BFFF","#FF6B35","#2DCA72","#FFD700","#E040FB",
                "#FF4444","#00E5FF","#FF9800","#69F0AE","#EA80FC",
                "#F06292","#80D8FF","#CCFF90","#FFD180","#B9F6CA",
            ]

            if sc_color_by == "Pozycja":
                color_key = '_pos_group'
            elif sc_color_by == "Liga":
                color_key = league_col
            else:
                color_key = tc_sc if tc_sc else '_pos_group'

            color_vals  = df_sc[color_key].astype(str).fillna('N/A')
            unique_vals = sorted(color_vals.unique())
            color_map   = {v: PALETTE[i % len(PALETTE)] for i, v in enumerate(unique_vals)}

            # ── Linie sredniej (kwadranty) ───────────────────────────
            x_med = float(df_sc['_x'].median())
            y_med = float(df_sc['_y'].median())

            # ── Rozmiar bąbli ────────────────────────────────────────
            if size_col and '_sz' in df_sc.columns:
                sz_min, sz_max = df_sc['_sz'].min(), df_sc['_sz'].max()
                sz_range = sz_max - sz_min if sz_max > sz_min else 1
                marker_sizes = (
                    6 + 18 * (df_sc['_sz'] - sz_min) / sz_range
                ).clip(4, 24).tolist()
            else:
                marker_sizes = [8] * len(df_sc)

            # ── Buduj wykres Plotly ──────────────────────────────────
            fig_sc = go.Figure()

            # Linie sredniej — kwadranty
            x_range_pad = (df_sc['_x'].max() - df_sc['_x'].min()) * 0.05
            y_range_pad = (df_sc['_y'].max() - df_sc['_y'].min()) * 0.05
            x_lo = float(df_sc['_x'].min()) - x_range_pad
            x_hi = float(df_sc['_x'].max()) + x_range_pad
            y_lo = float(df_sc['_y'].min()) - y_range_pad
            y_hi = float(df_sc['_y'].max()) + y_range_pad

            fig_sc.add_shape(type="line",
                x0=x_med, x1=x_med, y0=y_lo, y1=y_hi,
                line=dict(color="#2a3a4e", width=1, dash="dot"), layer="below"
            )
            fig_sc.add_shape(type="line",
                x0=x_lo, x1=x_hi, y0=y_med, y1=y_med,
                line=dict(color="#2a3a4e", width=1, dash="dot"), layer="below"
            )
            # Etykiety kwadrantow
            x_lbl_r = _stat_label(x_col)
            y_lbl_r = _stat_label(y_col)
            quadrant_labels = [
                (x_hi, y_hi, "↗",  "top right",    "Wysoki X + Y"),
                (x_lo, y_hi, "↖",  "top left",     "Niski X, Wysoki Y"),
                (x_hi, y_lo, "↘",  "bottom right", "Wysoki X, Niski Y"),
                (x_lo, y_lo, "↙",  "bottom left",  "Niski X + Y"),
            ]
            for qx, qy, qarrow, qpos, qtip in quadrant_labels:
                fig_sc.add_annotation(
                    x=qx, y=qy, text=qarrow,
                    showarrow=False,
                    font=dict(size=18, color="#2a3a4e"),
                    xanchor="center", yanchor="middle",
                )

            # Trace per grupa kolorów
            for val in unique_vals:
                mask_v = color_vals == val
                df_v   = df_sc[mask_v]
                szs    = [marker_sizes[i] for i in df_v.index.map(
                    lambda i: df_sc.index.get_loc(i)
                )] if hasattr(df_sc.index, 'get_loc') else [8] * len(df_v)

                # Oblicz rozmiary dla tej grupy
                idx_list = [df_sc.index.get_loc(i) for i in df_v.index]
                szs_v    = [marker_sizes[i] for i in idx_list]

                # Hover text
                hover_texts = []
                for _, row in df_v.iterrows():
                    name  = str(row.get(nc_sc, '?')).strip()
                    team  = str(row.get(tc_sc, '')).strip() if tc_sc else ''
                    lg    = str(row.get(league_col, '')).strip()
                    pos_v = str(row.get('_main_pos', '')).strip()
                    xv    = row['_x']
                    yv    = row['_y']
                    mins  = int(row.get('_minutes', 0))
                    ht = (
                        f"<b>{name}</b><br>"
                        f"{team} · {lg}<br>"
                        f"Poz: {pos_v} · {mins} min<br>"
                        f"<b>{_stat_label(x_col)}: {xv:.2f}</b><br>"
                        f"<b>{_stat_label(y_col)}: {yv:.2f}</b>"
                    )
                    if size_col and '_sz' in row.index:
                        ht += f"<br>{_stat_label(size_col)}: {row['_sz']:.2f}"
                    hover_texts.append(ht)

                # Highlight — rozdziel na zaznaczonych i resztę
                hl_mask = df_v[nc_sc].astype(str).str.strip().isin(sc_highlight)

                # Normalny trace
                df_normal = df_v[~hl_mask]
                idx_n = [df_sc.index.get_loc(i) for i in df_normal.index]
                if not df_normal.empty:
                    fig_sc.add_trace(go.Scatter(
                        x=df_normal['_x'],
                        y=df_normal['_y'],
                        mode='markers' + ('+text' if sc_show_labels else ''),
                        marker=dict(
                            color=color_map[val],
                            size=[marker_sizes[i] for i in idx_n],
                            opacity=0.75,
                            line=dict(color="#0d1117", width=0.5),
                        ),
                        text=df_normal[nc_sc].astype(str) if sc_show_labels else None,
                        textposition="top center",
                        textfont=dict(size=8, color="#c8d8e8"),
                        hovertext=[hover_texts[df_v.index.get_loc(i)] for i in df_normal.index],
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="#1a2a3a", font=dict(color="white", size=12),
                                        bordercolor=color_map[val]),
                        name=val,
                        legendgroup=val,
                        showlegend=True,
                    ))

                # Highlighted trace
                df_hl = df_v[hl_mask]
                idx_h = [df_sc.index.get_loc(i) for i in df_hl.index]
                if not df_hl.empty:
                    fig_sc.add_trace(go.Scatter(
                        x=df_hl['_x'],
                        y=df_hl['_y'],
                        mode='markers+text',
                        marker=dict(
                            color=color_map[val],
                            size=[min(marker_sizes[i] + 8, 32) for i in idx_h],
                            opacity=1.0,
                            line=dict(color="#FFFFFF", width=2.5),
                            symbol='star',
                        ),
                        text=df_hl[nc_sc].astype(str),
                        textposition="top center",
                        textfont=dict(size=11, color="#FFFFFF"),
                        hovertext=[hover_texts[df_v.index.get_loc(i)] for i in df_hl.index],
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="#1a2a3a", font=dict(color="white", size=12),
                                        bordercolor="#FFFFFF"),
                        name=f"★ {val}",
                        legendgroup=val,
                        showlegend=False,
                    ))

            # Labelki sredniej
            fig_sc.add_annotation(
                x=x_med, y=y_hi,
                text=f"mediana X: {x_med:.2f}",
                showarrow=False,
                font=dict(size=9, color="#5a6a7a"),
                yanchor="top", xanchor="left",
                xshift=4,
            )
            fig_sc.add_annotation(
                x=x_hi, y=y_med,
                text=f"mediana Y: {y_med:.2f}",
                showarrow=False,
                font=dict(size=9, color="#5a6a7a"),
                xanchor="right", yanchor="bottom",
                yshift=4,
            )

            x_title = _stat_label(x_col)
            y_title = _stat_label(y_col)
            n_players_sc = len(df_sc)

            fig_sc.update_layout(
                xaxis=dict(
                    title=dict(text=x_title, font=dict(color="#8899aa", size=12)),
                    tickfont=dict(color="#8899aa", size=10),
                    gridcolor="#1e2a38", zerolinecolor="#2a3a4e",
                    range=[x_lo, x_hi],
                ),
                yaxis=dict(
                    title=dict(text=y_title, font=dict(color="#8899aa", size=12)),
                    tickfont=dict(color="#8899aa", size=10),
                    gridcolor="#1e2a38", zerolinecolor="#2a3a4e",
                    range=[y_lo, y_hi],
                ),
                paper_bgcolor="#0d1117",
                plot_bgcolor="#0d1117",
                font=dict(color="#c8d8e8"),
                legend=dict(
                    bgcolor="rgba(17,24,32,0.9)",
                    bordercolor="#1e2a38",
                    borderwidth=1,
                    font=dict(size=11, color="#c8d8e8"),
                    itemsizing='constant',
                ),
                height=640,
                margin=dict(t=40, b=60, l=70, r=40),
                hovermode="closest",
            )

            # Info kapsułka
            st.caption(
                f"**{n_players_sc}** graczy · "
                f"X: *{x_title}* · Y: *{y_title}*"
                + (f" · Rozmiar: *{_stat_label(size_col)}*" if size_col else "")
                + f" · Mediana X: {x_med:.2f}, Y: {y_med:.2f}"
            )

            st.plotly_chart(fig_sc, use_container_width=True)

            # ── Tabela outlierów ──────────────────────────────────────
            with st.expander("📋 Top 15 — prawy górny kwadrant (wysoki X i Y)"):
                df_q1 = df_sc[(df_sc['_x'] >= x_med) & (df_sc['_y'] >= y_med)].copy()
                df_q1['_score'] = (
                    (df_q1['_x'] - x_med) / (df_sc['_x'].std() + 1e-9) +
                    (df_q1['_y'] - y_med) / (df_sc['_y'].std() + 1e-9)
                )
                df_q1 = df_q1.sort_values('_score', ascending=False).head(15)

                tbl_q1 = pd.DataFrame({
                    'Gracz':         df_q1[nc_sc].astype(str).str.strip().values,
                    'Drużyna':       df_q1[tc_sc].astype(str).str.strip().values if tc_sc else ['—']*len(df_q1),
                    'Liga':          df_q1[league_col].astype(str).str.strip().values,
                    'Poz.':          df_q1['_main_pos'].values,
                    x_title:         df_q1['_x'].round(2).values,
                    y_title:         df_q1['_y'].round(2).values,
                    'Min.':          df_q1['_minutes'].astype(int).values,
                })
                st.dataframe(tbl_q1, use_container_width=True, hide_index=True)

# =====================================================================
#  PLAYER SEARCH TAB
# =====================================================================
with tab_search:
    st.title("🔎 Player Search")
    st.markdown(
        "<p style='color:#8899aa;margin-top:-15px;'>"
        "Filtruj graczy po ligach, wieku, minutach i dowolnych statystykach — "
        "ustaw minimalne/maksymalne wartości dla każdej staty</p>",
        unsafe_allow_html=True
    )

    # ── Filtry podstawowe ────────────────────────────────────────────
    ps_c1, ps_c2, ps_c3 = st.columns([3, 1, 1])

    with ps_c1:
        ps_leagues = st.multiselect(
            "Liga(i)", available_leagues,
            default=[available_leagues[0]] if available_leagues else [],
            key="ps_leagues"
        )
    with ps_c2:
        ps_min_min = st.number_input(
            "Min. minut", min_value=0, max_value=5000,
            value=900, step=100, key="ps_min_min"
        )
    with ps_c3:
        ps_max_min = st.number_input(
            "Max. minut", min_value=0, max_value=9000,
            value=9000, step=100, key="ps_max_min"
        )

    # Filtr pozycji
    ps_pos_groups = st.multiselect(
        "Grupy pozycji (puste = wszystkie)",
        _SCATTER_POS_OPTIONS,
        default=[],
        key="ps_pos"
    )

    # Filtr wieku
    ps_age_c1, ps_age_c2 = st.columns(2)
    with ps_age_c1:
        ps_age_min = st.number_input(
            "Min. wiek", min_value=14, max_value=50,
            value=14, step=1, key="ps_age_min"
        )
    with ps_age_c2:
        ps_age_max = st.number_input(
            "Max. wiek", min_value=14, max_value=50,
            value=40, step=1, key="ps_age_max"
        )

    st.markdown("---")

    # ── Wybór statystyk do filtrowania ──────────────────────────────
    ps_all_stats = _all_scatter_stats(df_raw)
    ps_stat_labels_map = {c: _stat_label(c) for c in ps_all_stats}

    ps_selected_stats = st.multiselect(
        "📊 Statystyki do filtrowania",
        ps_all_stats,
        default=ps_all_stats[:4] if ps_all_stats else [],
        format_func=lambda c: ps_stat_labels_map.get(c, c),
        key="ps_selected_stats"
    )

    # ── Slidery dla wybranych statystyk ─────────────────────────────
    ps_filters = {}  # {col: (min_val, max_val)}

    if ps_selected_stats and not (not ps_leagues):
        # Buduj bazowy dataset żeby obliczyć zakresy
        ps_pos_col = next(
            (c for c in ['Primary position', 'Position', 'position', 'Pos']
             if c in df_raw.columns), None
        )
        df_base = df_raw.copy()
        df_base['_main_pos'] = (df_base[ps_pos_col].astype(str)
                                .str.split(',').str[0].str.strip()
                                if ps_pos_col else 'N/A')
        df_base['_minutes'] = pd.to_numeric(
            df_base.get('Minutes played', 0), errors='coerce'
        ).fillna(0)

        # Filtr ligowy dla zakresów sliderów
        if ps_leagues:
            mask_lg_base = df_base[league_col].astype(str).apply(_league_key).isin(
                [_league_key(l) for l in ps_leagues]
            )
            df_base_filtered = df_base[mask_lg_base].copy()
        else:
            df_base_filtered = df_base.copy()

        st.markdown("#### 🎚️ Ustaw zakresy statystyk")
        st.caption("Przesuń suwaki żeby ustawić minimalną i maksymalną wartość dla każdej statystyki")

        slider_cols = st.columns(2)
        for s_idx, col_name in enumerate(ps_selected_stats):
            series = pd.to_numeric(df_base_filtered[col_name], errors='coerce').dropna()
            if series.empty:
                continue

            col_min = float(series.min())
            col_max = float(series.max())

            if col_min == col_max:
                continue

            # Zaokrąglenie dla czytelności
            if col_max - col_min > 100:
                step = 1.0
                col_min_r = float(int(col_min))
                col_max_r = float(int(col_max) + 1)
            elif col_max - col_min > 10:
                step = 0.1
                col_min_r = round(col_min, 1)
                col_max_r = round(col_max, 1)
            else:
                step = 0.01
                col_min_r = round(col_min, 2)
                col_max_r = round(col_max, 2)

            lbl = ps_stat_labels_map.get(col_name, col_name)

            with slider_cols[s_idx % 2]:
                val = st.slider(
                    lbl,
                    min_value=col_min_r,
                    max_value=col_max_r,
                    value=(col_min_r, col_max_r),
                    step=step,
                    key=f"ps_sl_{col_name}"
                )
                ps_filters[col_name] = val

    st.markdown("---")

    # ── Wyniki ──────────────────────────────────────────────────────
    if not ps_leagues:
        st.info("Wybierz co najmniej jedną ligę.")
    else:
        # Buduj dataset wynikowy
        ps_pos_col2 = next(
            (c for c in ['Primary position', 'Position', 'position', 'Pos']
             if c in df_raw.columns), None
        )
        nc_ps  = 'Full name' if 'Full name' in df_raw.columns else 'Player'
        tc_ps  = next((c for c in ['Team within selected timeframe', 'Team'] if c in df_raw.columns), None)
        age_ps = next((c for c in ['Age', 'age'] if c in df_raw.columns), None)

        df_res = df_raw.copy()
        df_res['_main_pos'] = (df_res[ps_pos_col2].astype(str)
                               .str.split(',').str[0].str.strip()
                               if ps_pos_col2 else 'N/A')
        df_res['_minutes']  = pd.to_numeric(
            df_res.get('Minutes played', 0), errors='coerce'
        ).fillna(0)

        # 1. Liga
        mask_lg2 = df_res[league_col].astype(str).apply(_league_key).isin(
            [_league_key(l) for l in ps_leagues]
        )
        df_res = df_res[mask_lg2].copy()

        # 2. Minuty
        df_res = df_res[
            (df_res['_minutes'] >= ps_min_min) &
            (df_res['_minutes'] <= ps_max_min)
        ]

        # 3. Pozycja
        if ps_pos_groups:
            allowed_pos2 = set()
            for g in ps_pos_groups:
                allowed_pos2.update(SCATTER_POS_ALLOWED.get(g, set()))
            df_res = df_res[df_res['_main_pos'].isin(allowed_pos2)]

        # 4. Wiek
        if age_ps and ps_age_min > 14 or ps_age_max < 40:
            df_res['_age_num'] = pd.to_numeric(df_res[age_ps], errors='coerce')
            df_res = df_res[
                (df_res['_age_num'] >= ps_age_min) &
                (df_res['_age_num'] <= ps_age_max)
            ]

        # 5. Slidery statystyk
        for col_name, (fmin, fmax) in ps_filters.items():
            if col_name not in df_res.columns:
                continue
            series_f = pd.to_numeric(df_res[col_name], errors='coerce')
            full_min = float(pd.to_numeric(df_raw[col_name], errors='coerce').min())
            full_max = float(pd.to_numeric(df_raw[col_name], errors='coerce').max())
            # Zastosuj filtr tylko jeśli suwak jest przesunięty
            if fmin > full_min or fmax < full_max:
                df_res = df_res[
                    (series_f >= fmin) & (series_f <= fmax)
                ]

        n_found = len(df_res)
        st.markdown(f"### Znaleziono **{n_found}** graczy")

        if n_found == 0:
            st.warning("Brak graczy spełniających kryteria. Rozluźnij filtry.")
        else:
            # Buduj tabelę wyników
            result_rows = []
            for _, r in df_res.iterrows():
                row_d = {
                    'Gracz':   str(r.get(nc_ps, '—')).strip(),
                    'Drużyna': str(r.get(tc_ps, '—')).strip() if tc_ps else '—',
                    'Liga':    str(r.get(league_col, '—')).strip(),
                    'Poz.':    str(r.get('_main_pos', '—')).strip(),
                }
                if age_ps:
                    _a = pd.to_numeric(r.get(age_ps, np.nan), errors='coerce')
                    row_d['Wiek'] = int(_a) if not np.isnan(_a) else '—'
                row_d['Minuty'] = int(r.get('_minutes', 0))

                # Wartości wybranych statystyk
                for col_name in ps_selected_stats:
                    if col_name in r.index:
                        v = pd.to_numeric(r.get(col_name, np.nan), errors='coerce')
                        lbl = ps_stat_labels_map.get(col_name, col_name)
                        row_d[lbl] = round(float(v), 2) if not np.isnan(v) else None
                result_rows.append(row_d)

            df_table = pd.DataFrame(result_rows)

            # Auto-sort: pierwsza wybrana staty malejąco, fallback = Minuty
            stat_col_names_sort = [
                ps_stat_labels_map.get(c, c) for c in ps_selected_stats
                if ps_stat_labels_map.get(c, c) in df_table.columns
            ]
            sort_col_label = stat_col_names_sort[0] if stat_col_names_sort else 'Minuty'
            if sort_col_label in df_table.columns:
                df_table = df_table.sort_values(
                    sort_col_label, ascending=False, na_position='last'
                )

            # Native st.dataframe z column_config — virtual scrolling,
            # zero lagów nawet przy 5k+ wierszy
            stat_col_names = [
                ps_stat_labels_map.get(c, c)
                for c in ps_selected_stats
                if ps_stat_labels_map.get(c, c) in df_table.columns
            ]

            _ps_col_cfg = {
                'Minuty': st.column_config.NumberColumn('Minuty', format='%d'),
            }
            if 'Wiek' in df_table.columns:
                _ps_col_cfg['Wiek'] = st.column_config.NumberColumn('Wiek', format='%d')
            for col in stat_col_names:
                _ps_col_cfg[col] = st.column_config.NumberColumn(col, format='%.2f')

            st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
                height=600,
                column_config=_ps_col_cfg,
            )

            # Download CSV
            csv_buf = io.BytesIO()
            df_table.to_csv(csv_buf, index=False, encoding='utf-8-sig')
            csv_buf.seek(0)
            st.download_button(
                "⬇️ Pobierz CSV", data=csv_buf,
                file_name="player_search_results.csv",
                mime="text/csv", key="ps_download"
            )

