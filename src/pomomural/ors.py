import csv
import requests
from pprint import pprint
from memoize import memoize
import openrouteservice
from openrouteservice.distance_matrix import distance_matrix
from openrouteservice.geocode import pelias_search
from settings import settings

ors_client = openrouteservice.Client(key=settings.ORS_KEY)

@memoize(cache_lifetime_days=None, cache_dir='/tmp/memoize')
def get_directions(
    origin,
    dest,
    profile='foot-walking',
    **kw
):
    routes = ors_client.directions(
        (origin, dest),
        profile=profile,
        **kw
    )

    # Traveling salesman
    # coords = ((8.34234,48.23424),(8.34423,48.26424), (8.34523,48.24424), (8.41423,48.21424))
    # client = openrouteservice.Client(key='') # Specify your personal API key
    # routes = client.directions(coords, profile='cycling-regular', optimize_waypoints=True)

    return routes

@memoize(cache_lifetime_days=None, cache_dir='/tmp/memoize')
def get_otm_distance_matrix(
    origin,
    dests,
    metrics=None,
    profile='foot-walking',
    **kw
):
    """
    Origin and dests are in (lon,lat)
    Return 'duration' is in seconds.
    """
    metrics = metrics if metrics is not None else ['distance', 'duration']
    locs = [origin] + dests
    matrix = distance_matrix(
        client=ors_client,
        locations=locs,
        sources=[0],
        destinations=list(range(1, len(locs))),
        profile=profile,
        metrics=metrics,
        units='mi',
        **kw
    )
    return matrix

@memoize(cache_lifetime_days=None, cache_dir='/tmp/memoize')
def get_geocode_circular(
    query: str,
    center=None,
    radius=80, # km = ~50 miles
    **kw
):
    """
    https://github.com/pelias/documentation/blob/master/search.md#prioritize-within-a-circular-region
    """
    # Center defaults to Al's Italian Beef in the Loop
    center = center if center is not None else (-87.62514674683162, 41.92148133715662)
    return pelias_search(
        ors_client,
        text=query,
        focus_point=center,
        # rect_min_x=None,
        # rect_min_y=None,
        # rect_max_x=None,
        # rect_max_y=None,
        circle_point=center,
        circle_radius=radius,
        sources=['osm'],
        # layers=None,
        country='US',
        size=5,
        validate=True,
    )

def _test_directions():
    pprint(get_directions(
        origin=(8.34234, 48.23424),
        dest=(8.34423, 48.26424),
        profile='foot-walking',
        # profile='cycling-regular',
    ))

def _test_otm_distance_matrix():
    raw = get_otm_distance_matrix(
        # Salonica
        origin=(-87.59042435642392, 41.79237034197231),
        dests=[
            # Lake Geneva
            (-88.54468274754518, 42.59662527196502),
            # Polsky Exchange North
            (-87.58970524855233, 41.80008342543928),
        ],
        profile='foot-walking',
    )
    pprint(raw)
    dist = raw['distances']
    dur = raw['durations']
    # breakpoint()

def _test_get_geocode_circular():
    result = get_geocode_circular(
        query='Polsky Exchange North',
    )
    latlon = result['features'][0]['geometry']['coordinates']
    name = result['features'][0]['properties']['label']
    # breakpoint()
    pprint(result)
    print(f"Actual: -87.58970524855232, 41.80008342543928")

def _test_parse_mural_registry():
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
            img_url=row[17],
            # img_url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fcdn.theculturetrip.com%2Fwp-content%2Fuploads%2F2016%2F12%2Fgt_chicago.jpg&f=1&nofb=1&ipt=b28a0928ecd49643db0fc18b1ba1d79d6370c97f12dcf9830f01fa96f14d6915&ipo=images',
        )
        for row in rows
    ]
    # TODO: form Google Maps URL
    breakpoint()
    return parsed

def _test_get_divvy_locs():
    url = 'https://gbfs.divvybikes.com/gbfs/en/free_bike_status.json'
    resp = requests.get(url)
    bikes = resp.json()['data']['bikes']
    bike = bikes[0]
    # {'bike_id': 'b1eead00baebddf6a35483c3a62394ce',
    # 'fusion_lat': 0,
    # 'fusion_lon': 0,
    # 'is_disabled': 0,
    # 'is_reserved': 0,
    # 'lat': 41.910975933,
    # 'lon': -87.653251171,
    # 'name': 'b1eead00baebddf6a35483c3a62394ce',
    # 'rental_uris': {'android': 'https://chi.lft.to/lastmile_qr_scan',
    #                 'ios': 'https://chi.lft.to/lastmile_qr_scan'},
    # 'type': 'electric_bike'}
    breakpoint()

if __name__ == '__main__':
    # _test_otm_distance_matrix()
    # _test_get_geocode_circular()
    reg = _test_parse_mural_registry()
    # breakpoint()
    # _test_get_divvy_locs()