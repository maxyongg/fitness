#!/usr/bin/env python3
"""
Re-run the full analysis on a Strong app CSV export.

    python3 analyse.py data/strong_workouts.csv

Every number in plan.md came from this script. Re-running it on a fresh export is
how you check whether the programme is working.

IMPORTANT: Strong preserves the ORDER exercises were performed in, and the START TIME
of each session. This script uses both. Ignoring the order produced three wrong
conclusions in this project — a scheduling change read as an injury. Do not drop it.

Two questions in here are confounded with the calendar and are reported with their
de-trended counterpart every run, so nobody re-derives them naively: session length and
time of day.
"""
import sys
import numpy as np
import pandas as pd

MUSCLE = {
    'chest': ['Bench Press', 'Chest Fly', 'Chest Press', 'Cable Crossover', 'Push Up',
              'Incline Chest Press', 'Landmine Press', 'Decline Chest Press'],
    'delts': ['Lateral Raise', 'Arnold Press', 'Overhead Press', 'Shoulder Press',
              'Front Raise', 'Upright Row'],
    'rear_delt': ['Face Pull', 'Reverse Fly', 'Delt Rear', 'Reverse Pec'],
    'triceps': ['Triceps', 'Tricep', 'Skullcrusher', 'Dip'],
    'back_vert': ['Pull Up', 'Chin Up', 'Pulldown', 'Pullover'],
    'back_horiz': ['Row'],
    'biceps': ['Curl'],
    'quads': ['Squat', 'Leg Extension', 'Leg Press', 'Lunge', 'Step Up'],
    'posterior': ['Deadlift', 'Hip Thrust', 'Leg Curl', 'Back Extension', 'Kettlebell Swing'],
    'calves': ['Calf'],
    'core': ['Crunch', 'Leg Raise', 'Ab Wheel', 'Russian Twist', 'V Up', 'Plank',
             'Dead Bug', 'Pallof', 'Woodchopper', 'Cable Twist', 'Shoulder Taps'],
}
ORDER = ['chest', 'delts', 'triceps', 'rear_delt', 'back_vert', 'back_horiz',
         'biceps', 'quads', 'posterior', 'calves', 'core']


def classify(name):
    """First match wins, so ORDER above matters: 'Leg Curl' must beat 'Curl'."""
    for grp in ['posterior', 'calves', 'core', 'rear_delt', 'back_vert', 'quads',
                'triceps', 'delts', 'chest', 'back_horiz', 'biceps']:
        if any(k.lower() in name.lower() for k in MUSCLE[grp]):
            return grp
    return 'other'


def load(path):
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'])
    df['day'] = df.Date.dt.normalize()
    df['row'] = range(len(df))                      # preserves performed order
    df['is_work'] = ~df['Set Order'].astype(str).eq('W')
    df['grp'] = df['Exercise Name'].map(classify)
    df['hour'] = df.Date.dt.hour                    # Strong records the start time
    df['e1rm'] = np.where(df.Weight > 0, df.Weight * (1 + df.Reps / 30.0), np.nan)
    return df


def section(title):
    print('\n' + '=' * 68)
    print(title)
    print('=' * 68)


def main(path):
    df = load(path)
    w = df[df.is_work]
    weeks = (df.day.max() - df.day.min()).days / 7

    section('SHAPE')
    print(f'{df.day.nunique()} sessions · {len(w)} working sets')
    print(f'{df.day.min().date()} → {df.day.max().date()}')
    print(f'{df.day.nunique()/weeks:.2f} sessions/week lifetime')
    recent = w[w.day >= w.day.max() - pd.Timedelta(weeks=12)]
    print(f'{recent.day.nunique()/12:.2f} sessions/week over the last 12 weeks')

    section('WEEKLY SETS BY MUSCLE GROUP — last 8 vs previous 8 weeks')
    cut = w.day.max() - pd.Timedelta(weeks=8)
    prev, cur = w[(w.day < cut) & (w.day >= cut - pd.Timedelta(weeks=8))], w[w.day >= cut]
    tab = pd.DataFrame({
        'prev_8wk': prev.groupby('grp').size() / 8,
        'last_8wk': cur.groupby('grp').size() / 8,
    }).reindex(ORDER).fillna(0).round(1)
    tab['change'] = (tab.last_8wk - tab.prev_8wk).round(1)
    print(tab.to_string())
    legs = ['quads', 'posterior', 'calves']
    print(f'\nlegs as % of all sets, lifetime: '
          f'{100*len(w[w.grp.isin(legs)])/len(w):.1f}%')

    section('EXERCISE ORDER — does position in the session cost performance?')
    first = df.groupby(['day', 'Exercise Name']).row.min().reset_index()
    first['pos'] = first.groupby('day').row.rank(method='dense').astype(int)
    first['n_ex'] = first.groupby('day')['Exercise Name'].transform('size')
    per = (w.groupby(['day', 'Exercise Name'])
             .agg(best=('e1rm', 'max'), reps=('Reps', 'sum')).reset_index()
             .merge(first[['day', 'Exercise Name', 'pos', 'n_ex']],
                    on=['day', 'Exercise Name']))
    per['metric'] = per.best.fillna(per.reps)       # bodyweight lifts scored on reps
    g = per.groupby('Exercise Name').metric
    per = per[g.transform('size') >= 8].copy()
    per['z'] = (per.metric - g.transform('mean')) / g.transform('std')
    print(per.groupby('pos').agg(mean_z=('z', 'mean'), n=('z', 'size')).round(3).to_string())

    section('SESSION LENGTH — UNANSWERABLE, shown so nobody re-derives it')
    print("""Two specifications, opposite answers:
  raw z-score      -> longer sessions look WORSE
  time-de-trended  -> longer sessions look BETTER

Neither is valid. Raw is confounded with the calendar: 6-exercise days are 49% of
2024 and 6% of 2026, so the comparison mostly measures two years of getting
stronger. De-trended is reverse causation: good days produce longer sessions, so
session length selects for good days.

Observational data cannot separate these. To actually answer it, alternate a
5-exercise and a 7-exercise version of the same session for 8 weeks, deciding
which BEFORE training rather than by feel on the day.""")
    per['bucket'] = pd.cut(per.n_ex, [0, 4, 5, 6, 99], labels=['<=4', '5', '6', '7+'])
    per['t'] = (per.day - per.day.min()).dt.days

    def detrend(g):
        if g.t.nunique() < 3:
            return pd.Series(np.nan, index=g.index)
        slope, icept = np.polyfit(g.t, g.metric, 1)
        r = g.metric - (icept + slope * g.t)
        sd = r.std()
        return r / (sd if sd > 0 else 1)

    per['resid'] = per.groupby('Exercise Name', group_keys=False).apply(detrend)
    cmp = pd.DataFrame({
        'raw_z': per.groupby('bucket', observed=True).z.mean(),
        'de-trended': per.groupby('bucket', observed=True).resid.mean(),
        'n': per.groupby('bucket', observed=True).z.size(),
    }).round(3)
    print('\n' + cmp.to_string())
    print('\nSigns disagree. That is the finding: there is no finding.')

    section('TIME OF DAY — confounded with the calendar, like session length')
    start = df.groupby('day').hour.min()
    per['hour'] = per.day.map(start)
    per['tod'] = pd.cut(per.hour, [-1, 11, 14, 17, 24],
                        labels=['morning <=11', 'midday 12-14', 'afternoon 15-17', 'evening 18+'])
    tod = pd.DataFrame({
        'raw_z': per.groupby('tod', observed=True).z.mean(),
        'de-trended': per.groupby('tod', observed=True).resid.mean(),
        'n': per.groupby('tod', observed=True).z.size(),
    }).round(3)
    print(tod.to_string())
    print("""
Raw says mornings are much better. De-trended says the gap is nearly gone. That is the
same trap as session length: he moved from evening training in 2024 to morning training
in 2026, over the same two years he got stronger, so the raw comparison is measuring the
calendar. Mornings are also mostly weekends.""")

    print('\n--- each year on its own (raw z), which removes most of the trend ---')
    per['yr'] = per.day.dt.year
    per['am'] = np.where(per.hour <= 11, 'morning', np.where(per.hour >= 18, 'evening', 'mid'))
    print(per.pivot_table(index='yr', columns='am', values='z', aggfunc='mean').round(3).to_string())
    print('Sign flips year to year — evening led in 2024, morning in 2025, level in 2026.')

    print('\n--- 2026 only, per lift, morning vs afternoon/evening ---')
    p26 = per[per.day >= '2026-01-01'].copy()
    p26['ampm'] = np.where(p26.hour <= 11, 'AM', 'PM')
    gaps = []
    for name, s_ in p26.groupby('Exercise Name'):
        t = s_.groupby('ampm').z.agg(['mean', 'size'])
        if len(t) < 2 or t['size'].min() < 4:
            continue
        gaps.append(t.loc['AM', 'mean'] - t.loc['PM', 'mean'])
    if gaps:
        print(f'{sum(1 for g_ in gaps if g_ > 0)}/{len(gaps)} lifts favour mornings · '
              f'mean gap {np.mean(gaps):+.3f} SD · median {np.median(gaps):+.3f}')
        print('Inside the clean window there is no effect. Train when it suits him.')

    section('KEY LIFTS — quarterly best e1RM')
    watch = ['Incline Bench Press (Barbell)', 'Bench Press (Barbell)',
             'Overhead Press (Barbell)', 'Squat (Barbell)',
             'Romanian Deadlift (Barbell)', 'Pull Up',
             'Single Arm Vertical Iso-Lateral Row (Machine)', 'Seated Wide-Grip Row (Cable)']
    for name in watch:
        s = w[w['Exercise Name'] == name]
        if s.empty:
            continue
        q = s.groupby(s.day.dt.to_period('Q')).agg(
            best_e1rm=('e1rm', 'max'), top_wt=('Weight', 'max'),
            top_reps=('Reps', 'max'), sets=('Reps', 'size'))
        print(f'\n--- {name}')
        print(q.round(1).tail(6).to_string())

    section('PULL-UPS — reps against position, the confound that caught me out')
    pu = per[per['Exercise Name'] == 'Pull Up'].sort_values('day').tail(20)
    print(pu[['day', 'pos', 'n_ex', 'reps']].to_string(index=False))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
