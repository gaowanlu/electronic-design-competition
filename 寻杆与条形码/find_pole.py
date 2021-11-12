import sensor, image,struct,math
import utils
import Message
import find_code
class Pole(object):
    flag=0
    x=0
    y=0
    angle=0
    distance=0

poleData=Pole()


IMG_CENTER_X=int(utils.IMG_WIDTH/2)
IMG_CENTER_Y=int(utils.IMG_HEIGHT/2)

black_threshold=(0, 21, -26, 28, -24, 20)

def find_color_pole():
    img=sensor.snapshot()
    poleData.flag=0
    pixels_max=0
    #直接找色块  找出像素最多的
    blobs=img.find_blobs([black_threshold], merge=False)
    for b in blobs:
        if pixels_max<b.pixels() and b.w()<55 and b.w()>3 and b.w()*1.2<b.h() and b.h()>20:
            img.draw_rectangle(b[0:4])#圈出搜索到的目标
            poleData.flag = 1
            pixels_max=b.pixels()
            poleData.x = b.x()+int(b.w()/2)
            poleData.y = b.y()
            poleData.distance=int((b.cx()-int(utils.IMG_WIDTH/2))/2)
            img.draw_cross(poleData.x,poleData.y, color=127, size = 15)
            #img.draw_circle(poleData.x,poleData.y, 15, color = 127)

def sendData():
    # flag==1直线 0无效  angle夹角  distance距离中心水平距离正负值    crossflag永为0
    #def LineDataPack(flag,angle,distance,crossflag,crossx,crossy,T_ms)
    Message.UartSendData(Message.LineDataPack(poleData.flag,poleData.angle,poleData.distance,0,0,0,Message.Ctr.T_ms))

def check_pole():
    find_color_pole()
    sendData()

