import requests
import demjson
import re
import ast
from bs4 import BeautifulSoup
from NodeClasses import *
import itertools
from operator import attrgetter
from enum import Enum, auto


class WowheadDatasource(Enum):
   LIVE = 'www'
   PTR = 'ptr'
   BETA = 'shadowlands'


current_source = WowheadDatasource.LIVE


node_db = {}
fish_db = {}
map_db = {
    11510:Map("Ardenweald"),
    10534:Map("Bastion"),
    11462:Map("Maldraxxus"),
    10413:Map("Revendreth"),
    11400:Map("The Maw")
}


classs_to_find = 7


term_info_MINE = dict(name='Metal & Stone', term='WH.TERMS.minedfrom,')
term_info_FISH = dict(name='Cooking', term='WH.TERMS.fishedin,')
term_info_HERB = dict(name='Herb', term='WH.TERMS.gatheredfrom,')


subclass_object_lookup = {
    7: term_info_MINE,
    8: term_info_FISH,
    9: term_info_HERB
}


def reset_nodes():
    global map_db, node_db, fish_db
    for m in map_db.values():
        m.clear()
    #map_db.clear()
    node_db.clear()
    fish_db.clear()


def make_soup_instance(type_name, obj_id) -> BeautifulSoup:
    url = f"https://{current_source.value}.wowhead.com/{type_name}={obj_id}"
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


def scrape_subclass_object(item_id, soup):
    # Define lookups
    item_info_lookup = f'"id":{item_id}'
    classs_regex = re.compile('"classs":([0-9]+),')
    subclass_regex = re.compile('"subclass":([0-9]+),')

    # find subclass and classs based on item_info_lookup
    item_info_js = soup.find(text=re.compile(item_info_lookup))
    if item_info_js is None:
        print(f"Could not find item_info for item_id {item_id}")
        return

    # Since there are multiple js lines in this block, we need to split the data and find right lines
    classs, subclass = None, None
    for line in item_info_js.split(';'):
        if item_info_lookup in line:
            # classs = int(re.search(classs_regex, line).group(1))
            subclass = int(re.search(subclass_regex, line).group(1))
            break

    # Exit if not in lookup or invalid classs
    valid_classs = (classs == classs_to_find)
    valid_subclass = (subclass in subclass_object_lookup)
    if not (valid_subclass):
        print(f"Item_id {item_id} does not have correct class/subclass. Classs=[{classs}]; Subclass=[{subclass}]")
        return None

    return subclass_object_lookup[subclass]


def scrape_gathered_data_from_term(soup, term):
    # Find data based on passed term
    content = soup.find(text=re.compile(term))
    if content is None:
        return None

    # Since there can be multiple lines in this ListView, we need to split and find valid lines
    list_views = content.split(';')
    object_info = []
    for view in list_views:
        if term in view:
            object_info.extend(ast.literal_eval(re.search('data: (\\[.*\\])', view).group(1)))

    return object_info


def parse_fished_from_gathered_data(gathered_data, item_id):
    global fish_db, map_db
    for node in gathered_data:
        map_id = node['id']

        if item_id not in fish_db:
            fish_db[item_id] = None
        if map_id == -1:
            print(f"ERROR: item {item_id} is mapped to an invalid map id {map_id}. Skipping this map.")
            continue
        if map_id not in map_db:
            map_db[map_id] = Map(scrape_short_title_name("zone", map_id))


def parse_nodes_from_gathered_data(gathered_data):
    # TODO: Return data from this function and cache data based on the term used to find the data.
    global node_db, map_db
    for node in gathered_data:
        node_id = node['id']
        node_name = node['name']
        node_maps = node['location']

        if node_id not in node_db:
            node_db[node_id] = node_name

        for map_id in node_maps:
            if map_id == -1:
                print(f"ERROR: {node_id} '{node_name}' is mapped to an invalid map id {map_id}. Skipping this map.")
                continue
            if map_id not in map_db:
                map_db[map_id] = Map(scrape_short_title_name("zone", map_id))


def scrape_map_nodes_from_item(item_id):
    soup = make_soup_instance("item", item_id)

    subclass_object = scrape_subclass_object(item_id, soup)
    if subclass_object is None:
        return

    gathered_data = scrape_gathered_data_from_term(soup, subclass_object['term'])
    if gathered_data is None:
        print(f"No valid nodes found for {item_id}")
        return

    if subclass_object['term'] == term_info_FISH['term']:
        parse_fished_from_gathered_data(gathered_data, item_id)
    else:
        parse_nodes_from_gathered_data(gathered_data)


# def scrape_map_nodes_from_item(item_id):
#     global map_db, node_db
#     soup = make_soup_instance("item", item_id)
#     content = soup.find(text=re.compile("-from-object"))
#     if content is None:
#         print(f"Could not find content for {item_id}")
#         return
#
#     list_views = content.split(';')
#     object_info = []
#     for view in list_views:
#         if '-from-object' in view:
#             object_info.extend(ast.literal_eval(re.search('data: (\\[.*\\])', view).group(1)))
#     for node in object_info:
#         node_id = node['id']
#         node_name = node['name']
#         node_maps = node['location']
#
#         if node_id not in node_db:
#             node_db[node_id] = node_name
#
#         for map_id in node_maps:
#             if map_id == -1:
#                 print(f"ERROR: {node_id} '{node_name}' is mapped to an invalid map id {map_id}. Skipping this map.")
#                 continue
#             if map_id not in map_db:
#                 map_db[map_id] = Map(scrape_short_title_name("zone", map_id))


def construct_node_lists_from_wowhead_data():
    for key, value in node_db.items():
        #print(f"Parsing node: ({key}: {value})")
        parse_wowhead_data(key)

    for key in fish_db:
        #print(f"Parsing item: {key}")
        parse_wowhead_data(key, node_type="item")

    for map_uid in map_db:
        data = sorted(map_db[map_uid].node_set, key=attrgetter('name', 'x', 'y'))
        output = "\n\t".join(f"{k}: {list(g)}" for k, g in itertools.groupby(data, attrgetter('name')))
        #print(f"Map: {map_db[map_uid].name}\n\t{output}")


def parse_wowhead_data(node_id, node_type="object"):
    # node_id = 276238
    soup = make_soup_instance(node_type, node_id)
    soup.prettify()
    text = soup.find(class_='text')
    script_tags = text.find_all('script')
    script = None
    for tag in script_tags:
        for content in tag.contents:
            if "g_mapperData" in content:
                script = content
                break
    script = str(script)
    mapperdata = script.split('g_mapperData =')[1]
    mapperdata = mapperdata.split(';')[0]
    mapperdata = mapperdata.replace('\n', '')
    js_obj = mapperdata.replace(" ", "")
    # js_obj = str(script).split('g_mapperData =')[1].split(';')[0].replace('\n', '').replace(" ", "")
    # print("RAW:",js_obj)  # DEBUG PRINT
    wowhead_data = demjson.decode(js_obj)
    # print("PYTHON DICT:",wowhead_data)  # DEBUG PRINT
    # # add to node db
    # node_db[node_id] = wowhead_data

    # parse coords and add to map_db
    for map_uid in wowhead_data:
        # print(map_uid)  # DEBUG PRINT
        data = wowhead_data[map_uid][0].get("coords")
        if not len(data):
            continue

        # Make a map entry in the database
        curr_map = map_db.get(int(map_uid), Map('lookup later(id is %s' % map_uid))
        for coord in data:
            # print("\t", coord)  # DEBUG PRINT
            local_node_loc = MapNodeLocation(node_id, coord[0], coord[1])
            curr_map.add_node(local_node_loc)
        map_db[int(map_uid)] = curr_map



