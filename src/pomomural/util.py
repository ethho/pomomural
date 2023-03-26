def get_time_from_seconds(seconds:float)->str:
	mins = int(seconds)//60
	hours = mins//60
	mins_to_hour = mins%60
	return f"{mins_to_hour} mins"
