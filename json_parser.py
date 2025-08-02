import os
import json
import pandas as pd

# Paths
JSON_PATH = os.path.abspath("data")  
PROCESSED_DATA_PATH = os.path.abspath("processed_data")  
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

match_types = {
    "test": "test_matches.csv",
    "odi": "odi_matches.csv",
    "t20": "t20_matches.csv",
    "ipl": "ipl_matches.csv"
}

match_data = {key: [] for key in match_types.keys()}

# Read JSON Files
json_files = [jfile for jfile in os.listdir(JSON_PATH) if jfile.endswith(".json")]

for jf in json_files:
    file_path = os.path.join(JSON_PATH, jf)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        match_id = jf.replace(".json", "")
        match_type = data["info"].get("match_type", "").lower()
        event_name = data["info"].get("event", {}).get("name", "").lower()

        if match_type == "test":
            match_category = "test"
        elif match_type == "odi":
            match_category = "odi"
        elif match_type == "t20" and "indian premier league" in event_name:
            match_category = "ipl"
        elif match_type == "t20":
            match_category = "t20"
        else:
            continue 

        # Extract Match Information
        teams = data["info"].get("teams", [])
        match_info = {
            "match_id": match_id,
            "season": data["info"].get("season"),
            "teams": ",".join(teams),
            "team_1": teams[0] if len(teams) > 1 else None,
            "team_2": teams[1] if len(teams) > 1 else None,
            "venue": data["info"].get("venue"),
            "city": data["info"].get("city"),
            "toss_winner": data["info"].get("toss", {}).get("winner"),
            "toss_decision": data["info"].get("toss", {}).get("decision"),
            "match_winner": data["info"].get("outcome", {}).get("winner"),
            "win_by_runs": data["info"].get("outcome", {}).get("by", {}).get("runs"),
            "player_of_match": ",".join(data["info"].get("player_of_match", [])),
            "match_date": data["info"].get("dates", [None])[0],
            "match_number": data["info"].get("event", {}).get("match_number"),
        }

        # Extract & Process Deliveries
        for i, inning in enumerate(data.get("innings", []), start=1):
            for over in inning.get("overs", []):
                over_num = over.get("over")
                for delivery in over.get("deliveries", []):
                    ball_num = delivery.get("ball")
                    ball_number = round(over_num + (ball_num / 10), 1) if over_num is not None and ball_num is not None else None

                    delivery_info = {
                        **match_info,
                        "inning": i,
                        "over_number": over_num,
                        "batsman": delivery.get("batter"),
                        "bowler": delivery.get("bowler"),
                        "runs_batsman": delivery.get("runs", {}).get("batter"),
                        "runs_total": delivery.get("runs", {}).get("total"),
                    }
                    match_data[match_category].append(delivery_info)
    
    except Exception as e:
        print(f"Error processing {jf}: {e}")

for match_type, data in match_data.items():
    file_path = os.path.join(PROCESSED_DATA_PATH, match_types[match_type])
    if data:
        df = pd.DataFrame(data)
        df = df.fillna({"city": "Unknown", "player_of_match": "Unknown"}) 
        df.to_csv(file_path, index=False)
        print(f"Saved: {match_types[match_type]} ({df.shape[0]} records)")
print("Data Processing Complete")