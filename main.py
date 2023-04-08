import argparse
import os, sys
from feas_worker import FeasWorker


CUR_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
NFP_PATH = os.path.join(CUR_DIR_PATH, "NFPlugins")
sys.path.append(NFP_PATH)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert the traffic(.pcap/.pcapng file) to images and IDX files.")
    parser.add_argument("sample_dir", help="your traffic sample's dir")
    parser.add_argument("-nfplugin", help="point the traffic extract plugin")
    parser.add_argument("-clear", help="clear traffic data", action="store_true")
    parser.add_argument("-m_level", type=int, default=1, help="point traffic mark level")
    parser.add_argument("-t", type=float, default=0.9, help="training data ratio of the data")
    parser.add_argument("-no_idx", help="generate idx file, default is open", action="store_false")
    parser.add_argument("-idx_path", help="the idx files save path, default is current dir")
    parser.add_argument("-to_img", help="generate img file, default is off", action="store_true")
    parser.add_argument("-img_path", help="the images save path, default is current dir")
    parser.add_argument("-v", "--verbose", help="print verbose info", action="store_true")
    args = parser.parse_args()

    sample_dir = args.sample_dir
    if args.nfplugin:
        nfplugin = getattr(__import__(args.nfplugin), "FFE")
    else:
        nfplugin = getattr(__import__("session784bytes"), "FFE")
    clear = args.clear
    m_level = args.m_level
    train_data_ratio = args.t
    if train_data_ratio > 1.0 or train_data_ratio < 0:
        print(f"{train_data_ratio} is illegal!")
        exit()
    to_idx = args.no_idx
    to_img = args.to_img
    if args.idx_path:
        if not os.path.isdir(args.idx_path):
            print("f{args.idx_path} is not right dir!")
            exit()
        idx_path = args.idx_path
    else:
        idx_path = os.path.join(CUR_DIR_PATH, "IDX")
    if args.img_path:
        if not os.path.isdir(args.img_path):
            print("f{args.img_path} is not right dir!")
            exit()
        img_path = args.img_path
    else:
        img_path = os.path.join(CUR_DIR_PATH, "IMG")
    verbose = args.verbose
    print(sample_dir, nfplugin, clear, m_level, train_data_ratio, to_idx, to_img)
    print(idx_path, img_path, verbose)
    FeasWorker(
        sample_path=sample_dir, mark_level=m_level, FFE_obj=nfplugin,
        train_data_ratio=train_data_ratio, is_clear=clear, 
        to_idx=to_idx, to_img=to_img,
        idx_save_dir=idx_path, img_save_dir=img_path,
        verbose=verbose
    ).work()
