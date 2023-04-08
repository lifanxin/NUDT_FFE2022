from struct import *
import os
import numpy as np


class IDXParse():

    def __init__(self, file_dir, train_or_test_mark="train"):
        # read file
        if not os.path.isdir(file_dir):
            print(f"{file_dir} is not a right dir!")
            exit()
        item_idx_path = os.path.join(file_dir, f"{train_or_test_mark}-images-idx3-ubyte")
        label_idx_path = os.path.join(file_dir, f"{train_or_test_mark}-labels-idx1-ubyte")
        with open(item_idx_path, "rb") as f:
            self.item_f = f.read()
        with open(label_idx_path, "rb") as f:
            self.label_f = f.read()

        # parse headers
        item_dimen_cnt, self.item_nums = unpack_from(">BI", self.item_f, 3)
        self.item_dimen = []
        for i in range(item_dimen_cnt-1):
            self.item_dimen.append(unpack_from(">I", self.item_f, 8)[0])
        label_dimen_cnt, self.label_nums = unpack_from(">BI", self.label_f, 3)

        if label_dimen_cnt != 1:
            print("label file header is not right!")
            exit()
        if self.item_nums != self.label_nums:
            print("Error, idx3 file and idx1 file item nums is not equal!")
            exit()
    
    def get_size(self):
        return self.item_nums

    def get_items(self):
        seq_size = 1
        for size in self.item_dimen:
            seq_size *= size
        item_parse_format = str(seq_size) + "B"
        label_parse_format = "1B"
        items = iter_unpack(item_parse_format, self.item_f[8+len(self.item_dimen)*4:])
        labels = iter_unpack(label_parse_format, self.label_f[8:])

        item_with_label_list = []
        for item, label in zip(items, labels):
            item = np.array(item, dtype=np.int32).reshape(self.item_dimen)
            label = np.array(label, dtype=np.int64)[0]
            item_with_label_list.append((item, label))
        return item_with_label_list


class IDXAssemble():

    def __init__(self, save_dir, dimen, train_or_test_mark="train"):
        # set storage path
        self.item_f, self.label_f = None, None
        if not os.path.isdir(save_dir):
            print(f"{save_dir} is not a right dir!")
            exit()
        item_idx_path = os.path.join(
            save_dir, f"{train_or_test_mark}-images-idx3-ubyte"
        )
        label_idx_path = os.path.join(
            save_dir, f"{train_or_test_mark}-labels-idx1-ubyte"
        )

        # set file header
        self.item_size = 0
        self.expected_seq_size = 1
        item_magic = unpack(">I", b"\x00\x00\x08"+ (len(dimen)+1).to_bytes(1, "big"))[0]
        label_magic = unpack(">I", b"\x00\x00\x08\x01")[0]

        item_header = pack(">II", item_magic, self.item_size)
        for size in dimen:
            self.expected_seq_size *= size
            item_header += pack(">I", size)
        label_header = pack(">II", label_magic, self.item_size)

        # write file header
        self.item_f = open(item_idx_path, "wb")
        self.label_f = open(label_idx_path, "wb")
        self.item_f.write(item_header)
        self.label_f.write(label_header)
    
    def write_item(self, item, label):
        if self.expected_seq_size != len(item):
            print(f"{item} size is not match dimen!")
            exit()
        self.item_f.write(item)
        self.label_f.write(label)
        self.item_size += 1

    def __close_file(self, file_obj):
        if file_obj:
            file_obj.seek(4)
            file_obj.write(self.item_size.to_bytes(4, "big"))
            file_obj.close()

    def __del__(self):
        self.__close_file(self.item_f)
        self.__close_file(self.label_f)


if __name__ == "__main__":
    # test
    import numpy as np
    from PIL import Image

    idx_path = r"C:\Users\fanxinli\Desktop\Traffic\DLForVPN\PytorchStu\data\MNIST\raw"
    save_path = os.path.join(
        idx_path, "test.png"
    )
    parser = IDXParse(idx_path)
    # print(parser.item_nums)
    # exit()
    for item in parser.get_items():
            # d_arr = np.array(item).reshape(parser.item_dimen)
            # print(d_arr)
            print(item[1])
            print(item[0])
            data = item[0] *255
            print(data)
            # img = Image.fromarray(data)
            # img.show()
            # img.save(save_path)
            exit()

