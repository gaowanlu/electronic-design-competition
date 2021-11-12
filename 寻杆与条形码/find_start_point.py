import utils
import Message

#家参数(0, 21, -17, 15, -31, 13)
#场地参数(2, 26, -33, 16, -22, 31)
startPoint_threshold =(2, 26, -33, 16, -22, 31)
CROSS_MIN=10
CROSS_MAX=90

class StartDot(object):
    flag = 0
    color = 0
    x = 0
    y = 0
STARTDOT=StartDot()

'''寻找十字起点'''
def find_start_point_blob(img):
    #重置标志位
    STARTDOT.flag=0;
    blobs = img.find_blobs([startPoint_threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    result=None
    last_sub=2.0
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        rate=width/height
        size_limit=width>CROSS_MIN and width<CROSS_MAX and height>CROSS_MIN and height<CROSS_MAX
        sub=abs(1.0-rate)
        if(last_sub>sub and size_limit):
            print(width,height,rate)#
            last_sub=sub
            result=blob
    #十字检测
    if result!=None:
        cross_test_result,point=find_crossShape(img,result.rect())
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            utils.draw_blob(img,result)
            img.draw_cross(point[0],point[1],5,color=[0,255,0])
            STARTDOT.flag=1
            STARTDOT.x=point[0]-int(utils.IMG_WIDTH/2)
            STARTDOT.y=point[1]-int(utils.IMG_HEIGHT/2)
    sendMessage()
    return result


'''测试十字'''
def find_crossShape(img,ROI):
    result=False
    result_point=(-1,-1)
    if(ROI==None):
        return result,result_point
    lines=img.find_lines(roi=ROI, theta_margin = 25, rho_margin = 25)
    line_num = len(lines)
    for i in range(line_num -1):
            for j in range(i, line_num):
                # 判断两个直线之间的夹角是否为直角
                angle = utils.calculate_angle(lines[i], lines[j])
                print("Angle",angle)
                # 判断角度是否在阈值范围内
                if not(angle >= 83 and angle <=  90):
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
                return (True,result_point)
    return (result,result_point)

'''找圆形'''
def find_cirlce_method(img):
    STARTDOT.flag=0
    for c in img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max = 100, r_step = 2):
        #十字检测
        leaf_radius=int(c.r()/2.0);
        ROI=[c.x()-leaf_radius,c.y()-leaf_radius,c.x()+leaf_radius,c.y()+leaf_radius]
        cross_test_result,point=find_crossShape(img,ROI)
        print("cross_test_result",cross_test_result,point)
        if(cross_test_result):
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
            STARTDOT.flag=1
            STARTDOT.x=c.x()-int(utils.IMG_WIDTH/2)
            STARTDOT.y=c.y()-int(utils.IMG_HEIGHT/2)
            print(c)
    sendMessage()

'''发包'''
def sendMessage():
    #color,flag,x,y,T_ms
    pack=Message.DotDataPack(0,STARTDOT.flag,STARTDOT.x,STARTDOT.y,Message.Ctr.T_ms,0x43)
    Message.UartSendData(pack)
    STARTDOT.flag=0#重置标志位


