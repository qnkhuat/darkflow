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



def misc():
    # TODO: plot the number of images for each make
    attribute = pd.read_csv(os.path.join(data_path,'misc/attributes.txt'),delimiter=' ')
    data_labels = io.loadmat(os.path.join(data_path,'misc/make_model_name'))
    model_names = data_labels['model_names']
    make_names = data_labels['make_names']
    return model_names,make_names

def make_dict(choose):
    '''
    return a dict contain number of images from each make
    '''

    make_path = os.path.join(data_path,'image/')
    make_list = os.listdir(make_path)
    # filter all the dir isn't number
    make_list = [make for make in make_list if re.search(r'\d+',make)]

    # list of contains number of examples for each make
    models_name , makes_name = misc()
    make_analysis = {make.item()[0] :0 for make in makes_name}
    # loop through items in makes folder
    for make in make_list:
        models_path = os.path.join(make_path,make)
        models_list = os.listdir(models_path)
        models_list = [model for model in models_list if re.search(r'\d+',model)]
        # loop through items in model folder
        for model in models_list:
            years_path = os.path.join(models_path,model)
            years_list = os.listdir(years_path)
            years_list = [year for year in years_list if re.search(r'\d+',year)]
            # loop through items in year folder
            for year in years_list:
                images_list = os.listdir(os.path.join(years_path,year))
                images_list = [image for image in images_list if re.search(r'.png|.jpg',image)]
                make_analysis[makes_name[int(make)-1].item()[0]]+= len(images_list)

    if choose :
        make_analysis = { key:value for key,value in make_analysis.items() if key.lower().strip() in choose}
    return make_analysis


def get_idx_for_make(choose):
    '''
    choose : list of car makes to get
    '''
    model_name,make_model = misc()


    #make id that I chose to class
    make_relation_dict = { idx +1:make[0][0].lower().strip() for idx,make in enumerate(make_model) if make[0][0].lower().strip() in choose}
    return make_relation_dict


def visual_images(choose=False):
    '''
    visualize number of images for each make
    '''

    make_dict_data = make_dict(choose)
    make_dict_data = list(make_dict_data.items())

    make_analysis = pd.DataFrame(make_dict_data,columns=['Makes','Images'])
    make_analysis= make_analysis.sort_values(by=['Images'])

    # Filter
    makes = make_analysis.Makes
    images = make_analysis.Images
    pos = np.arange(len(makes))

    plt.figure(figsize=(10, make_analysis.shape[0]*0.3))

    plt.barh(pos,images,height=.7)

    # annotate to the end of the bar
    for p, c, ch in zip(pos, makes, images):
        plt.annotate(str(ch), xy=(ch + 7, p + .1), va='center')

    plt.yticks(pos, makes)
    plt.grid(axis = 'x', color ='white', linestyle='-')

    plt.ylim(pos.max() + 1, pos.min() - 1)
    plt.xlim(0, 6000)

    plt.show()




def copy_images(choose,output_path,delete=False,verbose=False ):


    count=0
    if delete:
        try:
            sh.rmtree(os.path.join(data_path,output_path))
        except:
            pass


    make_map = get_idx_for_make(choose)

    # list of number of examples for each make
    models_name , makes_name = misc()
    make_analysis = {make.item()[0] :0 for make in makes_name}

    make_path = os.path.join(data_path,'image')
    print(make_path)
    makes_list = [os.path.join(make_path, str(make)) for make in make_map.keys()]

    # loop through models in make folder
    for make in makes_list:
        model_path=make
        models_list = os.listdir(make)
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
                    copy_list[image_dir] = image_dir



            copy_dir_shuffled = list(copy_list.keys())
            random.shuffle(copy_dir_shuffled)
            for idx,copy_dir in enumerate(copy_dir_shuffled):
                make_id = re.search(r'\d+',make).group()
                dest_dir = copy_list[copy_dir]
                dest_dir = dest_dir.replace(make_id,make_map[int(make_id)],1)
                # 8:2 train:test
                if idx >0.8*len(copy_dir_shuffled):
                    dest_dir = dest_dir.replace('image',os.path.join(output_path,'test'))
                    dest_base_dir = dest_dir.replace(re.search('\w+(.jpg|.png)',dest_dir).group(),'')
                    if not os.path.exists(dest_base_dir):
                        os.makedirs(dest_base_dir)

                else:
                    dest_dir = dest_dir.replace('image',os.path.join(output_path,'train'))
                    dest_base_dir = dest_dir.replace(re.search('\w+(.jpg|.png)',dest_dir).group(),'')
                    if not os.path.exists(dest_base_dir):
                        os.makedirs(dest_base_dir)
                # sh.copyfile(copy_dir,dest_dir)
                count+=1
                if verbose:
                    print('Copied: {} => {}'.format(copy_dir,dest_dir))

    print('Data path:',os.path.abspath(data_path))
    print('Destination path : ',os.path.abspath(output_path))
    print('Copied {} files'.format(count))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--datapath',dest ='datapath',help='path to carcomp folder',default='./data')
    parser.add_argument('-dd',dest ='datadest',help='path to copy destination',default='./data')
    parser.add_argument('-v','--verbose',dest ='verbose',help='Turn on verbose mode',action='store_true')
    parser.add_argument('-vs','--visual',dest ='visual',help='Visualize',action='store_true')
    parser.add_argument('-c','--copy',dest ='copy',help='Copy images to dir',action='store_true')
    args = parser.parse_args()


    global data_path
    data_path = args.datapath
    data_dest = args.datadest
    verbose = args.verbose
    is_copy = args.copy
    is_visual = args.visual

    choose = open('labels.txt').read().splitlines()

    if is_copy:

        copy_images(choose,data_dest,delete=True,verbose=verbose)
    if is_visual:
        print('Visualize')
        visual_images(choose)

if __name__ == '__main__':
    main()
