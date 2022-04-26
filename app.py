from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
import math

app = Flask(__name__)

PITCH_TYPES = {
    'FF': ['Fastball', '#e6194b'],
    'FT': ['Two-seam Fastball', '#469990'],
    'FC': ['Cutter', '#f58231'],
    'FS': ['Splitter', '#3cb44b'],
    'FO': ['Pitch Out', '#000000'],
    'SI': ['Sinker', '#911eb4'],
    'SL': ['Slider', '#000075'],
    'CU': ['Curveball', '#42d4f4'],
    'KC': ['Knuckle-curve', '#ffffff'],
    'EP': ['Eephus', '#ffffff'],
    'CH': ['Changeup', '#ffe119'],
    'SC': ['Screwball', '#ffffff'],
    'KN': ['Knuckleball', '#ffffff'],
    'UN': ['Unidentified', '#ffffff']
}

def getSpray(x, y):
    return round((math.atan((x-125.42)/(198.27-y))*180/math.pi*.75),2)

def getX(deg, hyp):
    return round(float(hyp) * math.sin(math.radians(deg)),2)

def getY(deg, hyp):
    return round(float(hyp) * math.cos(math.radians(deg)),2)

@app.route('/')
def index():
    df = pd.read_csv('./ohtani_pitching.csv')
    df_k = df.loc[df['events'] == 'strikeout']
    df_k_swing = df_k.loc[df_k['description'] != 'called_strike']
    pitches = df_k_swing.pitch_type.unique()
    data1 = []
    for pitch in pitches:
        p = []

        p.append(PITCH_TYPES[pitch][0])
        df_temp = df_k_swing.loc[df_k_swing['pitch_type'] == pitch]
        df_new = df_temp[['plate_x', 'plate_z']]
        df_new = df_new.rename(columns={"plate_x": "x", "plate_z": "y"})
        locs = list(zip(df_new.x, df_new.y))
        p.append(locs)
        p.append(PITCH_TYPES[pitch][1])
        data1.append(p)

    data2 = []

    pitches1 = df_k_swing.pitch_type.unique()
    for pitch1 in pitches1:
        p1 = []

        p1.append(PITCH_TYPES[pitch1][0])
        df_temp1 = df.loc[df['pitch_type'] == pitch1]
        df_new1 = df_temp1[['release_pos_x', 'release_pos_z']]
        df_new1 = df_new1.rename(columns={"release_pos_x": "x", "release_pos_z": "y"})
        locs1 = list(zip(df_new1.x, df_new1.y))
        p1.append(locs1)
        p1.append(PITCH_TYPES[pitch1][1])
        data2.append(p1)

    df_batting = pd.read_csv('./ohtani_batting.csv')
    df_bat = df_batting[~df_batting['hc_x'].isnull()]
    df_bat['spray_angle'] = df_bat.apply(lambda x: getSpray(x['hc_x'], x['hc_y']), axis=1)
    df_bat['x'] = df_bat.apply(lambda x: getX(x['spray_angle'], x['hit_distance_sc']), axis=1)
    df_bat['y'] = df_bat.apply(lambda x: getY(x['spray_angle'], x['hit_distance_sc']), axis=1)
    
    events = df_bat.events.unique()
    print(events)

    df_out = df_bat.loc[df_bat['events'] != 'single']
    df_out = df_out.loc[df_out['events'] != 'double']
    df_out = df_out.loc[df_out['events'] != 'home_run']

    df_single = df_bat[df_bat['events'] == 'single']
    df_double = df_bat[df_bat['events'] == 'double']
    df_hr = df_bat[df_bat['events'] == 'home_run']

    spray = [(df_out, 'Out/Error', '#FF0000'), (df_single, 'Single', '#42D4F4'), (df_double, 'Double', '#000075'), (df_hr, 'Home Run', '#3CB44B')]

    data3 = []

    for df_temp_b, title, color in spray:
        p2 = []

        p2.append(title)
        locs2 = list(zip(df_temp_b.x, df_temp_b.y))
        p2.append(locs2)
        p2.append(color)
        data3.append(p2)
    return render_template('index.html', data1=data1, data2=data2, data3=data3)

if __name__ == "__main__":
    app.run(debug=True)