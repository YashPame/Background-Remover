from tkinter import *
from tkinter import filedialog, simpledialog
from tkinter.filedialog import askopenfile
import os
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp


class BGRemove():
    def __init__(self, model=1):
        self.model = model
        self.mpDraw = mp.solutions.drawing_utils
        self.mpSelfieSegmentation = mp.solutions.selfie_segmentation
        self.selfieSegmentation = self.mpSelfieSegmentation.SelfieSegmentation(self.model)

    def removeBG(self, img, imgBg=(255, 255, 255), threshold=0.1):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.selfieSegmentation.process(imgRGB)
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > threshold
        if isinstance(imgBg, tuple):
            _imgBg = np.zeros(img.shape, dtype=np.uint8)
            _imgBg[:] = imgBg
            imgOut = np.where(condition, img, _imgBg)
        else:
            imgOut = np.where(condition, img, imgBg)
        return imgOut


class BackgroundRemover:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x600+10+10")
        self.root.title("Remove/Change Background")
        Heading = Label(self.root, text="Remove/Change Background", font=("Times New Roman", 30, "bold"), relief=RIDGE,
                        bd=3)
        Heading.place(x=0, y=0, width=1200, height=60)

        self.Step1Frame = Frame(self.root, relief=RIDGE, bd=3)
        self.Step1Frame.place(x=25, y=100, width=350, height=470)
        self.Step1Image_Frame = Label(self.Step1Frame, relief=RIDGE, bd=3)
        self.Step1Image_Frame.place(x=25, y=70, width=300, height=300)

        AddImageButton = Button(self.Step1Frame, text="Add Image", command=self.AddImage)
        AddImageButton.place(x=25, y=380, width=100, height=30)

        RemoveBackgroundButton = Button(self.Step1Frame, text="Remove Background", command=self.RemoveBackground)
        RemoveBackgroundButton.place(x=175, y=380, width=150, height=30)

        self.segmentor = BGRemove()
        self.Step2Frame = Frame()
        self.Step3Frame = Frame()

    def AddImage(self):
        self.Step2Frame.destroy()
        self.Step3Frame.destroy()
        # print("Add Image")
        file = filedialog.askopenfilename()
        if file:
            self.filepath = os.path.abspath(file)
            # print(self.filepath)
            img = cv2.imread(self.filepath)
            if img.shape[0] > img.shape[1]:
                img = cv2.resize(img, (300, int(img.shape[0] * 300 / img.shape[1])))
            elif img.shape[0] < img.shape[1]:
                img = cv2.resize(img, (int(img.shape[1] * 300 / img.shape[0]), 300))
            else:
                img = cv2.resize(img, (300, 300))

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.im1 = Image.fromarray(img)
            self.BG_image = ImageTk.PhotoImage(image=self.im1)
            self.Step1Image_Frame.config(image=self.BG_image)

    def RemoveBackground(self):
        self.Step2Frame = Frame(self.root, relief=RIDGE, bd=3)
        self.Step2Image_Frame = Label(self.Step2Frame, relief=RIDGE, bd=3)

        img = cv2.imread(self.filepath)
        imgOut = self.segmentor.removeBG(img, (255, 255, 255))

        # print(imgOut.shape)
        if imgOut.shape[0] > imgOut.shape[1]:
            imgOutdisplay = cv2.resize(imgOut, (300, int(imgOut.shape[0] * 300 / imgOut.shape[1])))
        elif imgOut.shape[0] < imgOut.shape[1]:
            imgOutdisplay = cv2.resize(imgOut, (int(imgOut.shape[1] * 300 / imgOut.shape[0]), 300))
        else:
            imgOutdisplay = cv2.resize(imgOut, (300, 300))

        # print(imgOutdisplay.shape)
        self.Step2Frame.place(x=425, y=100, width=350, height=470)
        self.Step2Image_Frame.place(x=25, y=70, width=300, height=300)

        self.IW = imgOut
        imgOutdisplay = cv2.cvtColor(imgOutdisplay, cv2.COLOR_BGR2RGB)
        self.im2 = Image.fromarray(imgOutdisplay)
        self.BG_image2 = ImageTk.PhotoImage(image=self.im2)
        self.Step2Image_Frame.config(image=self.BG_image2)

        saveImgButton = Button(self.Step2Frame, text="Save Image", command=self.SaveImage_W)
        saveImgButton.place(x=25, y=380, width=100, height=30)

        AddBackgroundButton = Button(self.Step2Frame, text="Add Background", command=self.AddBackground)
        AddBackgroundButton.place(x=175, y=380, width=150, height=30)

    def SaveImage_W(self):
        file = filedialog.asksaveasfilename()
        if file:
            self.savepath = os.path.abspath(file)
            # print(self.savepath)
            cv2.imwrite(str(self.savepath) + ".png", self.IW)

    def AddBackground(self):
        self.Step3Frame.destroy()
        self.Step3Frame = Frame(self.root, relief=RIDGE, bd=3)
        self.Step3Image_Frame = Label(self.Step3Frame, relief=RIDGE, bd=3)

        file = filedialog.askopenfile(mode='r', filetypes=[('.jpg', '.png')])
        if file:
            self.filepath2 = os.path.abspath(file.name)
            # print(self.filepath2)

            img = cv2.imread(self.filepath)
            io = cv2.imread(self.filepath2)
            io = cv2.resize(io, (img.shape[1], img.shape[0]))

            imgOut = self.segmentor.removeBG(img, io)

            if imgOut.shape[0] > imgOut.shape[1]:
                imgOutdisplay = cv2.resize(imgOut, (300, int(imgOut.shape[0] * 300 / imgOut.shape[1])))
            elif imgOut.shape[0] < imgOut.shape[1]:
                imgOutdisplay = cv2.resize(imgOut, (int(imgOut.shape[1] * 300 / imgOut.shape[0]), 300))
            else:
                imgOutdisplay = cv2.resize(imgOut, (300, 300))

            self.Step3Frame.place(x=825, y=100, width=350, height=470)
            self.Step3Image_Frame.place(x=25, y=70, width=300, height=300)
            self.IBG = imgOut
            imgOutdisplay = cv2.cvtColor(imgOutdisplay, cv2.COLOR_BGR2RGB)
            self.im3 = Image.fromarray(imgOutdisplay)
            self.BG_image3 = ImageTk.PhotoImage(image=self.im3)
            self.Step3Image_Frame.config(image=self.BG_image3)

            saveImgButton = Button(self.Step3Frame, text="Save Image", command=self.SaveImage_BG)
            saveImgButton.place(x=25, y=380, width=100, height=30)

    def SaveImage_BG(self):
        file = filedialog.asksaveasfilename()
        if file:
            self.savepath = os.path.abspath(file)
            # print(self.savepath)
            cv2.imwrite(str(self.savepath) + ".png", self.IBG)


if __name__ == "__main__":
    root = Tk()
    obj = BackgroundRemover(root)
    root.mainloop()
