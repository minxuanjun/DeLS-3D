# preprocess the training images
import os
import cv2
import sys

import json

import numpy as np
import utils.dels_utils as uts



def cp_sim_seq(0):
    params = set_params()
    res_path = params['sim_path'] + '%02d/' % i
    image_list = [x.stripe() for x in open(params['test_set'])]


def set_params(val_id=-1):
    params = {'stage': 2}
    root_path = './'
    params['data_path'] = root_path + 'data/zpark/'
    # params['image_path'] = params['data_path'] + 'images/'
    params['depth_path'] = params['data_path'] + 'depth/'
    params['pose_path'] = params['data_path'] + 'camera_pose/'
    params['label_path'] = params['data_path'] + 'semantic_label/'
    # params['cloud'] = params['data_path'] + "semantic_3D_point/BkgCloud.pcd";
    params['cloud'] = "/home/peng/Data/zpark/cluster1686.pcd";

    HOME = '/home/peng/Data/'
    params['data_path'] = HOME + 'zpark/'
    params['image_path'] = params['data_path'] + 'Images/'
    # params['depth_path'] = params['data_path'] + 'Depth/'
    # params['pose_path'] = params['data_path'] + 'Results/Loc/'
    # params['label_path'] = params['data_path'] + 'LabelFull/'
    params['train_set'] = params['data_path'] + 'split/train.txt'
    params['test_set'] = params['data_path'] + 'split/val.txt'
    # full with manually labelled object
    params['label_color_path'] = params['data_path'] + 'LabelFullColor/'


    # full with manually labelled object
    params['label_color_path'] = params['data_path'] + 'LabelFullColor/'
    # path directly rendered
    params['label_bkg_path'] = params['data_path'] + 'LabelBkg/'
    # bkg with manually impainted building
    params['label_bkgfull_path'] = params['data_path'] + 'LabelBkgFull/'
    # bkg with single object foreground only
    params['label_bkgobj_path'] = params['data_path'] + 'LabelBkgObj/'

    shader_path = "/home/peng/test/baidu/personal-code/projector/src/"
    params['vertex'] = shader_path + "PointLabel.vertexshader"
    params['geometry'] = shader_path + "PointLabel.geometryshader"
    params['frag'] = shader_path + "PointLabel.fragmentshader"
    params['is_color_render'] = True

    # results/pose/pose_cnn or pose_rnn,  results/segments
    params['output_path'] = root_path + 'results/zpark/'

    # sample simulated seqences for testing
    params['noisy_pose_path'] = params['output_path'] + 'noisy_pose/'

    params['camera'] = ['Camera_1', 'Camera_2']
    scenes = os.listdir(params['image_path'])
    params['scene_names'] = []
    for scene in scenes:
        for camera in params['camera']:
            params['scene_names'].append(scene + '/' + camera)

    params['test_scene'] = []
    if val_id == -1:
        for scene in scenes[-1:]:
            for camera in params['camera']:
                params['test_scene'].append(scene + '/' + camera)

    # each scene forms a sequence of data points
    params['train_scene'] = uts.parse_scenes(params['train_set'])
    params['test_scene'] = uts.parse_scenes(params['test_set'])

    params['intrinsic'] = {
            'Camera_1': np.array([1450.317230113, 1451.184836113,
                                  1244.386581025, 1013.145997723]),
            'Camera_2': np.array([1450.317230113, 1451.184836113,
                                  1244.386581025, 1013.145997723])
            }
    params['cam_names'] = params['intrinsic'].keys()
    params['raw_size'] = [2056, 2452]
    for cam in params['intrinsic'].keys():
        params['intrinsic'][cam][[0, 2]] /= params['raw_size'][1]
        params['intrinsic'][cam][[1, 3]] /= params['raw_size'][0]

    # for network configuration height width
    params['size'] = [256, 304]
    params['size'] = [512, 608]
    params['out_size'] = [128, 152]
    params['size_stage'] = [[8, 9], [64, 76]]
    params['batch_size'] = 4

    params['read_depth'] = uts.read_depth

    color_params = uts.gen_color_list(params['data_path'] + 'color_v2.lst')
    params['class_num'] = color_params['color_num'] # with extra background 0
    params.update(color_params)

    params['id_2_trainid'] = np.arange(256)
    params['class_names'] = ['background',
            'sky',
            'car',
            'bike',
            'pedestrian',
            'cyclist',
            'unknown-surface',
            'car-lane',
            'pedestrian-lane',
            'bike-lane',
            'unknown',
            'unknown-road-edge',
            'curb',
           'unknown-lane-barrier',
           'traffic-cone',
           'traffic-stack',
           'fence',
           'unknown-road-side-obj',
           'light-pole',
           'traffic-light',
           'telegraph-pole',
           'traffic-sign',
           'billboard',
           'bus-stop-sign',
           'temp-building',
           'building',
           'newstand',
           'policestand',
           'unknown',
           'unknown',
           'unknown-plants',
           'plants',
           'vehicle',
           'motor-vehicle',
           'bike',
           'pedestrian',
           'cyclist']

    # these weights are use for sample points for training projective loss
    params['label_weight'] = [0, 0.1, 0, 0, 0, 0,
            1, 1, 3, 3, 0, 5, 10, 10, 10, 10, 10, 0,
            100, 100, 100, 100, 100, 10, 2, 5, 5, 5, 0, 0,
            0, 1, 0, 0, 0, 0, 0]

    params['is_rare'] = [False for i in range(params['class_num'])]
    for i in [23,26]:
        params['is_rare'][i] = True

    params['is_exist'] = [True for i in range(params['class_num'])]
    for i in [0, 2,3,4,5,10,26,28,29]:
        params['is_exist'][i] = False

    params['is_obj'] = [False for i in range(params['class_num'])]
    params['obj_ids'] = [2,3,4,5,32,33,34,35,36]
    for i in params['obj_ids']:
        params['is_obj'][i] = True

    params['is_unknown'] = [False for i in range(params['class_num'])]
    for i in range(params['class_num']):
        if 'unknown' in params['class_names'][i]:
            params['is_unknown'][i] = True

    return params




def eval_reader(scene_names, height, width, params):
    def get_image_list(scene_name):
        image_path = params['image_path'] + scene_name + '/'
        trans_list = uts.list_images(image_path, exts=set(['txt']))
        ext = [line for line in open(trans_list[0])]
        ext = ext[1:]
        image_name_list = []
        for line in ext:
            image_name_list.append(line.split('\t')[1][:-4])
        return image_name_list

    def reader():
        # loading path
        for scene_name in scene_names:
            res_path = params['res_path'] + scene_name + '/'
            gt_path = params['label_path'] + scene_name + '/'
            image_list = get_image_list(scene_name)
            image_num = len(image_list)
            for i, name in enumerate(image_list):
                if i % 10 == 1:
                    print "{} / {}".format(i, image_num)
                label_res = cv2.imread(res_path + name + '.png')[:, :, 0]
                label_gt = cv2.imread(gt_path + name + '.png')[:, :, 0]
                label_res = cv2.resize(label_res, (width, height),
                            interpolation=cv2.INTER_NEAREST)
                label_gt = cv2.resize(label_gt, (width, height),
                            interpolation=cv2.INTER_NEAREST)
                weight = np.ones((height,width), dtype=np.float32)
                weight = weight * np.float32(label_gt != 255)
                weight = weight * np.float32(label_gt != 0)
                weight = weight * np.float32(label_res != 0)

                # uts.plot_images({'label':label_gt, 'weight':weight})
                label_res = np.float32(label_res.flatten())
                label_gt = np.float32(label_gt.flatten())
                weight = np.float32(weight.flatten())
                yield label_res, label_gt, weight

    return reader



def test_eval(scene_names, height, width, params):
    return eval_reader(scene_names, height, width, params)




if __name__ == "__main__":
    test_eval()
