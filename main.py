import matplotlib.pyplot as plt
from matplotlib import cm as cm
import math as math
import numpy as np
import urllib3
from NodeClasses import *
from NodeData import *
from PIL import Image
from io import BytesIO
import pprint
from datetime import datetime
import os
from enum import Enum


class ZamimgDatasource(Enum):
    RETAIL = 'enus'
    BETA = 'beta'


def convert_wowgathering_coord_to_xy(coord):
    return math.floor(coord / 10000)/100, math.floor(coord % 10000)/100


def convert_gathermate_coord_to_xy(coord):
    return math.floor(coord/1000000)/10000, math.floor(coord % 1000000 / 100)/10000


def convert_wowhead_coord_to_xy(x, y):
    return x/100.000, y/100.000

def transparent_cmap(cmap, N=255):
    "Copy colormap and set alpha values"
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:,-1] = np.linspace(0, 0.5, N+4)
    return mycmap


# my_db = defaultdict(list)
# my_db[map_name].append(MapNodeLocation(node, coord[0]/100.000, coord[1]/100.000))
map_list = []

# Random objects
"""
356539: "Lush Widowbloom",
"""

herbalism_item_lookup = {
    169701: "Death Blossom",
    170554: "Vigil's Torch",
    168583: "Widowbloom",
    171315: "Nightshade",
    168586: "Rising Glory",
    168589: "Marrowroot",
}

mining_item_lookup = {
    171831: "Phaedrum Ore",
    171833: "Elethium Ore",
    171828: "Laestrite Ore",
    171832: "Sinvyr Ore",
    171829: "Solenium Ore",
    171830: "Oxxein Ore"
}

fishing_item_lookup = {
    173192: "shrouded cloth bandage",
    180168: "oribobber",
    171441: "laestrite skeleton key",
    173032: "lost sole",
    173037: "elysian thade",
    173034: "silvergill pike",
    173035: "pocked bonefish",
    173033: "iridescent amberjack",
    173036: "spinefin piranha",
    173038: "lost sole bait",
    173043: "elysian thade bait",
    173040: "silvergill pike bait",
    173041: "pocked bonefish bait",
    173039: "iridescent amberjack bait",
    173042: "spinefin piranha bait"
}

tag_lookup = {
    'mines': mining_item_lookup,
    'herbs': herbalism_item_lookup,
    'fishing': fishing_item_lookup,
    'all': {**mining_item_lookup, **herbalism_item_lookup, **fishing_item_lookup}
}

def make_folder(path):
    path = os.path.join(path)
    os.makedirs(path, exist_ok=True)
    return path


def parse_tag(tags: List[str], datasource: ZamimgDatasource):
    # Reset parsed nodes in-case of previous run
    reset_nodes()

    # Early exit conditions
    if not len(tags) or datasource is None:
        return

    # Parse all tags passed and scrape associated nodes
    for tag in tags:
        if tag not in tag_lookup:
            print("ERROR: Invalid tag passed.")
            return
        for node_id, name in tag_lookup[tag].items():
            print(f"Scraping data for {name} - {node_id}")
            scrape_map_nodes_from_item(node_id)

    # Make output folder
    output_name = '_'.join(tags)
    path = make_folder(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'))
    stats_path = make_folder(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_includes'))

    # Convert all scrapped nodes into map data
    construct_node_lists_from_wowhead_data()

    # Begin to plot the data
    i = 0
    for map_uid in map_db:
        i += 1
        # print("Parsing map:",map_uid)
        x = []
        y = []
        for node in map_db.get(map_uid).get_nodes():
            x.append(node.x)
            y.append(node.y)
            # print(node)  # DEBUG PRINT
        fig = plt.figure(i, figsize=(10, 4), dpi=200)
        # setup transparent cmap
        mycmap = transparent_cmap(cm.gist_rainbow)

        # import the map image
        img_request = requests.get(f"https://wow.zamimg.com/images/wow/maps/{datasource.value}/original/{map_uid}.jpg")
        img = np.flipud(Image.open(BytesIO(img_request.content)))
        img_extent=[0, 100, 0, 100]

        (ax1, ax2) = fig.subplots(1, 2, sharex=True, sharey=True)
        ax1.imshow(img, extent=img_extent)
        ax2.imshow(img, extent=img_extent)

        binsize = 15
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=binsize)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        square_plot = ax1.imshow(heatmap.T, extent=extent, origin='lower', cmap=mycmap, alpha=1)
        ax1.set_title('Square histogram with %d bins' % binsize)
        fig.colorbar(square_plot, ax=ax1)
        # alternate way to perform heat map
        gridsize = 15
        ax2.set_title('Hex-Grid with %d gridsize' % gridsize)
        hexbin_plot = ax2.hexbin(x, y, gridsize=gridsize, cmap=mycmap, bins=None, facecolor=None)
        # end alternate way to perform heat map
        fig.colorbar(hexbin_plot, ax=ax2)

        plt.gca().invert_yaxis()
        # tmp = plt.scatter(x,y)
        plt.ylim([100, 0])
        plt.xlim([0, 100])
        fig.canvas.set_window_title(map_db[map_uid].name)

        plt.savefig(os.path.join(path, f"{map_db[map_uid].name}-{output_name}.png"), bbox_inches='tight', dpi=fig.dpi)
        plt.show()
        fig.clf()
        plt.close(fig)


    # Output stats to file
    counts = {}
    for map_uid, map_obj in map_db.items():
        counts[map_obj.name] = map_obj.get_counts()
        counts[map_obj.name]['UUID'] = map_uid
    total = sum(count['Total'] for count in counts.values())

    with open(os.path.join(stats_path, f"stats-{output_name}.txt"), 'w') as stats_file:
        header = f"{datetime.now()}, '{output_name}' tag, {len(map_db)} maps, {total} nodes\n"
        # Write to file
        stats_file.write(header)
        pprint.pprint(counts, stream=stats_file)
        # Write to stdout
        pprint.pprint(header)
        pprint.pprint(counts)


if __name__ == "__main__":
    source = ZamimgDatasource.BETA
    parse_tag(['herbs'], source)
    parse_tag(['mines'], source)
    parse_tag(['herbs', 'mines'], source)
    parse_tag(['fishing'], source)
    parse_tag(['all'], source)

