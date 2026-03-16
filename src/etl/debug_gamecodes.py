from euroleague_api.game_stats import GameStats

gs = GameStats("E")

print("=== get_gamecodes_season(2025) ===")
df = gs.get_gamecodes_season(2025)
print(f"shape: {df.shape}")
print(f"columns: {list(df.columns)}")
print(df.head(5).to_string())

print("\n=== get_gamecodes_round(2025, 31) ===")
df2 = gs.get_gamecodes_round(2025, 31)
print(f"shape: {df2.shape}")
print(f"columns: {list(df2.columns)}")
print(df2.to_string())
