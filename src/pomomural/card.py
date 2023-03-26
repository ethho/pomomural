#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from nicegui import ui

import util

class Card(ui.card):
    def __init__(self, location_dict, ptr,card_idx) -> None:
        super().__init__()
        self.location_dict = location_dict
        self.ptr = ptr
        self.idx = card_idx
        self.display()

    def display(self) -> None:
        with self.props('draggable').classes('bg-gray-200 w-48 p-4 rounded shadow cursor-pointer'):
            ui.button(self.location_dict["name"], on_click =lambda: self.ptr.set_top(self))

class LargeCard(ui.card):
    def __init__(self,location_dict) -> None:
        super().__init__()
        self.location_dict = location_dict
        self.display()

    def display(self) -> None:
        with self.props('draggable').classes('bg-gray-200 w-80 h-80 p-8 rounded shadow cursor-pointer'):
            self.name = ui.label(self.location_dict["name"])
            #ui.label(self.location_dict["artist"]).style("font-size:10pt;")
            #ui.label(self.location_dict["addr"]).style("font-size:10pt;")
            self.markdown = ui.markdown(util.get_time_from_seconds(self.location_dict["dur"]))
            #ui.image(self.location_dict["image_url"])
            #ui.image(self.location_dict["maps_url"])        
    
    def update_card(self,location_dict):
        self.name.text = location_dict["name"]
        self.markdown.text = util.get_time_from_seconds(location_dict["dur"])

        self.name.update()
        self.markdown.update()


class CardStructure():
    def __init__(self,results) -> None:
        self.results_list = results
        with ui.row():
            self.card_list = [Card(result,self,idx) for idx,result in enumerate(self.results_list)]
        self.top_card = LargeCard(self.results_list[0])
        self.container = ui.row()

    def set_top(self,card) -> None:
        display = False
        if self.top_card == None:
            display = True
        if display == False:
            self.top_card.update_card(self.results_list[card.idx])
        self.top_card.display()

    def display(self) -> None:   
        with ui.column():
            for c in self.card_list:
                c.display()
