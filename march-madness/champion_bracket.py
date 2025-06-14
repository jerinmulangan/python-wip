# champion_bracket.py

import pandas as pd
from pathlib import Path

PREPROBS = Path("data/pre2025_champ_probs.csv")
TEMPLATE = Path("data/bracket_template_2025.csv")
OUTPUT   = Path("data/2025_bracket_winners.csv")

if not PREPROBS.exists() or not TEMPLATE.exists():
    raise FileNotFoundError(
        "Missing input files. Ensure 'data/pre2025_champ_probs.csv' and 'data/bracket_template_2025.csv' exist."
    )

df_probs = pd.read_csv(PREPROBS)
bracket  = pd.read_csv(TEMPLATE)

if 'team1' not in bracket.columns or 'team2' not in bracket.columns:
    raise RuntimeError(
        "Your 'bracket_template_2025.csv' must include 'team1' and 'team2' columns "
        "with the exact team names as in 'pre2025_champ_probs.csv'."
    )

strength = dict(zip(df_probs['team'], df_probs['champ_prob']))

def play_round(df_round, scores):
    """
    Simulate a round of matchups:
      df_round: columns ['slot_id','team1','team2','next_slot_id','round']
      scores: dict of team->strength
    Returns: DataFrame of winners with ['slot_id','team','next_slot_id']
    """
    winners = []
    for _, row in df_round.iterrows():
        t1, t2 = row['team1'], row['team2']
        p1 = scores.get(t1, 0)
        p2 = scores.get(t2, 0)
        win = t1 if p1 >= p2 else t2
        winners.append({'slot_id': row['next_slot_id'], 'team': win, 'round': row['round']})
    return pd.DataFrame(winners)

winner_records = []
slots = bracket.copy()
for rd in ['R64','R32','S16','E8','F4','Champ']:
    df_rd = slots[slots['round'] == rd][['slot_id','team1','team2','next_slot_id','round']]
    if df_rd.empty:
        continue
    df_w = play_round(df_rd, strength)
    winner_records.append(df_w)
    # prepare slots for next iteration by merging team names into bracket template
    # next round slots already have team1, team2 placeholders in bracket

    slots = bracket.merge(
        df_w[['slot_id','team']].rename(columns={'slot_id':'slot_id','team':'team1'}),
        on='slot_id', how='left'
    )
    # fill team2 from original bracket for the slots
    slots['team2'] = slots['team2']

# Concatenate all winners
all_winners = pd.concat(winner_records, ignore_index=True)


print("Predicted 2025 bracket winners by round:")
for _, row in all_winners.iterrows():
    print(f"{row['round']}: {row['team']} (advances to {row['slot_id']})")

all_winners.to_csv(OUTPUT, index=False)
print(f"\n➡️  Full bracket winners saved to {OUTPUT}")
