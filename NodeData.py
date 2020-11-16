import requests
import demjson
import re
import ast
from bs4 import BeautifulSoup
from NodeClasses import *

node_db = {
    349983: 'Sinvyr Deposit',
    350084: 'Rich Sinvyr Deposit',
    349981: 'Oxxein Deposit',
    350085: 'Rich Oxxein Deposit',

}
# map_db = {8721:Map('Drustvar'), 8567:Map('Tiragarde Sound'), 9042:Map('Stormsong Valley')}
map_db = {
    11510: Map('Ardenweald'),
    10413: Map('Revendreth'),
    10534: Map('Bastion'),
    11462: Map('Maldraxxus')
}

herbalism_item_lookup = {
    169701: 'Death Blossom'
}


def make_soup_instance(type_name, obj_id) -> BeautifulSoup:
    url = f"https://shadowlands.wowhead.com/{type_name}={obj_id}"
    hdr = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    page = requests.get(url, headers=hdr)
    return BeautifulSoup(page.text, 'html.parser')


def scrape_short_title_name(type_name, obj_id, soup=None):
    if soup is None:
        soup = make_soup_instance(type_name, obj_id)
    content = soup.find('title')
    if not content:
        raise RuntimeError(f"Could not find title for {type_name} with id {obj_id}")
    return content.contents[0].split('-')[0].strip()


def scrape_map_nodes_from_item(item_id):
    global map_db
    soup = make_soup_instance("item", item_id)
    content = soup.find(text=re.compile("-from-object"))
    if content is None:
        print(f"Could not find content for {item_id}")
        return

    list_views = content.split(';')
    object_info = []
    for view in list_views:
        if '-from-object' in view:
            object_info.extend(ast.literal_eval(re.search('data: (\\[.*\\])', view).group(1)))
    for node in object_info:
        node_id = node['id']
        node_name = node['name']
        node_maps = node['location']

        if node_id not in node_db:
            node_db[node_id] = node_name

        for map_id in node_maps:
            if map_id not in map_db:
                map_db[map_id] = Map(scrape_short_title_name("zone", map_id))


def construct_node_lists_from_wowhead_data():
    for key, value in node_db.items():
        print(f"Parsing node: ({key}: {value})")
        parse_wowhead_data(key)


def parse_wowhead_data(node_id):
    # node_id = 276238
    soup = make_soup_instance("object", node_id)
    soup.prettify()
    text = soup.find(class_='text')
    script_tags = text.find_all('script')
    script = script_tags[1].contents[0]
    js_obj = str(script).split('g_mapperData =')[1].split(';')[0].replace('\n', '').replace(" ", "")
    print("RAW:",js_obj)
    wowhead_data = demjson.decode(js_obj)
    print("PYTHON DICT:",wowhead_data)
    # # add to node db
    # node_db[node_id] = wowhead_data

    # parse coords and add to map_db
    for map_uid in wowhead_data:
        print(map_uid)
        curr_map = map_db.get(int(map_uid), Map('lookup later(id is %s' % map_uid))
        for coord in wowhead_data[map_uid][0].get("coords"):
            print("\t", coord)
            local_node_loc = MapNodeLocation(node_id, coord[0], coord[1])
            curr_map.add_node(local_node_loc)
        map_db[int(map_uid)] = curr_map

    for map_uid in map_db:
        print(map_db[map_uid].node_location_list)
