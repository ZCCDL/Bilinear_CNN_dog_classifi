#!/usr/bin/evn python
# -*- coding: utf-8 -*-

import sys

sys.path.append("/mnt/git/Bilinear_CNN_dog_classifi/")
import pickle
import random
import cv2
import os
import numpy as np
from bdgod.dog_config import *
from bdgod.data_augmentation import data_augmentation_img_tag


class data_loader_(object):
    def __init__(self, batch_size, band_num=0, tag_id=0, shuffle=True, data_add=4, onehot=True,
                 data_size=224,
                 nb_classes=100):
        self.batch_szie = batch_size
        self.shuffle = shuffle
        self.tag_id = tag_id
        self.key_file_name = 'pkls/all_pic_infs_%d_%d.pkl' % (band_num, tag_id)
        self.train_data,self.test_data= self.load_keys()
        # print self.all_pic_inf,
        self.train_length = len(self.train_data)
        self.test_length = len(self.test_data)
        self.train_index = 0
        self.test_index = 0
        self.data_add = data_add
        self.data_size = data_size
        self.nb_classes = nb_classes
        self.onehot = onehot

    def load_keys(self):
        file_d = open(self.key_file_name, 'rb')
        pic_data = pickle.load(file_d)
        file_d.close()
        print len(pic_data)
        # print pic_data
        random.shuffle(pic_data)

        file_d = open('all_pic_infs1.pkl', 'rb')
        pic_test_data = pickle.load(file_d)
        file_d.close()

        dog_key = os.listdir(Image_Path)
        self.key_map = {dog_key[x]: x for x in range(100)}

        return pic_data,pic_test_data

    def add_train_index(self):
        self.train_index += 1
        if self.train_index == self.train_length:
            random.shuffle(self.train_data)
            self.train_index = 0

    def add_test_index(self):
        self.test_index += 1
        if self.test_index == self.test_length:
            random.shuffle(self.test_data)
            self.test_index = 0

    def data_pop(self, train=True):
        if train:
            data_temp = self.train_data[self.train_index]
            self.add_train_index()
            return data_temp
        else:
            data_temp = self.test_data[self.test_index]
            self.add_test_index()
            return data_temp

    def get_train_data(self):
        result = np.ones((0, self.data_size, self.data_size, 3))
        pop_num = self.batch_szie / self.data_add
        all_labels = []
        for i in range(pop_num):
            data_temp = self.data_pop(train=True)
            image_path = data_temp[0]
            label = image_path.split('/')[-2]
            label = self.key_map[label]
            labels = [int(label) for x in range(self.data_add)]
            all_labels += labels
            image_points = data_temp[1]
            point_index = random.randint(1, len(image_points)) - 1
            point_value = image_points[point_index]
            img_temp = cv2.imread(image_path)
            img_temp_arr = np.array(img_temp)
            rad_width = (point_value[2] - point_value[0]) / 10
            rad_hight = (point_value[3] - point_value[1]) / 10
            point_value[0] = point_value[0] + random.randint(0, rad_width) - (rad_width / 2)
            if point_value[0] < 0:
                point_value[0] = 0
            point_value[2] = point_value[2] + random.randint(0, rad_width) - (rad_width / 2)
            point_value[1] = point_value[1] + random.randint(0, rad_hight) - (rad_hight / 2)
            if point_value[1] < 0:
                point_value[1] = 0
            point_value[3] = point_value[3] + random.randint(0, rad_hight) - (rad_hight / 2)
            corp_img = img_temp_arr[point_value[1]:point_value[3], point_value[0]:point_value[2]]
            all_imgs = data_augmentation_img_tag(corp_img, data_size=self.data_size,tag=self.tag_id)
            all_imgs = all_imgs[:self.data_add]
            assert len(all_imgs) == self.data_add
            result = np.concatenate((result, all_imgs), axis=0)
        if self.onehot:
            targets = np.array(all_labels).reshape(-1)
            all_labels = np.eye(self.nb_classes)[targets]
        else:
            all_labels = np.array(all_labels)

        assert result.shape[0] == all_labels.shape[0]
        return result, all_labels

    def get_test_data(self):
        result = np.ones((0, self.data_size, self.data_size, 3))
        all_labels = []
        for i in range(self.batch_szie):
            data_temp = self.data_pop(train=False)
            image_path = data_temp[0]
            label = image_path.split('/')[-2]
            label = self.key_map[label]
            labels = [int(label)]
            all_labels += labels

            image_points = data_temp[1]
            point_index = random.randint(1, len(image_points)) - 1
            point_value = image_points[point_index]
            if point_value[0] < 0:
                point_value[0] = 0
            if point_value[1] < 0:
                point_value[1] = 0
            img_temp = cv2.imread(image_path)
            img_temp_arr = np.array(img_temp)
            corp_img = img_temp_arr[point_value[1]:point_value[3], point_value[0]:point_value[2]]
            corp_img = cv2.resize(corp_img, (self.data_size, self.data_size))
            corp_img = corp_img[np.newaxis, ...]
            result = np.concatenate((result, corp_img), axis=0)
        if self.onehot:
            targets = np.array(all_labels).reshape(-1)
            all_labels = np.eye(self.nb_classes)[targets]
        else:
            all_labels = np.array(all_labels)

        assert result.shape[0] == all_labels.shape[0]
        return result, all_labels
