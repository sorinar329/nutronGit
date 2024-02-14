import queryCollection

stadium = queryCollection.get_stadium_based_careagent("CareAgent_3_Spätstadium")[0]["label"]["value"]

print(f"Your Patient has Stadium {stadium}")

