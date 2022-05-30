import os
import io
from abc import ABC
from typing import List, Optional, Sequence, Union, Any

from PIL import Image
from pytorch_lightning import LightningDataModule
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import VisionDataset
from torchvision.datasets.celeba import CSV, CelebA
import zipfile
import cv2
import numpy as np
import torch
import csv


# Reference: https://github.com/pytorch/vision/blob/main/torchvision/datasets/celeba.py
# https://discuss.pytorch.org/t/dataloader-with-zipfile-failed/42795
class CelebAZipDataset(VisionDataset):
    def __init__(self, root_path, attribute, transform=None, cache_into_memory=True, ):
        super().__init__(root_path, transform=transform)

        self.root_path = root_path
        zip_file_path = os.path.join(root_path, 'img_align_celeba.zip')
        if cache_into_memory:
            f = open(zip_file_path, 'rb')
            self.zip_content = f.read()
            f.close()
            self.zip_file = zipfile.ZipFile(io.BytesIO(self.zip_content), 'r')
        else:
            self.zip_file = zipfile.ZipFile(zip_file_path, 'r')

        self.name_list = list(filter(lambda x: x[-4:] == '.jpg', self.zip_file.namelist()))
        print(self.name_list[:10])
        self.datadict = self._load_csv(os.path.join(self.root_path, "list_attr_celeba.txt"), attribute, header=1)

        print(self.datadict[:10])
        print(len(self.datadict))


    def _load_csv(
            self,
            filename: str,
            attribute: tuple = None,
            header: Optional[int] = None,
    ) -> list:
        with open(filename) as csv_file:
            data = list(csv.reader(csv_file, delimiter=" ", skipinitialspace=True))

        if header is not None:
            headers = data[header][:-1]
            data = data[header + 1:]
        else:
            headers = []
        i = headers.index(attribute[0])

        indices = [row[0] for row in data]
        data = [row[1:][i] for row in data]
        data_int = [int(i) for i in data]

        d = [(x, y) for x, y in zip(indices, data_int) if y == attribute[1]]

        return d

    def __getitem__(self, key):
        buf = self.zip_file.read(name=self.datadict[key][0])
        arr = cv2.imdecode(np.frombuffer(buf, dtype=np.uint8), cv2.IMREAD_COLOR)

        pil_img = Image.fromarray(arr[:, :, ::-1])  # because the current mode is BGR
        # pil_img.save('savedimage.jpg')
        target = self.datadict[key][1]

        if self.transform is not None:
            pil_img = self.transform(pil_img)
        # if self.target_transform is not None:
        #     target = self.target_transform(target)

        return pil_img, target, key

    def __len__(self):
        return len(self.datadict)


train_transforms = transforms.Compose([transforms.RandomHorizontalFlip(),
                                       transforms.CenterCrop(148),
                                       transforms.Resize(64),
                                       transforms.ToTensor(), ])
ds = CelebAZipDataset('../../data/celeba', ('Male', -1),
                           transform=train_transforms)

dl = DataLoader(
    ds,
    batch_size=64,
    num_workers=0,
    shuffle=False,
    pin_memory=False,
)

x, y, k = next(iter(dl))
