import sensor, image, time, math, struct
# import json
import Message

#上中下有 左有右无  或者 右有左无 直走
#

Green_threshold =(47, 70, -26, -10, -5, 11)# 寻绿线
rad_to_angle = 57.29#弧度转度
IMG_WIDTH = 160
IMG_HEIGHT = 120

# 取样窗口
#（x1,y1,x2,y2）
ROIS = {
    'down':   (0, 105, 160, 15), # 横向取样-下方       1
    'middle': (0, 52,  160, 15), # 横向取样-中间       2
    'up':     (0,  0,  160, 15), # 横向取样-上方       3
    'left':   (0,  0,  15, 120), # 纵向取样-左侧       4
    'right':  (145,0,  15, 120), # 纵向取样-右侧       5
    'All':    (0,  0,  160,120), # 全画面取样-全画面    6
}

'''交互数据'''
class Line(object):
    flag = 0
    color = 0
    angle = 0
    distance = 0
    cross_x=0
    cross_y=0
    cross_flag=0

class LineFlag(object):
    turn_left = 0
    turn_right = 0

LineFlag=LineFlag()
Line=Line()


# 计算两直线的交点
def CalculateIntersection(line1, line2):
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()
    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))

        Line.cross_flag = 1
        #坐标系变换
        #变换为原点在中心的坐标
        Line.cross_x = cross_x-80
        Line.cross_y = cross_y-60
        #调试 画出来
        img.draw_cross(cross_x,cross_y,5,color=[255,0,0])
        return (cross_x, cross_y)#返回交点
    else:#没有交点
        Line.cross_flag = 0
        Line.cross_x = 0
        Line.cross_y = 0
        return None

'''
利用四边形的角公式， 计算出直线夹角
if line.theta()>90:
#line.theta():0-90 Y+半轴和直线的夹角,90-180 Y-半轴和直线的夹角
    theta_err = line.theta()-180
else:
    theta_err = line.theta()
'''
def calculate_angle(line1, line2):
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle


'''
根据夹角阈值寻找两个相互交叉的直线， 且交点需要存在于画面中
'''
#def find_interserct_lines(lines, angle_threshold=(10,90), window_size=None):
    #line_num = len(lines)
    ##迭代 向后两两组队
    #for i in range(line_num -1):
        #for j in range(i, line_num):
            ## 判断两个直线之间的夹角是否为直角
            #angle = calculate_angle(lines[i], lines[j])
            ## 判断角度是否在阈值范围内
            #if not(angle >= angle_threshold[0] and angle <=  angle_threshold[1]):
                #continue#不在区间内

            ## 判断交点是否在画面内
            #if window_size is not None:
                ## 获取窗口的尺寸 宽度跟高度
                #win_width, win_height = window_size
                ## 获取直线交点
                #intersect_pt = CalculateIntersection(lines[i], lines[j])
                ## 没有交点
                #if intersect_pt is None:
                    #Line.cross_x = 0
                    #Line.cross_y = 0
                    #Line.cross_flag = 0
                    #continue
                ##有交点
                #x, y = intersect_pt
                ##不在图像范围内
                #if not(x >= 0 and x < win_width and y >= 0 and y < win_height):
                    ## 交点如果没有在画面中
                    #Line.cross_x = 0
                    #Line.cross_y = 0
                    #Line.cross_flag = 0
                    #continue
            ##返回目标两直线:符合角度范围限制与直线在图像中有交点
            #return (lines[i], lines[j])

    #return None



'''
在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
'''
#寻找每个感兴趣区里的指定色块并判断是否存在
def find_blobs_in_rois(img):
    global ROIS #全局变量
    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    #根据json 属性名称生成结果对象
    for roi_direct in ROIS.keys():#数值复位
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }

    # 遍历定义的ROIS矩形
    for roi_direct, roi in ROIS.items():
        #在定义的ROI找色块
        blobs=img.find_blobs([Green_threshold], roi=roi, merge=True, pixels_area=10)
        #没找到则迭代下一个ROI
        if len(blobs) == 0:
            continue
        #选出最大的色块
        largest_blob = max(blobs, key=lambda b: b.pixels())
        #得到色块的坐标与宽高信息
        x,y,width,height = largest_blob[:4]

        #根据色块大小进行过滤
        if not(width >=3 and width <= 45 and height >= 3 and height <= 45):
             #根据色块的长宽进行过滤
            continue#迭代下一个ROI

        #在此ROI找到符合要求的色块，记录中心坐标
        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True

        #将其画出进行调试
        img.draw_rectangle((x,y,width, height), color=(0,255,255))

    # 判断是否需要左转与右转
    LineFlag.turn_left = False#先清除左转标志位
    LineFlag.turn_right = False#清除右转



    #上面没有 且 下面有 且 （左无右有 或者 右无左有）
    if (not roi_blobs_result['up']['blob_flag'] ) and roi_blobs_result['down']['blob_flag'] and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        # 确定是向左还是向右
        if roi_blobs_result['left']['blob_flag']:
            LineFlag.turn_left = True
        if roi_blobs_result['right']['blob_flag']:
            LineFlag.turn_right = True

    #上有 且 中有 且 下有    大可能走直线
    #此处右行走优先级  走直线最优先  其次向左  其次向右
    if (roi_blobs_result['up']['blob_flag']and roi_blobs_result['middle']['blob_flag']and roi_blobs_result['down']['blob_flag']):
        Line.flag = 1#直线
    elif LineFlag.turn_left:
        Line.flag = 2#左转
    elif LineFlag.turn_right:
        Line.flag = 3#右转
        #下没有 上有  右有或者左有(两个只能走一个)
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.flag = 1
        #左右转后直线（并没有在上方时 就能转弯的决策 走过点 将线条全部置于后半部分 再进行转弯 转弯之后，则上面有色块 且左右也会有 会走直线处理）
    else:
        Line.flag = 0#未检测到


    #图像上显示检测到的直角类型
    turn_type = 'N' # 啥转角也不是
    if LineFlag.turn_left:
        turn_type = 'L' # 左转
    elif LineFlag.turn_right:
        turn_type = 'R' # 右转

    #调试显示左转还是右转
    img.draw_string(0, 0, turn_type, color=(255,255,255))


    #计算角度
    CX1 = roi_blobs_result['up']['cx'] #上方最大色块中心点X
    CY1 = roi_blobs_result['up']['cy']
    CX2 = roi_blobs_result['middle']['cx']#中间部分最大色块中心点X
    CY2 = roi_blobs_result['middle']['cy']
    CX3 = roi_blobs_result['down']['cx']
    CY3 = roi_blobs_result['down']['cy']

    #计算中心部分最大色块中心点 距离中心源点的距离 大概就是中心偏移量
    if  Line.flag:
        Line.distance = CX2-80
    else:
        Line.distance = 0

    # 向左或者向右转
    if LineFlag.turn_left or LineFlag.turn_right:
        Line.angle = math.atan((CX2-CX3)/(CY2-CY3))* rad_to_angle
        Line.angle = int(Line.angle)

    #走直线
    elif Line.flag==1 and (roi_blobs_result['down']['blob_flag'] and roi_blobs_result['up']['blob_flag'] ):
        Line.angle = math.atan((CX1-CX3)/(CY1-CY3))* rad_to_angle
        Line.angle = int(Line.angle)

    #左右只有一个能走
    elif (not roi_blobs_result['down']['blob_flag'] ) and roi_blobs_result['up']['blob_flag']and ( roi_blobs_result['right']['blob_flag'] or roi_blobs_result['left']['blob_flag'])and roi_blobs_result['left']['blob_flag'] != roi_blobs_result['right']['blob_flag']:
        Line.angle = math.atan((CX1-CX2)/(CY1-CY2))* rad_to_angle
        Line.angle = int(Line.angle)
    #无路可走
    else:
        Line.angle = 0


#线检测
def LineCheck(img):
    ##lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)
    ## 没有找到任何直线
    #if not lines:
        #Line.cross_x=Line.cross_y= Line.cross_flag=0#偏移量清零

    ## 寻找相交的点 要求满足角度阈值,如果又符合的两条的直线、则返回结果元组
    #find_interserct_lines(lines, angle_threshold=(45,90), window_size=(IMG_WIDTH, IMG_HEIGHT))
    #print('交点坐标',Line.cross_x,-Line.cross_y, Line.cross_flag)

    # 在交点出取ROI,逻辑巡线
    find_blobs_in_rois(img)


    #寻线数据打包发送
    #将数据有效标志、与目的方向的偏差角度、距离中心的位置、是否有交叉线、交叉线坐标、帧率
    #直接打包发送
    Message.UartSendData(Message.LineDataPack(Line.flag,Line.angle,Line.distance,Line.cross_flag,Line.cross_x,Line.cross_y,Message.Ctr.T_ms))
    return Line.flag
