import sensor, image, time, math, struct
import json
import Message
green_threshold = (44, 88, -31, -5, -9, 24)
rad_to_angle = 57.29#弧度转度

# 取样窗口
# 根据分辨率修改！
'''
ROIS = {
    'down':   (0, 105, 160, 15), # 横向取样-下方       1
    'middle': (0, 52,  160, 15), # 横向取样-中间       2
    'up':     (0,  0,  160, 15), # 横向取样-上方       3
    'left':   (0,  0,  15, 120), # 纵向取样-左侧       4
    'right':  (145,0,  15, 120), # 纵向取样-右侧       5
    'All':    (0,  0,  160,120), # 全画面取样-全画面    6
}
'''

class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0

Line=Line()

def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:#两条线不平行，斜率不相等
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))

        Line.cross_flag = 1
        Line.cross_x = cross_x-80
        Line.cross_y = cross_y-60
        img.draw_cross(cross_x,cross_y,5,color=[255,0,0])
        return (cross_x, cross_y)
    else:
        Line.cross_flag = 0
        Line.cross_x = 0
        Line.cross_y = 0
        return None

def calculate_angle(line1, line2):
    '''
    利用四边形的角公式， 计算出直线夹角
    '''
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle

def find_interserct_lines(lines, angle_threshold=(10,90), window_size=None):
    '''
    根据夹角阈值寻找两个相互交叉的直线， 且交点需要存在于画面中
    '''
    line_num = len(lines)
    for i in range(line_num -1):
        for j in range(i, line_num):
            # 判断两个直线之间的夹角是否为直角
            angle = calculate_angle(lines[i], lines[j])
            # 判断角度是否在阈值范围内
            if not(angle >= angle_threshold[0] and angle <=  angle_threshold[1]):
                continue

            # 判断交点是否在画面内
            if window_size is not None:
                # 获取窗口的尺寸 宽度跟高度
                win_width, win_height = window_size
                # 获取直线交点
                intersect_pt = CalculateIntersection(lines[i], lines[j])
                if intersect_pt is None:
                    # 没有交点
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
                x, y = intersect_pt
                if not(x >= 0 and x < win_width and y >= 0 and y < win_height):
                    # 交点如果没有在画面中
                    Line.cross_x = 0
                    Line.cross_y = 0
                    Line.cross_flag = 0
                    continue
            return (lines[i], lines[j])
    return None

#寻找每个感兴趣区里的指定色块并判断是否存在
def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    IMG_WIDTH = img.width()
    IMG_HEIGHT = img.height()

    ROIS = {
        'UL':       (0, 0, 30, int(IMG_HEIGHT/4)),
        'UR':       (50, 0, 30, int(IMG_HEIGHT/4)),
        'middle':   (0, int(IMG_HEIGHT/2), int(IMG_WIDTH), int(IMG_HEIGHT/4)),
        'down':     (0, int(3*IMG_HEIGHT/4), int(IMG_WIDTH), int(IMG_HEIGHT/4)),
        # 'all':      (0,  0,  160,120),
    }

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():  # 数值复位
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }

    # 遍历所有ROI区域，寻找色块并取最大色块
    for roi_direct, roi in ROIS.items():

        if Message.Ctr.IsDebug == 1:
            img.draw_rectangle(roi, color=(255,0,0))

        roix, roiy, roiw, roih = roi

        #寻找绿色色块
        blobs=img.find_blobs([green_threshold], roi=roi, merge=True, pixels_area=5)
        if len(blobs) == 0:
            continue
        # 取最大色块
        largest_blob = max(blobs, key=lambda b: b.pixels())  #lambda函数：匿名函数冒号前面是参数，冒号后面是返回的值
        if(largest_blob==None):
            continue
        x,y,width,height = largest_blob[:4]
        print("max blob: ", largest_blob[:4])
        # 根据色块过滤
        # 尺寸过小
        #if width < roiw/4 and height < roih/2):
            #continue
        # UR色块起点和尺寸异常
        #if roi_direct=='UR' \
            #and width < int(4*roiw/3) and x > int(roix + roiw/4) and y > int(roiy + roih/2):
            #continue

        if(roi_direct=='middle' or roi_direct=='UL' or roi_direct=='down'):
            roi_blobs_result[roi_direct]['cx'] = x+width
        roi_blobs_result[roi_direct]['cy'] = y
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if Message.Ctr.IsDebug == 1:
            img.draw_rectangle((x,y,width, height), color=(0,255,255))

    '''
    if (not roi_blobs_result['up']['blob_flag'] ) and roi_blobs_result['down']['blob_flag'] and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:  #下方有 左或右有
        if roi_blobs_result['left']['blob_flag']:
            LineFlag.turn_left = True
        if roi_blobs_result['right']['blob_flag']:
            LineFlag.turn_right = True
    if (roi_blobs_result['up']['blob_flag']and roi_blobs_result['middle']['blob_flag']and roi_blobs_result['down']['blob_flag']):   #前中后
        Line.flag = 1#直线
    elif LineFlag.turn_left:
        Line.flag = 2#左转
    elif LineFlag.turn_right:
        Line.flag = 3#右转
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.flag = 1#左右转后直线
    else:
        Line.flag = 0#未检测到
    '''

    # 左右都有，中下也有
    if roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['UR']['blob_flag'] \
        and roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 右转
        Line.flag = 3
    elif roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['middle']['blob_flag'] \
        and roi_blobs_result['down']['blob_flag']:
        # 直行
        Line.flag = 1
    elif roi_blobs_result['middle']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        # 左转
        Line.flag = 2
    elif roi_blobs_result['UL']['blob_flag']:
        # 刚结束左转 直行
        Line.flag = 1
    else:
        # 未检测到
        Line.flag = 0

    if Message.Ctr.IsDebug == 1:
        print("Line.flag: ", Line.flag)

    #图像上显示检测到的直角类型
    turn_type = 'N' # 不转
    if Line.flag == 2:
        turn_type = 'L' # 左转
    elif Line.flag == 3:
        turn_type = 'R' # 右转

    #计算角度
    CX1 = roi_blobs_result['UL']['cx']
    CX2 = roi_blobs_result['middle']['cx']
    CX3 = roi_blobs_result['down']['cx']
    CY1 = roi_blobs_result['UL']['cy']
    CY2 = roi_blobs_result['middle']['cy']
    CY3 = roi_blobs_result['down']['cy']
    if  Line.flag:
        Line.distance = CX2 - int(IMG_WIDTH/2)
    else:
        Line.distance = 0


    # 转弯
    if Line.flag==2 or Line.flag==3:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    # 直走
    elif Line.flag==1 and  roi_blobs_result['UL']['blob_flag'] and roi_blobs_result['down']['blob_flag']:
        Line.angle = math.atan((CX1-CX3)/(CY1-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    # 结束转弯后
    elif roi_blobs_result['UL']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    else:
        Line.angle = 0

    if Message.Ctr.IsDebug == 1:
        img.draw_string(0, 0, turn_type, color=(255,255,255))
        img.draw_string(int(IMG_WIDTH/8), 0, str(Line.angle), color=(255,255,255))

    '''
    #图像上显示检测到的直角类型
    turn_type = 'N' # 啥转角也不是
    if LineFlag.turn_left:
        turn_type = 'L' # 左转
    elif LineFlag.turn_right:
        turn_type = 'R' # 右转
    img.draw_string(0, 0, turn_type, color=(255,255,255))
    #计算角度
    CX1 = roi_blobs_result['up']['cx']
    CX2 = roi_blobs_result['middle']['cx']
    if  Line.flag:
        Line.distance = CX2-80
    else:
        Line.distance = 0
    CX3 = roi_blobs_result['down']['cx']
    CY1 = roi_blobs_result['up']['cy']
    CY2 = roi_blobs_result['middle']['cy']
    CY3 = roi_blobs_result['down']['cy']
    # 转弯
    if LineFlag.turn_left or LineFlag.turn_right:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    # 直走
    elif Line.flag==1 and (roi_blobs_result['down']['blob_flag'] and roi_blobs_result['up']['blob_flag'] ):
        Line.angle = math.atan((CX1-CX3)/(CY1-CY3))* rad_to_angle
        Line.angle = int(Line.angle)
    # 结束转弯后
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    else:
        Line.angle = 0
    '''

#线检测
def find_line():
    # 拍摄图片
    img = sensor.snapshot()
    find_blobs_in_rois(img)
    #print('交点坐标',Line.cross_x,-Line.cross_y, Line.cross_flag)
    #寻线数据打包发送
    Message.UartSendData(Message.LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Message.Ctr.T_ms))
    return Line.flag
