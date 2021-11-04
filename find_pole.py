import sensor, image, time
import utils
pole_threshold=(32, 52, 3, 26, 24, 49)
def find_pole(img):
    blobs = img.find_blobs([pole_threshold], pixels_threshold=3, area_threshold=3, merge=True, margin=5)
    result=None
    for blob in blobs:
        width=blob.w()
        height=blob.h()
        rate=width/height
        print(width,height,rate)#
        result=blob
        utils.draw_blob(img,result)
    return result

