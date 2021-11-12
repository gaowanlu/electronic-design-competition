import sensor, image, time, math
import utils
import Message

class Code(object):
    model_flag=0x46
    value=0

codeData=Code()


#sensor.reset()
#sensor.set_pixformat(sensor.GRAYSCALE)
#sensor.set_framesize(sensor.VGA) # High Res!
#sensor.set_windowing((640, 80)) # V Res of 80 == less work (40 for 2X the speed).
#sensor.skip_frames(time = 2000)
#sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
#sensor.set_auto_whitebal(False)  # 必须关闭此功能，以防止图像冲洗…
#clock = time.clock()

# 条形码检测可以在OpenMV Cam的OV7725相机模块的640x480分辨率下运行。
# 条码检测也将在RGB565模式下工作，但分辨率较低。 也就是说，
# 条形码检测需要更高的分辨率才能正常工作，因此应始终以640x480的灰度运行。

def find_code():
#roi=[100,0,120,240]
    img=sensor.snapshot()
    codes = img.find_barcodes()
    for code in codes:
        img.draw_rectangle(code.rect())#画矩形
        print_args = ( code.payload())
        print("-----------------------------------------Payload \"%s\"" % print_args)
        value=int(print_args)
        if(value<3 or value>6):
            value=0
        codeData.value=value
    #color,flag,x,y,T_ms,mode_flag
    Message.UartSendData(Message.DotDataPack(0,codeData.value,0,0,0,codeData.model_flag))
    if not codes:
        print("-----------------------------------------No Code")
