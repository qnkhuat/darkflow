import matplotlib.pyplot as plt
import numpy as np
import os
import re
import pandas as pd
import scipy.io as io
from pprint import pprint
import shutil as sh
import random
import argparse
import xml.etree.cElementTree as ET
import cv2
import time


def misc():
    data_labels = io.loadmat(os.path.join(data_path,'misc/make_model_name'))
    model_names = data_labels['model_names']
    make_names = data_labels['make_names']
    return model_names,make_names


def get_idx_for_make(choose):
    '''
    choose : list of car makes to get

    return {make_idx : make_name}
    '''
    model_name,make_model = misc()
    #make id that I chose to class
    make_relation_dict = { idx +1:make[0][0].lower().strip() for idx,make in enumerate(make_model) if make[0][0].lower().strip() in choose}
    return make_relation_dict


def handle_file(image_dir,annotation_dir,output_path,class_name,verbose=False):
    image_output = os.path.join(output_path,'images/')
    annotation_output = os.path.join(output_path,'annotations')
    image_dest = os.path.join(image_output,image_dir.split('/')[-1])
    annotations_dest = os.path.join(annotation_output,annotation_dir.split('/')[-1].replace('txt','xml'))
    sh.copyfile(image_dir,image_dest)

    #start creating tree
    root = ET.Element('annotation')
    ET.SubElement(root,'folder').text = 'carcomp'
    ET.SubElement(root,'filename').text = image_dir.split('/')[-1]

    #source : aborted

    #owner : aborted

    #size : width + height + depth
    shape = cv2.imread(image_dir).shape
    size = ET.SubElement(root,'size')
    ET.SubElement(size,'height').text = str(shape[0])
    ET.SubElement(size,'width').text = str(shape[1])
    ET.SubElement(size,'depth').text = str(shape[2])


    #segmented
    ET.SubElement(root,'segmented').text = 0


    annotates = open(annotation_dir).read().splitlines()[2].split(' ') # only the third line contain bndbox
    #object:name + bndbox
    object= ET.SubElement(root,'object')

    bndbox = ET.SubElement(object,'bndbox')
    ET.SubElement(bndbox,'xmin').text = str(annotates[0])
    ET.SubElement(bndbox,'ymin').text = str(annotates[1])
    ET.SubElement(bndbox,'xmax').text = str(annotates[2])
    ET.SubElement(bndbox,'ymax').text = str(annotates[3])

    ET.SubElement(object,'name').text = class_name

    # #write file
    tree = ET.ElementTree(root)



    tree.write(annotations_dest)
    if verbose:
        print('Copied: {} and {}'.format(image_output,annotations_dest))



def convert(choose,output_path,delete=False,verbose=False ):
    print('Start convert')
    count=0
    if delete:
        try:
            sh.rmtree(output_path)
            print('removed',output_path)
            os.mkdir(output_path)
        except:
            pass
    os.mkdir(os.path.join(output_path,'images'))
    os.mkdir(os.path.join(output_path,'annotations'))


    make_map = get_idx_for_make(choose)

    base_path = os.path.join(data_path,'image')

    for make in make_map.keys():
        model_path=os.path.join(base_path,str(make))
        models_list = os.listdir(model_path)
        models_list = [model for model in models_list if re.search(r'\d+',model)]
        for model in models_list:
            copy_list = {}
            years_path = os.path.join(model_path,model)
            years_list = os.listdir(years_path)
            years_list = [year for year in years_list if re.search(r'\d+',year)]
            # loop through items in year folder
            for year in years_list:
                image_path = os.path.join(years_path,year)
                images_list = os.listdir(image_path)
                images_list = [image for image in images_list if re.search(r'.png|.jpg',image)]
                #loop through image from images list
                for image in images_list:
                    image_dir = os.path.join(image_path,image)
                    annotation_dir = image_dir.replace('image','label')
                    annotation_dir = annotation_dir.replace('jpg','txt')
                    handle_file(image_dir,annotation_dir,output_path,class_name=make_map[make],verbose=verbose)
                    count+=1

    print('Data path:',os.path.abspath(data_path))
    print('Destination path : ',os.path.abspath(output_path))
    print('Copied {} files'.format(count))

def main():
    parser = argparse.ArgumentParser(epilog='Usage : python convert.py -d /Users/qnkhuat/Documents/carcomp/data -dd data -c')
    parser.add_argument('-d','--datapath',dest ='datapath',help='path to data folder',default='/Users/qnkhuat/Documents/carcomp/data')
    parser.add_argument('-dd',dest ='datadest',help='path to copy destination',default='./data')
    parser.add_argument('-v','--verbose',dest ='verbose',help='Turn on verbose mode',action='store_true')
    args = parser.parse_args()


    global data_path
    data_path = args.datapath
    data_dest = args.datadest
    # assert 'image' in data_dest , "destination can't not be image "
    verbose = args.verbose

    start = time.time()

    choose = open('labels.txt').read().splitlines()

    convert(choose,data_dest,delete=True,verbose=verbose)
    print('Ran in :',time.time() -start)

if __name__ == '__main__':
    main()
