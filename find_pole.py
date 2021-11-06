import sensor, image,struct,math
import utils
import Message
class Pole(object):
    flag=0
    x=0
    y=0
    angle=0
    distance=0

poleData=Pole()
IMG_CENTER_X=int(utils.IMG_WIDTH/2)
IMG_CENTER_Y=int(utils.IMG_HEIGHT/2)

black_threshold=(18, 47, -31, 3, -42, -16)

def find_color_pole(img):
    poleData.flag=0
    pixels_max=0
    #直接找色块  找出像素最多的
    for b in img.find_blobs([black_threshold],merge=False):
        if pixels_max<b.pixels() and b.w()<47 and b.w()>5 and b.w()*1.5<b.h():
            img.draw_rectangle(b[0:4])#圈出搜索到的目标
            poleData.flag = 1
            pixels_max=b.pixels()
            poleData.x = b.x()+int(b.w()/2)
            poleData.y = b.y()
            poleData.distance=b.cx()-int(utils.IMG_WIDTH/2)
            img.draw_cross(poleData.x,poleData.y, color=127, size = 15)
            img.draw_circle(poleData.x,poleData.y, 15, color = 127)

def sendData():
    # flag==1直线 0无效  angle夹角  distance距离中心水平距离正负值    crossflag永为0
    #def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms)
    Message.UartSendData(Message.LineDataPack(poleData.flag,poleData.angle,poleData.distance,0,0,0,Message.Ctr.T_ms))

def check_pole():
    img=sensor.snapshot()
    find_color_pole(img)
    sendData()

