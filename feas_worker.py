import os
import random

from tqdm import *
import numpy as np
from nfstream import NFStreamer

from utils import get_sample_with_mark, print_data_info
from data_cleaner import DataCleaner
from idx_helper import IDXAssemble
from img_helper import IMGHelper


class  FeasWorker():

    def __init__(self, 
            sample_path, mark_level, FFE_obj,
            train_data_ratio=0.9, is_clear=False, 
            to_idx=True, idx_save_dir=None, to_img=False, img_save_dir=None,
            verbose=False):
        self.sample_path = sample_path
        self.mark_level = mark_level
        self.FFE_obj = FFE_obj
        self.train_data_ratio = train_data_ratio
        self.is_clear = is_clear
        self.to_idx = to_idx
        self.idx_save_dir = idx_save_dir if idx_save_dir else os.path.join(os.getcwd(), "IDX")
        self.to_img = to_img
        self.img_save_dir = img_save_dir if img_save_dir else os.path.join(os.getcwd(), "IMG")
        self.verbose = verbose

    def __gen_feas(self, sample_list):
        data_map = {}
        for sample_item in tqdm(sample_list):
            if len(sample_item) == self.mark_level:
                print(f"{sample_item} don't have right mark level!")
                exit()
            
            sample_mark = sample_item[self.mark_level-1]
            pcap_file = sample_item[-1]
            if sample_mark not in data_map.keys():
                data_map[sample_mark] = []

            my_streamer = NFStreamer(
                source=pcap_file,
                decode_tunnels=False,
                bpf_filter=None,
                promiscuous_mode=True,
                snapshot_length=1536,
                idle_timeout=120,
                active_timeout=1800,
                accounting_mode=3,
                udps=self.FFE_obj(),
                n_dissections=20,
                statistical_analysis=False,
                splt_analysis=0,
                n_meters=0,
                performance_report=0
            )
            for flow in my_streamer:
                item_map = {k: v for k, v in zip(flow.keys(), flow.values())}
                data_map[sample_mark].append(item_map)
        return data_map

    def __mark_train_test_data(self, all_data_map):
        train_data_map = {cls: [] for cls in all_data_map.keys()}
        test_data_map = {cls: [] for cls in all_data_map.keys()}
        
        for cls, d_list in all_data_map.items():
            random.shuffle(d_list)
            for idx, data in enumerate(d_list):
                if idx < int(self.train_data_ratio * len(d_list)):
                    train_data_map[cls].append(data)
                else:
                    test_data_map[cls].append(data)
        return train_data_map, test_data_map

    def __convert_to_idx(self, data_map, dimen, train_or_test_mark):
        if not os.path.exists(self.idx_save_dir):
            os.makedirs(self.idx_save_dir)

        idx_assembler = IDXAssemble(self.idx_save_dir, dimen, train_or_test_mark)
        cls_map_to_digit = {cls: idx for idx, cls in enumerate(data_map.keys())}
        for cls, d_list in tqdm(data_map.items()):
            for data in d_list:
                item = data["udps.bytes_fea"]
                label = cls_map_to_digit[cls].to_bytes(1, "big")
                idx_assembler.write_item(item, label)

    def __convert_to_img(self, data_map, dimen, save_dir):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for cls, d_list in tqdm(data_map.items()):
            img_cls_dir = os.path.join(save_dir, cls)
            if not os.path.exists(img_cls_dir):
                os.makedirs(img_cls_dir)

            for idx, data in enumerate(d_list):
                img_data = np.array([bt for bt in data["udps.bytes_fea"]]).reshape(dimen)
                img_path = os.path.join(img_cls_dir, f"{cls}_{idx}.png")
                IMGHelper.save_img(img_data, img_path)
    
    def work(self):
        sample_list = get_sample_with_mark(self.sample_path)

        print(f"{'=' * 20} \nGenerate Features...")
        data_map = self.__gen_feas(sample_list)
        if self.verbose:
            print_data_info(data_map, False)
        if self.is_clear:
            print(f"{'=' * 20} \nData cleaning...")
            data_map = DataCleaner().clear_data(data_map)
            if self.verbose:
                print_data_info(data_map, False)

        train_data_map, test_data_map = self.__mark_train_test_data(data_map)
        if self.verbose:
            print_data_info(train_data_map, True, "train")
            print_data_info(test_data_map, True, "test")
        if self.to_idx:
            print(f"{'=' * 20} \nGenerate Trainging IDX...")
            self.__convert_to_idx(train_data_map, self.FFE_obj.get_storage_dimen(), "train")
            print(f"{'=' * 20} \nGenerate Testing IDX...")
            self.__convert_to_idx(test_data_map, self.FFE_obj.get_storage_dimen(), "test")
        if self.to_img:
            print(f"{'=' * 20} \nGenerate Trainging IMG...")
            train_img_dir = os.path.join(self.img_save_dir, "train")
            self.__convert_to_img(train_data_map, self.FFE_obj.get_storage_dimen(), train_img_dir)
            print(f"{'=' * 20} \nGenerate Testing IMG...")
            test_img_dir = os.path.join(self.img_save_dir, "test")
            self.__convert_to_img(test_data_map, self.FFE_obj.get_storage_dimen(), test_img_dir)
