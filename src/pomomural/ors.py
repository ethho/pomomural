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

if __name__ == '__main__':
    _test_otm_distance_matrix()
    # _test_get_geocode_circular()