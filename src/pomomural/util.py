def get_time_from_seconds(seconds:float)->str:
	mins = int(seconds)//60
	hours = mins//60
	mins_to_hour = mins%60
	return f"Time taken to reach: {hours:02d}:{mins_to_hour:02d}"
