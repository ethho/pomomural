#!/usr/bin/env python3
from __future__ import annotations
from settings import settings

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
        with self.props('draggable').classes('bg-gray-200 w-40 h-35 p-4 rounded shadow cursor-pointer'):
            with ui.row():
                self.select_button = ui.button(on_click =lambda: self.ptr.set_top(self)).props('icon=check').classes('w-6 h-6 bg-green absolute-left')
                ui.label(self.location_dict["name"]).classes('q-ml-xl')
                ui.label(util.get_time_from_seconds(self.location_dict["dur"]))
            # ui.button('Select', on_click =lambda: self.ptr.set_top(self))

    def select(self):
        self.select_button.classes(add='bg-orange', remove='bg-green')

    def deselect(self):
        self.select_button.classes(add='bg-green', remove='bg-orange')

class LargeCard(ui.card):
    def __init__(self,location_dict, idx) -> None:
        super().__init__()
        self.idx = idx
        self.location_dict = location_dict
        self.display()

    def display(self) -> None:
        time = util.get_time_from_seconds(self.location_dict["dur"])
        with self.props('draggable').classes('bg-gray-100 w-40 h-40 p-4 rounded shadow cursor-pointer').style('width: 600px; height: 600px;'):
            self.name = ui.label(self.location_dict["name"])
            self.artist = ui.label(self.location_dict["artist"]).style("font-size:10pt;")
            self.addr = ui.label(self.location_dict["addr"]).style("font-size:10pt;")
            self.markdown = ui.markdown(f"Time taken to reach: {time}")
            #ui.image(self.location_dict["image_url"])
            #ui.image(self.location_dict["maps_url"])
            # print(self.location_dict['img_url'])
            with ui.image(self.location_dict['img_url']).classes('absolute-left').style('height: 80%; top: 20%;') as self.image:
                self.caption = ui.label(self.location_dict['name']).classes('absolute-bottom text-subtitle2 text-center')
        # self.update()

    def update_card(self,location_dict):
        self.location_dict = location_dict
        self.name.text = location_dict["name"]
        self.artist.text = location_dict["artist"]
        self.addr.text = location_dict["addr"]
        time = util.get_time_from_seconds(location_dict["dur"])
        self.markdown.set_content(f"Time taken to reach: {time}")
        self.image.set_source(location_dict['img_url'])
        self.caption.set_text(location_dict['name'])

        self.name.update()
        self.markdown.update()
        self.image.update()
        self.caption.update()
        self.artist.update()
        self.addr.update()


class CardStructure():
    def __init__(self,results) -> None:
        self.results_list = results
        with ui.row():
            self.top_card = LargeCard(self.results_list[0], 0)
            with ui.column():
                self.card_list = [Card(result,self,idx) for idx,result in enumerate(self.results_list)]
        # self.container = ui.row()

    def set_top(self,card) -> None:
        display = False
        self.card_list[self.top_card.idx].deselect() # deselect current
        # print(f"{self.top_card.idx=}")
        if self.top_card == None:
            display = True
            self.top_card.display()
        if display == False:
            self.top_card.update_card(self.results_list[card.idx])
            self.top_card.idx = card.idx
        self.card_list[card.idx].select() # select new

    def display(self) -> None:
        with ui.column():
            for c in self.card_list:
                c.display()
