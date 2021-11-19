# electronic-design-competition
China 2021 Electronic Design Competition  
2021 大学生电子设计竞赛无人机 G题 (植保无人机) 视觉解决方案  
Create By Gao Wanlu   
email:  2209120827@qq.com  | heizuboriyo@gmail.com     

  
## 硬件解决方案
前视OpenMV与下视OpenMV ， 双OpenMV解决方案 。

### 项目目录结构  
/**.py 下视OpenMV   
/寻杆与条形码/**.py 前视OpenMV    

### 赛题整体解决方案
> 视觉只负责识别部分、采用定焦镜头、OpenMV只负责发送像素坐标系下的坐标信息  
> 其他解算等决策部分均由嵌入式控制解决   
> 解决思想：围绕田地即地图中的绿色边缘巡航喷洒  
> 主要解决问题:寻找边缘巡航、寻找A点、寻找停机坪、寻找黑色杆、寻找条形码   

### 视觉ROI模型建立
ROI模型图如 图表3所示，本项目采用视觉图像大小为 160*120（即宽为 160像素 高为120像素）。在图像中设计四个ROI区域，
![在这里插入图片描述](https://img-blog.csdnimg.cn/f2a33bd1eb9c441b878832c97412ae71.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

 
图表 3 ROI模型





### 利用ROI模型设计识别算法  
当右上区域的内绿色色块的高大于右上区域高的二分之一，与宽度大于右上区域宽的三分之二时，则应向右转。因为项目方案为逆时针方案旋转，所以只能遇到如图中的一种右转情况。

 ![在这里插入图片描述](https://img-blog.csdnimg.cn/6c2e07f44df64b2d85e6fd2e1b742877.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

图表 4 右转情况 注(阴影区域为绿色)


当只有中间区域与底部区域内具有绿色色块时，无人机应该向左转(注：逆时针绕行地图情况)。
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/af2420a969d240408affac77caddb148.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

图表 5 ROI模型 左转情况 注(阴影区域为绿色)
  
 
当只有中间区域与底部区域、左上区域具有色块与右上区域不满足右转条件时，无人机应该直行。
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/5afca08f245742058accbc55400ac143.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_19,color_FFFFFF,t_70,g_se,x_16)

图表 6  ROI模型 直行情况 注(阴影区域为绿色)

无人机在直行中利用视觉数据 a角度与distance 距离偏差 进行姿态校正，沿边飞行。
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/8479dbe710ad4b8a95973403a023fc03.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_19,color_FFFFFF,t_70,g_se,x_16)

图表 7 ROI模型 直行情况 注(阴影区域为绿色)
寻找“A”字体机器视觉解决方案：

 ![在这里插入图片描述](https://img-blog.csdnimg.cn/3b80b9dc7930442cad4050537329fcd4.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_13,color_FFFFFF,t_70,g_se,x_16)

图表 8  ROI模型 寻找A 注(阴影区域为绿色)
	
当无人机利用程序控制从起点起飞后或者喷洒完毕后到A字体之上时，无人机向上位机发送识别A字体的通信指令，上位机首先在无人机下方视野中寻找绿色ROI区域(使用LAB色彩模型进行二值化与轮廓寻找可以很好解决)，再利用如图中的ROI1区域作为下一步的感性区域。在ROI1区域中寻找最大的黑色轮廓，并将其范围作为ROI2区域。下一步利用霍夫直线检测
算法检测ROI2内的直线，在直线集合中寻找是否有满足类似于“A”字体如图中a角范围，判断ROI2内是否为“A”字体。
当上位机在相机视野中寻找到“A”时，将ROI 2 中心点在像素坐标系下的坐标通过串口通信将数据发送至下位机。如何调整无人机姿态由嵌入式程序进行控制。
为什么不采用神经网络或者机器学习等算法来识别“A”？原因有如下击点原因：1、对于OpenMV轻量级机器视觉计算平台算力有限，难以流畅运行机器学习模型。2、要采用简单解决方案解决问题，往往简单的算法鲁棒性更强。


寻找“停机坪”机器视觉解决方案：
 ![在这里插入图片描述](https://img-blog.csdnimg.cn/c008206d58214e8b98becdd239e2af37.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_16,color_FFFFFF,t_70,g_se,x_16)

图表 9  停机坪
与“A”字体识别方案类似，当无人机到达停机坪附近时下位机通过串口通信通知OpenMV,首先在相机视野中寻找最大的黑色轮廓区域(在地图中停机坪的背景色为白色，利用LAB进行阈值调整为二值图，只留下黑色区域)。在图中ROI区域内使用霍夫直线检测算法查找是否有两条直线在图像坐标系下具有交点，且二者的夹角类似于90度。通过以上筛选范围将两直线的交点发送至下位机，有嵌入式程序进行无人机的姿态调整。


寻找黑色杆与识别条形码机器视觉解决方案：
![在这里插入图片描述](https://img-blog.csdnimg.cn/b894cb4d4e9d419f9ff005d6a1e8b2f4.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

 
图表 10  识别黑色杆与条形码

解决此问题需要解决两个难点：1、如何寻找黑色杆使得无人机前方的相机镜头尽可能正对黑色杆方向。2、采用QVGA分辨率(320*240)的条件且无人机距离杆较远的情况下如何识别到条形码。
解决方案：同样原理当需要识别二维码时下位机向上位机发送指令，无人机前方的OpenMV装配有长焦镜头原因：1、能够观察的更远、使得远处的特征更加清晰提高条形码识别的成功率。2、缩小视野范围，尽可能排除非黑色杆其他的黑色区域的干扰。
首先在相机视野中寻找符合一定长宽比的黑色区域，寻找到符合条件的ROI1区域，在ROI1 区域根据ROI1范围的宽与长划定ROI2区域，在ROI2区域内识别条形码，如有识别到条形码，将条形码代表的数字发送至下位机，有下位机记录条形码数值，当在停机坪降落时做出降落位置的调整。


## 赛题详情  
![在这里插入图片描述](https://img-blog.csdnimg.cn/5b54da5f961e42a18a591d5ce8a1177d.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)
![在这里插入图片描述](https://img-blog.csdnimg.cn/c737a9c3df9c4643aeaa95cbbb02ee14.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)
![在这里插入图片描述](https://img-blog.csdnimg.cn/b5650e31980f455981853659799d613b.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

![在这里插入图片描述](https://img-blog.csdnimg.cn/b2a83848b4614f088fa2aa61e4017c1e.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)
![在这里插入图片描述](https://img-blog.csdnimg.cn/e3501fe826cd43bc84953d298ffa7155.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)

![在这里插入图片描述](https://img-blog.csdnimg.cn/4c11badf0d2e4dde91d781c6d959b8bc.png?x-oss-process=image/watermark,type_ZHJvaWRzYW5zZmFsbGJhY2s,shadow_50,text_Q1NETiBAd2FubHVOMQ==,size_20,color_FFFFFF,t_70,g_se,x_16)
