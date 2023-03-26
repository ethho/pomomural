#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from nicegui import ui

import util

class Card(ui.card):
    def __init__(self, location_dict, ptr) -> None:
        super().__init__()
        self.location_dict = location_dict
        self.ptr = ptr
        self.display()
        
    def display(self) -> None:
        with self.props('draggable').classes('bg-gray-200 w-48 p-4 rounded shadow cursor-pointer'):
            ui.button(self.location_dict["name"], on_click =lambda: self.ptr.set_top(self))

class LargeCard(ui.card):
    def __init__(self,location_dict) -> None:
        super().__init__()
        self.location_dict = location_dict

    def display(self) -> None:
        with self.props('draggable').classes('bg-gray-200 w-80 p-4 rounded shadow cursor-pointer'):
            ui.label(self.location_dict["name"]).style("font-size:12pt;")
            #ui.label(self.location_dict["artist"]).style("font-size:10pt;")
            #ui.label(self.location_dict["addr"]).style("font-size:10pt;")
            #ui.markdown("Time taken to reach : ",util.get_time_from_seconds(self.location_dict["dur"]))
            #ui.image(self.location_dict["image_url"])
            #ui.image(self.location_dict["maps_url"])        
                
class CardStructure():
    def __init__(self,results) -> None:
        self.results_list = results
        with ui.column():
            self.card_list = [Card(result,self) for result in self.results_list]
        self.top_card = None
        self.container = ui.row()

    def set_top(self,card) -> None:
        self.top_card = card
        self.container.clear
        print("Container cleared")
        with self.container:
            self.top_card.display()

    def display(self) -> None:   
        with ui.column():
            for c in self.card_list:
                c.display()