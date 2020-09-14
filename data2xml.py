import xml.etree.ElementTree as ET
import skimage as ski
import re
from skimage import io
from os import listdir
from os.path import isfile, join
import numpy as np
import cv2


def parseGaofen(annotation_filepath, filepath):
    tree = ET.parse(annotation_filepath)
    img = io.imread(filepath)
    root = tree.getroot()
    metadata = {}

    # source
    source = {}
    source['filename'] = root.find("./source/filename").text
    source['origin'] = root.find("./source/origin").text

    # research
    research = {}
    research['version'] = root.find("./research/version").text
    research['provider'] = root.find("./research/provider").text
    research['author'] = root.find("./research/author").text
    research['pluginname'] = root.find("./research/pluginname").text
    research['time'] = root.find("./research/time").text

    # size
    size = {'width': img.shape[0], 'height': img.shape[1], 'depth': 1}
    metadata['size'] = size
    # objects vector
    objects = []
    # objects
    for gaofen_obj in root.findall("./objects/object"):
        voc_obj = {}
        xs = []
        ys = []
        # names
        voc_obj['coordinate'] = gaofen_obj.find("./coordinate").text
        voc_obj['type'] = gaofen_obj.find("./type").text
        voc_obj['description'] = gaofen_obj.find("./description").text
        possibleresult = {}
        possibleresult['name'] = gaofen_obj.find("./possibleresult/name").text
        voc_obj['possibleresult'] = possibleresult

        # points
        points = []
        for point in gaofen_obj.findall('./points/point'):
            ints = [int(p) for p in point.text.split(sep=", ")]
            points.append(ints)
        voc_obj['points'] = points
        objects.append(voc_obj)
    metadata['source'] = source
    metadata['research'] = research
    metadata['objects'] = objects
    return metadata


# for references visit -> https://docs.python.org/2/library/xml.etree.elementtree.html#modifying-an-xml-file
# metadata is a python dictionary from a Gaofen Annotation
def toPascalVOC(metadata):
    voc_annotation = ET.Element('annotation')
    folder = ET.SubElement(voc_annotation, 'folder')
    filename = ET.SubElement(voc_annotation, 'filename')
    filename.text = metadata['source']['filename']
    path = ET.SubElement(voc_annotation, 'path')

    source = ET.SubElement(voc_annotation, 'source')
    database = ET.SubElement(source, 'database')

    size = ET.SubElement(voc_annotation, 'size')
    width = ET.SubElement(size, 'width')
    height = ET.SubElement(size, 'height')
    depth = ET.SubElement(size, 'depth')

    width.text = str(metadata['size']['width'])
    height.text = str(metadata['size']['height'])
    depth.text = str(metadata['size']['depth'])

    segmented = ET.SubElement(voc_annotation, 'segmented')
    segmented.text = '0'

    for i, obj in enumerate(metadata['objects']):
        voc_obj = ET.SubElement(voc_annotation, 'object')
        name = ET.SubElement(voc_obj, 'name')
        name.text = obj['possibleresult']['name']
        pose = ET.SubElement(voc_obj, 'pose')
        truncated = ET.SubElement(voc_obj, 'truncated')
        difficult = ET.SubElement(voc_obj, 'difficult')
        difficult.text = obj['difficult'] if 'difficult' in obj else '0'

        bndbox = ET.SubElement(voc_obj, 'bndbox')
        xs = []
        ys = []
        for point in obj['points']:
            xs.append(point[0])
            ys.append(point[1])
        min_max = {
            'xmin': min(xs),
            'ymin': min(ys),
            'xmax': max(xs),
            'ymax': max(ys),
        }
        for attr, value in min_max.items():
            p = ET.SubElement(bndbox, attr)
            p.text = str(value)
    return voc_annotation

def toRGB8(filepath, out_path):
    bw = cv2.imread(filepath, -1)
    image = np.uint8(np.stack((bw,bw,bw), axis=2))
    name = re.search('\w*(?=\.)', filepath).group(0)
    cv2.imwrite(f'{out_path}/{name}.jpg', image)


gaofen_root = 'C:\\Users\\juliadnoce\\Documents\\original'
path = gaofen_root + '\\data\\val\\'
out_path = gaofen_root + '\\data\\out\\'


onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
print(onlyfiles)
for f in onlyfiles:
  m = re.search('(\w+)\.tiff', f)
  if(m):
      print(m.group(1))
      toRGB8(path + m.group(0), out_path)
#
# onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
# print(onlyfiles)
# for f in onlyfiles:
#     m = re.search('(\w+)\.xml', f)
#     if (m):
#         print(m.group(1))
#         f = open(f'{gaofen_root}/data/out/{m.group(1)}.xml', 'w')
#         f.write(ET.tostring(toPascalVOC(parseGaofen(f'{path}/{m.group(1)}.xml', f'{out_path}/{m.group(1)}.jpg')),
#                             encoding='utf8').decode('utf8'))
#         f.close()
#         # except:
#         #     print(m.group(0) + ' unable to Parse.')
