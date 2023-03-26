import csv
import re
import asyncio
import requests
from time import sleep
from nicegui import ui
from memoize import memoize
from settings import settings
from ors import get_geocode_circular, get_otm_distance_matrix
from card import Card,LargeCard,CardStructure

async def get_location_from_browser(
    *args,
    niters=10,
    sleep_between_iters=0.1,
    **kw,
):
    loc_fetch_js = f"""
    var x = document.getElementById("{invisible_label.id}");

    function getLocation() {{
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(
                // Success function
                showPosition,
                // Error function
                null,
                // Options. See MDN for details.
                {{
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 0
                }});
        }} else {{
            x.innerHTML = "Geolocation is not supported by this browser.";
            x.latitude = null;
            x.longitude = null;
        }}
    }}

    function showPosition(position) {{
        x.latitude = position.coords.latitude;
        x.longitude = position.coords.longitude;
    }}

    getLocation();
    """
    await ui.run_javascript(loc_fetch_js, respond=False)
    latlon = None
    for _ in range(niters):
        try:
            latlon = await ui.run_javascript(
                f'var x = getElement({invisible_label.id});'
                'x.latitude + "," + x.longitude;'
            )
        except Exception as e:
            latlon = None
        else:
            if latlon is not None and latlon != 'undefined,undefined':
                break
        sleep(sleep_between_iters)
    else:
        ui.notify(f'Could not fetch lat/lon from browser')
        return (None, None)
    lat, lon = [float(val) for val in latlon.split(',')]
    # ui.notify(f'Fetched location: {(lat, lon)}')
    return (lat, lon)

async def resolve_starting_loc_input(query: str):
    # Check if query looks like lat/lon e.g. '-33.856680,151.215281'
    matches = re.findall(r'^\s*\(?\s*(\-?\d+\.?\d*)\s*,\s*(\-?\d+\.?\d*)\s*\(?\s*$', query)
    if matches:
        latlon = [float(val) for val in matches[0]]
        if len(latlon) == 2:
            return dict(
                lat=latlon[0],
                lon=latlon[1],
                name=None,
            )

    # Fallback on geocode API
    result = get_geocode_circular(query=query)
    try:
        lonlat = result['features'][0]['geometry']['coordinates']
        name = result['features'][0]['properties']['label']
    except (KeyError, AttributeError) as e:
        raise e
    return dict(
        lat=lonlat[1],
        lon=lonlat[0],
        name=name,
    )


@memoize(cache_dir='/tmp/memoize')
def get_mural_pois():
    with open(settings.MURAL_CSV_FP, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = list(reader)[1:]
    parsed = [
        dict(
            id=int(row[0]),
            artist=row[1],
            title=row[2],
            name=row[2],
            media=row[3],
            year_inst=int(row[4]) if row[4] else None,
            year_rest=row[5],
            loc_desc=row[6],
            addr=row[7],
            zip=row[8],
            ward=int(row[9]),
            aff_org=row[10],
            desc=row[11],
            comm_areas=row[12],
            lat=float(row[13]),
            lon=float(row[14]),
            loc=row[15],
            # dalle_img_url=row[16],
            img_url=row[17] if row[17] else settings.NOT_FOUND_IMG,
            # img_url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.theculturetrip.com%2Fwp-content%2Fuploads%2F2016%2F12%2Fgt_chicago.jpg&f=1&nofb=1&ipt=b28a0928ecd49643db0fc18b1ba1d79d6370c97f12dcf9830f01fa96f14d6915&ipo=images',
        )
        for row in rows
    ]
    # TODO: form Google Maps URL
    return parsed

# TODO
# @memoize(cache_dir='/tmp/memoize')
def _get_mural_pois_mock():
    with open(settings.MURAL_CSV_FP, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))
    # TODO
    return [
        dict(
            # name='Polsky Exchange North',
            name='<a href="http://example.com" style="text-decoration: underline;">Polsky Exchange North</a>',
            lon=-87.58970524855232,
            lat=41.80008342543928,
        ),
        dict(
            # name='Random place in Lake Geneva',
            name='<a href="http://example.com" style="text-decoration: underline;">Random place in Lake Geneva</a>',
            lon=-88.54468274754518,
            lat=42.59662527196502,
        ),
    ]

def get_gmaps_url(poi, center, profile) -> str:
    # %2C is comma
    cent = f"{center[1]}%2C{center[0]}"
    dest = f"{poi['lat']}%2C{poi['lon']}"

    # Get travelmode
    if profile == 'foot-walking':
        tmode = 'walking'
    elif profile == 'cycling-regular':
        tmode = 'bicycling'
    else:
        raise Exception(f"Disallowed {profile=}")

    url = f"https://www.google.com/maps/dir/?api=1&origin={cent}&destination={dest}&travelmode={tmode}"
    # DEBUG
    # print(f'{url=}')
    return url


def find_nearest_mural(
    center=None,
    profile='foot-walking',
):
    # Get mural coordinates for destination
    pois = get_mural_pois()
    dests = [(item['lon'], item['lat']) for item in pois]
    # Salonica by default
    center = center if center is not None else (-87.59042435642392, 41.79237034197231)
    raw = get_otm_distance_matrix(
        origin=center,
        dests=dests,
        profile=profile,
    )
    dists = raw['distances'][0]
    durs = raw['durations'][0]
    if not dists or not durs:
        raise Exception(f'Found no routes from {center=}')
    for poi, dist, dur in zip(pois, dists, durs):
        poi['dist'] = dist
        poi['dur'] = dur * 2
        poi['gmaps_url'] = get_gmaps_url(poi, center, profile)
    pois = sorted(pois, key=lambda x: x.get('dur', 1e8), reverse=False)
    return pois

def get_divvy_locs():
    # TODO
    return []

def find_nearest_divvy(
    center=None,
    profile='foot-walking',
):
    # Get Divvy bike coordinates for destination
    bikes = get_divvy_locs()
    dests = [(item['lon'], item['lat']) for item in bikes]
    # Salonica by default
    center = center if center is not None else (-87.59042435642392, 41.79237034197231)
    raw = get_otm_distance_matrix(
        origin=center,
        dests=dests,
        profile=profile,
    )
    dists = raw['distances'][0]
    durs = raw['durations'][0]
    if not dists or not durs:
        raise Exception(f'Found no routes to Divvy bikes from {center=}')
    for bike, dist, dur in zip(bikes, dists, durs):
        bike['dist'] = dist
        bike['dur'] = dur
        bike['gmaps_url'] = get_gmaps_url(bike, center, profile)
    bikes = sorted(bikes, key=lambda x: x.get('dur', 1e8), reverse=False)
    return bikes

def render_results(results, **kw):
    return render_results_as_card(results, **kw)
    # return render_results_as_table(results)

def render_results_as_card(results, lat=None, lon=None):
    results_row.clear()
    results_row.classes(remove='hidden')
    with results_row:
        structure = CardStructure(results, lat=lat, lon=lon)
    return

def render_results_as_table(results):
    columns = [
        # {'name': 'lat', 'label': 'Lat', 'field': 'lat', 'required': True, 'align': 'left'},
        # {'name': 'lon', 'label': 'Lon', 'field': 'lon', 'sortable': True},
        {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True, 'align': 'left', 'width': 300},
        {'name': 'dist', 'label': 'Distance (mi)', 'field': 'dist', 'sortable': True, 'align': 'left'},
        {'name': 'dur', 'label': 'Duration (sec)', 'field': 'dur', 'sortable': True, 'align': 'left'},
        # {'name': 'lat', 'label': 'Lat', 'field': 'lat', 'sortable': False, 'align': 'left'},
        # {'name': 'lon', 'label': 'Lon', 'field': 'lon', 'sortable': False, 'align': 'left'},
    ]
    results_ui_expansion.clear()
    results_ui_expansion.set_value(True)
    results_ui_expansion.classes(remove='hidden')
    with results_ui_expansion:
        # ui.table(
        #     columns=columns, rows=results,
        #     html_columns=[0],
        #     row_key='name',
        # )
        grid = ui.aggrid({
            'columnDefs': columns,
            'rowData': results,
            'rowSelection': 'single',
        }, theme='ag-theme-material', html_columns=[0])
        grid.update()
        # ui.notify(grid.get_selected_row())
    results_ui_expansion.update()

async def submit_form():
    """
    Event loop that triggers when "Find Nearest Mural" is clicked.
    """
    # Open loading dialogue
    dialog.open()
    await asyncio.sleep(1.5)
    dialog.close()

    # Get starting location coords
    loc_raw = starting_loc_input.value
    name = None
    if loc_raw:
        loc = await resolve_starting_loc_input(loc_raw)
        lat, lon = loc['lat'], loc['lon']
        name = loc.get('name', None)
        if name:
            ui.notify(f"Resolved location to: {name}")
    else:
        # Try to fetch location from user's browser
        lat, lon = await get_location_from_browser()
        if lat is None and lon is None:
            ui.notify(f"Please enter a starting location, or allow location access and reload the page.")
            return
    ui.notify(f"Resolved coordinates: {(lat, lon)}")

    # Get profile from radio button element
    prof_val = profile_radio.value
    if prof_val == 1:
        profile = 'foot-walking'
    elif prof_val == 2:
        profile = 'cycling-regular'
    else:
        raise Exception(f"Unsupported profile selection with value: {prof_val}")
    # ui.notify(profile)

    # Find nearest mural
    results = find_nearest_mural(
        center=[lon, lat],
        profile=profile,
    )[:settings.MAX_RESULTS]
    # ui.notify(results)
    # DEBUG
    # print(f"Found {len(results)} results: {results}")

    # Render results
    render_results(results, lat=lat, lon=lon)

# Quasar color scheme
ui.colors(
    primary='green',
    secondary='red',
    accent='blue',
)

@ui.page('/')
def index_page():
    # ui.label('Hello, world!')
    # We use an invisible label to pass shared state variables
    global invisible_label
    invisible_label = ui.label()
    invisible_label.profile_id = 0

    # Body content
    ui.markdown('''Plan a walk/ride to a nearby public art piece during your Pomodoro break!\n\n----\n\n''').style('width: 80%;')

    # ui.label('How long is your break?')
    # with ui.row().style('width: 100%;'):
    #     slider = ui.slider(min=5, max=60, value=30).props('color=orange').classes('col')
    #     ui.label().bind_text_from(slider, 'value', backward=lambda x: f"{x} minutes").classes('col q-pt-xs q-pl-xs')

    global profile_radio
    with ui.row():
        ui.label('I want to').classes('q-pt-sm')
        profile_radio = ui.radio({
            1: 'Walk',
            2: 'Bike',
        }, value=1).props('inline color=light-green-6')
    global starting_loc_input
    starting_loc_input = ui.input(
        label='Enter starting location (optional)',
        placeholder='Examples: Polsky Exchange North, 1103 E 57th St., (41.7964,-87.5985)',
        # on_change=lambda e: result.set_text('you typed: ' + e.value),
        # validation={'Input too long': lambda value: len(value) < 20},
    ).style('width: 80%')
    ui.button('find nearest mural', on_click=submit_form).props('color=purple-5')
    global dialog
    with ui.dialog() as dialog, ui.card():
        ui.label('Finding a mural near you...')
        ui.spinner('dots', size='xl', color='default').props('color=deep-purple').classes('q-ml-xl')

    global results_ui_expansion
    results_ui_expansion = ui.expansion('All Nearby Murals', icon='drag_indicator').classes('w-full hidden')
    results_ui_expansion.clear()
    results_ui_expansion.update()
    global results_row
    results_row = ui.row().classes('hidden').style('width: 100%;')
    results_row.clear()
    results_row.update()

    # TODO: pretty animation for starting location placeholder text

    # Header
    with ui.header(elevated=True).style('background-color: #3874c8; background-image: url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fs.inyourpocket.com%2Fgallery%2Fpisa%2F2020%2F02%2FKeith%2520Haring%27s%2520Tuttomondo%2520Mural-1.jpg&f=1&nofb=1&ipt=377a590a023b15027d4114a17993a41eea4ee78fbf1af7315265762d502a129c&ipo=images");').classes('items-center justify-between'):
        # ui.label('HEADER')
        ui.label('PomoMural').style('color: #fe9ffa; font-size: 17pt;')
        ui.button(text='Menu', on_click=lambda: right_drawer.toggle()).props('flat color=white icon=menu')

    # Right drawer
    with ui.right_drawer(value=False, fixed=False).style('background-color: #ebf1fa; background-image: none;').props('bordered') as right_drawer:
        ui.markdown(
            '#### Links\n\n'
            '- [PomoMural GitHub](https://github.com/ethho/pomomural)\n'
            '- [Uncommon Hacks 2023](https://github.com/ethho/pomomural)\n'
        )
        ui.markdown(
            '#### Tools & Data Sources\n\n'
            '- [Chicago Data Portal](https://data.cityofchicago.org/)\n'
            '- [Chicago Mural Registry](https://www.chicago.gov/city/en/depts/dca/supp_info/mural_registry1.html)\n'
            '- [NiceGUI](https://nicegui.io/)\n'
            '- [Heroku](https://www.heroku.com/github-students)\n'
            '- [wttr.in](https://github.com/chubin/wttr.in)\n'
        )
        ui.markdown(
            '#### Authors\n\n'
            '- [Ethan Ho](https://github.com/ethho/)\n'
            '- [Ajay Sailopal](https://github.com/Ajay-26)\n'
            '- [Brian Whitehouse](https://github.com/btwhitehouse2)\n'
        )

    # Footer
    with ui.footer().style('background-color: #3874c8; background-image: url("https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fs.inyourpocket.com%2Fgallery%2Fpisa%2F2020%2F02%2FKeith%2520Haring%27s%2520Tuttomondo%2520Mural-1.jpg&f=1&nofb=1&ipt=377a590a023b15027d4114a17993a41eea4ee78fbf1af7315265762d502a129c&ipo=images");'):
        # ui.label('FOOTER')
        pass

# Kick off async processes that cache
get_mural_pois()

ui.run(
    port=settings.PORT,
    title='PomoMural - Plan a Trip to a Mural in Chicago'
)
