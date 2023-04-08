import os
from idx_helper import IDXParse


def get_dir_mark(dir_path, stop_mark):
    marks = []
    dir_path, cur_mark = os.path.split(dir_path)

    while cur_mark != stop_mark:
        marks.append(cur_mark)
        dir_path, cur_mark = os.path.split(dir_path)
    marks.reverse()
    return marks


def get_sample_with_mark(traffic_sample_path):
    if not os.path.isdir(traffic_sample_path):
        print(f"{traffic_sample_path} is not a dir path!")
        exit()
    
    _, cur_dir = os.path.split(traffic_sample_path)
    sample_list = []
    for root, _, files in os.walk(traffic_sample_path):
        for file in files:
            sample_marks = get_dir_mark(root, cur_dir)
            sample_marks.append(os.path.join(root, file))
            sample_list.append(tuple(sample_marks))
    return sample_list


def print_data_info(data_map, verbose=False, train_or_test_mark=None):
    cnt = sum([len(d_list) for d_list in data_map.values()])
    if not train_or_test_mark:
        print(f"All data: {cnt}")
    else:
        print(f"The data used for {train_or_test_mark}: {cnt}")
    if verbose:
        data_cls_info = {cls: len(d_list) for cls, d_list in data_map.items()}
        for cls, val in data_cls_info.items():
            print(f"    {cls}: {val}")
