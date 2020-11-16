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
    171832: "Sinvyr Ore",   # These weren't really tracked well
    171829: "Solenium Ore",
    171830: "Oxxein Ore"
}

outputs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')


def make_output_folder(folder_name: str):
    path = os.path.join(outputs_path, folder_name)
    os.makedirs(path, exist_ok=True)
    return path


def parse_tag(tag: str):
    # plt.clf()

    if tag not in ['all', 'herbs', 'mines']:
        print("ERROR: Invalid tag passed.")
        return

    if tag == 'all' or tag == 'herbs':
        for node_id, name in herbalism_item_lookup.items():
            scrape_map_nodes_from_item(node_id)

    if tag == 'all' or tag == 'mines':
        for node_id, name in mining_item_lookup.items():
            scrape_map_nodes_from_item(node_id)

    path = make_output_folder(tag)

    construct_node_lists_from_wowhead_data()

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
        fig = plt.figure(i, figsize=(10,4), dpi=200)
        # setup transparent cmap
        mycmap = transparent_cmap(cm.gist_rainbow)
        # import the map image
        # img_request = requests.get("https://wow.zamimg.com/images/wow/maps/enus/original/"+map_uid.__str__()+".jpg")
        img_request = requests.get(f"https://wow.zamimg.com/images/wow/maps/beta/original/{map_uid}.jpg")
        img = np.flipud(Image.open(BytesIO(img_request.content)))
        img_extent=[0, 100, 0, 100]
        # I = Image.open("drustvar.jpg")
        # p = np.asarray(I).astype('float')

        (ax1, ax2) = fig.subplots(1,2,sharex=True,sharey=True)
        ax1.imshow(img, extent=img_extent)
        ax2.imshow(img, extent=img_extent)

        binsize = 15
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=binsize)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        square_plot = ax1.imshow(heatmap.T, extent=extent, origin='lower', cmap=mycmap, alpha=.8)
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

        plt.savefig(os.path.join(path, f"{map_db[map_uid].name}-{tag}.png"), bbox_inches='tight', dpi=fig.dpi)
        fig.clf()
        plt.close(fig)
    # plt.show()

    # Output stats to file
    counts = {}
    for map_uid, map_obj in map_db.items():
        counts[map_obj.name] = map_obj.get_counts()
        counts[map_obj.name]['UUID'] = map_uid
    total = sum(count['Total'] for count in counts.values())

    with open("outputs/stats.txt", 'w') as stats_file:
        header = f"{datetime.now()}, '{tag}' tag, {len(map_db)} maps, {total} nodes"
        # Write to file
        stats_file.write(header)
        pprint.pprint(counts, stream=stats_file)
        # Write to stdout
        pprint.pprint(header)
        pprint.pprint(counts)


if __name__ == "__main__":
    # global map_db, node_db

    reset_nodes()
    parse_tag('herbs')

    reset_nodes()
    parse_tag('mines')

    reset_nodes()
    parse_tag('all')

