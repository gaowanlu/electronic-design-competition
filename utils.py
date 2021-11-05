IMG_WIDTH = 160
IMG_HEIGHT = 120
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
        return (cross_x, cross_y)#返回交点
    else:#没有交点
        return None



'''计算两个直线的角度'''
def calculate_angle(line1, line2):
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle

'''图像中找最大的某个阈值色块'''
def find_maxSizeBlob_byThreshold(img,threshold):
    result=None
    blobs = img.find_blobs([threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    for blob in blobs:
        if(result==None):
            result=blob
        elif(result.w()*result.h()<blob.w()*blob.h()):
            result=blob
    return result

'''画矩形'''
def draw_blob(img,blob):
    if(blob!=None):
        img.draw_rectangle(blob.rect())#画矩形


