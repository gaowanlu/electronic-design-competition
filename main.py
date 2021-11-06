#sensor::感光模块,可以设置采集到的图片的格式等
import sensor, image, time, math, struct
import json
from pyb import LED,Timer
import find_a,find_start_point,find_pole,utils,find_pole
import find_code
import Message
import find_line
import video
import mjpeg, pyb

#---------------------------镜头初始化---------------------------#
#sensor.reset()
#sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
#sensor.set_framesize(sensor.QQVGA)#设置相机分辨率
#sensor.skip_frames(time=3000)#时钟
#sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
#clock = time.clock()#初始化时钟
#初始化镜头
sensor.reset()#清除掉之前摄像头存在的代码对于图片的设置
sensor.set_pixformat(sensor.RGB565)#设置相机模块的像素模式
#565说明存储RGB三个通道
#每个通道存储像素值所对应的二进制位分别是5，6，5
#RGB565与RGB比较
#通道  RGB565    RGB       变化RGB565
#R      10101   10101000    左移三位
#G      100010  10001000    左移两位
#B      00101   00101000    左移三位
sensor.set_framesize(sensor.QQVGA)#设置相机分辨率160*120
#预设大小   窗口宽度    窗口高度
#VGA        640         480
#QVGA       320         240
#QQVGA      160         120
sensor.skip_frames(time=3000)#时钟
#跳过一些刚开始不稳定的时间段，在开始读取图像
#sensor.skip_frames([n,time]) 跳帧方法
#sensor.skip_frames(20) 跳20帧
#sensor.skip_frames(time=2000) 跳2000ms即2s
sensor.set_auto_whitebal(False)#若想追踪颜色则关闭白平衡
#sensor.set_auto_gain() 自动增益开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动增益。
#sensor.set_auto_whitebal() 自动白平衡开启（True）或者关闭（False）。在使用颜色追踪时，需要关闭自动白平衡。
#sensor.set_auto_exposure(True, exposure_us=5000) # 设置自动曝光，exposure_us=为设置的曝光参数
# 这里的参数配置 QQVGA + exposure=5000 为官方推荐的高帧率模式
# sensor.get_exposure_us()获得此时的曝光参数 如不采用自动曝光 可以采用 int(sensor.get_exposure_us()*scale)
sensor.set_auto_gain(False)
sensor.set_auto_exposure(False)
sensor.skip_frames(time = 3000)
clock = time.clock()#初始化时钟

#VIDEO=mjpeg.Mjpeg("example.mjpeg")


#主循环line_filter = LineFilter
while(True):
    clock.tick()
    #读取串口数据更新接收体
    Message.UartReadBuffer()
    Message.Ctr.WorkMode=4
    #Message.Ctr.Shirk=1
    if(Message.Ctr.WorkMode==0):
        continue

    print("MODE",Message.Ctr.WorkMode,"Shirk ",Message.Ctr.Shirk)

    img = sensor.snapshot()#拍一张图像
    #VIDEO.add_frame(img)
    if(Message.Ctr.WorkMode==3):
        find_start_point.find_start_point_blob(img)
    elif(Message.Ctr.WorkMode==4):
        find_a.find_A_blob(img)
        #fps=int(clock.fps())
        #VIDEO.close(fps)
    elif(Message.Ctr.WorkMode==2):
        find_line.find_line()
    elif(Message.Ctr.WorkMode==6):
        find_pole.check_pole()
        find_code.find_code(img)
    print("fps: ",clock.fps())
    if Message.Ctr.IsDebug == 0:
        fps=int(clock.fps())
        Message.Ctr.T_ms = (int)(1000/fps)#1s内的帧数















