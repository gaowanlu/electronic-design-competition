import utils
from pyb import LED,Timer
import math
import Message
Green_threshold=(36, 75, -79, -36, -12, 55)
A_threshold=(0, 36, -59, 8, -8, 74)
#A 家 (0, 21, -23, 10, -19, 25)
#A 场地 (13, 40, -36, 4, 5, 38)
class ADot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
ADOT=ADot()

'''寻找A字'''
def find_A_blob(img):
    ADOT.flag=0;#重置没有找到
    blobs = img.find_blobs([A_threshold], merge=True)
    result=None
    #4.3  4.8 0.895   short/long
    #62 69  27 29
    last_sub=100.0
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        short_side=width if width<height else height
        long_side=width if width>height else height
        rate=short_side/long_side
        #print("A",width,height,rate)
        #sub=math.fabs(0.7407-rate)
        side_limit=short_side>8 and short_side<68
        side_limit=side_limit and long_side>13 and long_side<68#and side_limit
        #if(sub<last_sub and side_limit and and find_AShape(img,blob) ):
        if(side_limit):
            #last_sub=sub
            result=blob
        #utils.draw_blob(img,blob)
    if result!=None:
        utils.draw_blob(img,result)
        #更新要发送的数据
        print("SEND X Y: ",result.cx(),result.cy())
        ADOT.flag=1
        ADOT.x=result.cx()-int(utils.IMG_WIDTH/2)
        ADOT.y=result.cy()-int(utils.IMG_HEIGHT/2)
        LED(3).toggle()
    else:
        LED(3).off()
    #发送数据
    sendMessage()
    return result




'''测试A字'''
def find_AShape(img,blob):
    result=False
    if(blob==None):
        return result
    ROI=(blob.rect())
    lines=img.find_lines(roi=ROI,x_stride=1,y_stride=1, theta_margin = 25, rho_margin = 25)
    line_num = len(lines)
    for i in range(line_num -1):
            for j in range(i, line_num):
                # 判断两个直线之间的夹角是否为直角
                angle = utils.calculate_angle(lines[i], lines[j])
                print("Angle",angle)
                # 判断角度是否在阈值范围内
                if not(angle >= 20 and angle <=  50):
                    continue#不在区间内
                intersect_pt = utils.CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    continue
                #有交点
                x, y = intersect_pt
                #不在图像范围内
                if not(x >= 0 and x < utils.IMG_WIDTH and y >= 0 and y < utils.IMG_HEIGHT):
                    # 交点如果没有在画面中
                    continue
                result_point=(x,y)
                return True
    return result

'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=Message.DotDataPack(0,ADOT.flag,ADOT.x,ADOT.y,Message.Ctr.T_ms,0x44)
    Message.UartSendData(pack)
    ADOT.flag=0#重置标志位


