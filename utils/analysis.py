import pandas as pd
import scipy.io as io
import os

data_path = './data'

def misc():
    # TODO: plot the number of images for each make
    attribute = pd.read_csv(os.path.join(data_path,'misc/attributes.txt'),delimiter=' ')
    print('Describe:')
    # print(data.describe())

    data_labels = io.loadmat(os.path.join(data_path,'misc/make_model_name'))
    model_name = data_labels['model_names']
    make_model = data_labels['make_names']



def makes():
    makes_list = os.listdir(os.path.join(data_path,'image/'))
        

def main():
    # misc()
    makes()


if __name__ == '__main__':
    main()
