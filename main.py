import cv2
import sys
import time
from pathlib import Path
import yolov5
import os
import glob
import tkinter as tk
import tkinter.filedialog as fd


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.APP_DIRECTORY = '-'
        self.model = yolov5.load('best.pt').cpu()
        btn_check = tk.Button(self, text="check dir",
                              command=self.check_dir)
        btn_dir = tk.Button(self, text="Выбрать папку",
                            command=self.choose_directory)
        btn_sort = tk.Button(self, text="Sort animals",
                             command=self.sort_photos)
        btn_check.pack(padx=60, pady=10)
        btn_dir.pack(padx=60, pady=10)
        btn_sort.pack(padx=60, pady=10)

    def check_dir(self):
        if self.APP_DIRECTORY != '-':
            print(self.APP_DIRECTORY)

    def sort_photos(self):
        write_dir = './pictures with animals'
        if not os.path.isdir(write_dir):
            os.mkdir(write_dir)
        else:
            i = 0
            while os.path.isdir(write_dir + '_' + str(i)):
                i += 1
            write_dir += str(i)
            os.mkdir(write_dir)
        for file in glob.glob(self.APP_DIRECTORY + '/*'):
            filename = file.split('/')[-1]
            img = cv2.imread(file)
            if img:
                print('checking image ')
                img = img[..., ::-1]
                result = len(self.model(img, size=640).xyxy[0].numpy())
                if result > 0:
                    cv2.imwrite(write_dir + '/' + filename, img)

    def choose_directory(self):
        directory = fd.askdirectory(title="Открыть папку", initialdir="/")
        if directory:
            self.APP_DIRECTORY = directory


def print_hi():
    model = yolov5.load('best.pt').cpu()
    img = cv2.imread('./05060578.JPG')[..., ::-1]
    pred = model(img, size=640)
    pred.show()
    results = pred.xyxy[0].numpy()
    print(len(results))


if __name__ == '__main__':
    app = App()
    app.mainloop()
