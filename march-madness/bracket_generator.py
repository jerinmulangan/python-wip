import pandas as pd

regions = ["East", "South", "Midwest", "West"]
rows = []

# Round of 64
for region in regions:
    pairs = [(1,16),(8,9),(5,12),(4,13),(6,11),(3,14),(7,10),(2,15)]
    for idx, (s1, s2) in enumerate(pairs, start=1):
        rows.append({
            "slot_id": f"R64_{region}_{idx}",
            "team1": "",
            "team2": "",
            "next_slot_id": f"R32_{region}_{(idx+1)//2}",
            "region": region,
            "round": "R64"
        })

# Round of 32
for region in regions:
    for idx in range(1,5):
        rows.append({
            "slot_id": f"R32_{region}_{idx}",
            "team1": "",
            "team2": "",
            "next_slot_id": f"S16_{region}_{(idx+1)//2}",
            "region": region,
            "round": "R32"
        })

# Sweet 16
for region in regions:
    for idx in range(1,3):
        rows.append({
            "slot_id": f"S16_{region}_{idx}",
            "team1": "",
            "team2": "",
            "next_slot_id": f"E8_{region}_1",
            "region": region,
            "round": "S16"
        })

# Elite 8
for region in regions:
    rows.append({
        "slot_id": f"E8_{region}_1",
        "team1": "",
        "team2": "",
        "next_slot_id": f"F4_{1 if region in ['East','South'] else 2}",
        "region": region,
        "round": "E8"
    })

# Final Four
rows.append({
    "slot_id": "F4_1",
    "team1": "",
    "team2": "",
    "next_slot_id": "C1",
    "region": "FinalFour",
    "round": "F4"
})
rows.append({
    "slot_id": "F4_2",
    "team1": "",
    "team2": "",
    "next_slot_id": "C1",
    "region": "FinalFour",
    "round": "F4"
})

# Championship
rows.append({
    "slot_id": "C1",
    "team1": "",
    "team2": "",
    "next_slot_id": "",
    "region": "Championship",
    "round": "Champ"
})

template_df = pd.DataFrame(rows)
template_df.to_csv('data/bracket_template_2025.csv', index=False)
