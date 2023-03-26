from typing import Optional

from nicegui import ui

def get_time_from_seconds(seconds:float)->str:
	mins = seconds/60
	hours = mins/60
	mins_to_hour = mins%60
	return f"{hours}:{mins_to_hour}"
