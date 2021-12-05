import cv2
import yolov5
import os
import glob
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import StringVar
from tkinter import ttk
from PIL import Image, ImageTk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.FROM_DIRECTORY = './'
        self.TO_DIRECTORY = '_with_animals_'
        self.mode = StringVar()
        self.model = yolov5.load('best.pt').cpu()

        self.title("Распознавание животных WildHack")
        self.geometry('1000x562')
        self.resizable(False, False)
        self.image = Image.open("./items/logo1.png")
        self.img_copy = self.image.copy()
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background = tk.Label(self, image=self.background_image)
        self.background.pack(fill=tk.BOTH, expand=tk.YES)
        self.background.bind('<Configure>', self._resize_image)

        self.fontExample = ("Courier", 16, "bold")
        self.comboExample = ttk.Combobox(self, values=[
            "Обрезать видео",
            "Отобрать фото"],
                                         font=self.fontExample, textvariable=self.mode)
        self.comboExample.current(0)
        self.option_add('*TCombobox*Listbox.font', self.fontExample)
        self.comboExample.place(x=50, y=50)

        self.lbl1 = tk.Label(self, text="Выберите исходную папку", font=("Montserrat Bold", 16), bg='white')
        self.lbl1.place(x=50, y=112)

        self.btn1 = tk.Button(self, text="Обзор", command=self.choose_directory_from, font=("Arial Bold", 10), height=2,
                              width=55, foreground="green", activeforeground="red")
        self.btn1.place(x=50, y=140)

        self.lbl2 = tk.Label(self, text="Выберите папку для загрузки результата", font=("Montserrat Bold", 16),
                             bg='white', foreground="darkOrchid")
        self.lbl2.place(x=50, y=262)

        self.btn2 = tk.Button(self, text="Обзор", command=self.choose_directory_to, font=("Arial Bold", 10), height=2,
                              width=55, foreground="green", activeforeground="red")
        self.btn2.place(x=50, y=290)

        self.lbl4 = tk.Label(self, text='./<photo/video>/with_animals',
                             font=("Montserrat", 13), foreground="grey", bg='white')
        self.lbl4.place(x=50, y=350)

        self.btn_start = tk.Button(self, text='СТАРТ', command=self.work_with_nn, width=10, height=1, state=tk.DISABLED)
        self.btn_start.place(x=50, y=400)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=230, mode='determinate')

    def _resize_image(self, event):

        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)

    def choose_directory_from(self):
        directory = fd.askdirectory(title="Открыть папку", initialdir="/")
        if directory:
            self.btn_start['state'] = tk.NORMAL
            self.FROM_DIRECTORY = directory
            self.lbl3 = tk.Label(self, text=directory, font=("Montserrat", 13), foreground="grey", bg='white')
            self.lbl3.place(x=50, y=200)

    def choose_directory_to(self):
        directory = fd.askdirectory(title="Открыть папку", initialdir="/")
        if directory:
            self.TO_DIRECTORY = directory
            self.lbl4['text'] = directory

    def work_with_nn(self):
        if self.mode.get() == 'Отобрать фото':
            self.sort_photos()
        else:
            self.cut_video()

    def sort_photos(self):
        self.progress_bar.place(x=200, y=410)
        self.progress_bar["value"] = 0
        self.update()
        write_dir = self.TO_DIRECTORY
        if write_dir == '_with_animals_':
            write_dir = './photos' + self.TO_DIRECTORY
            i = 0
            while os.path.isdir(f'{write_dir}{i}'):
                i += 1
            write_dir += str(i)
            os.mkdir(write_dir)
        self.progress_bar['maximum'] = len([name for name in os.listdir(self.FROM_DIRECTORY)])
        for file in glob.glob(self.FROM_DIRECTORY + '/*'):
            self.progress_bar["value"] += 1
            self.update()
            filename = file.split('/')[-1]
            img = cv2.imread(file)
            if img is not None:
                img = img[..., ::-1]
                result = len(self.model(img, size=640).xyxy[0].numpy())
                if result > 0:
                    img = img[..., ::-1]
                    cv2.imwrite(write_dir + '/' + filename, img)

        self.progress_bar.place_forget()
        self.update()

    def cut_video(self):
        self.progress_bar.place(x=200, y=410)
        self.update()
        self.progress_bar["value"] = 0
        write_dir = self.TO_DIRECTORY
        if write_dir == '_with_animals_':
            write_dir = './videos' + self.TO_DIRECTORY
            i = 0
            while os.path.isdir(f'{write_dir}{i}'):
                i += 1
            write_dir += str(i)
            os.mkdir(write_dir)
        file_count = 0
        frames = []
        for file in glob.glob(self.FROM_DIRECTORY + '/*'):
            vid = cv2.VideoCapture(file)
            if vid.isOpened():
                self.progress_bar['maximum'] = vid.get(cv2.CAP_PROP_FRAME_COUNT)
                frame_width = int(vid.get(3))
                frame_height = int(vid.get(4))
                fps = vid.get(cv2.CAP_PROP_FPS)
                frame_size = (frame_width, frame_height)
                while vid.isOpened():
                    ret, frame = vid.read()
                    if ret:
                        self.progress_bar["value"] += 1
                        self.update()
                        img = frame[..., ::-1]
                        result = len(self.model(img, size=640).xyxy[0].numpy())
                        if result > 0:
                            frames.append(frame)
                        else:
                            if len(frames) > 25:
                                create_video_file(write_dir + '/animal_{0:05}.avi'.format(file_count),
                                                  frames, fps, frame_size)
                                file_count += 1
                            frames.clear()
                    else:
                        break

                if len(frames) > 25:
                    create_video_file('./animal_{0:05}.avi'.format(file_count),
                                      frames, fps, frame_size)
                file_count += 1
                frames.clear()

            self.progress_bar["value"] = 0
            vid.release()
        self.progress_bar.place_forget()
        self.update()


def create_video_file(name, frames, fps, frame_size):
    out = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*'XVID'), fps, frame_size)
    for fr in frames:
        out.write(fr)
    out.release()


if __name__ == '__main__':
    app = App()
    app.mainloop()
