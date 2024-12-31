import random
import string
import numpy as np 
import math
dict_mdc={}#记录了各个dc的id与multiple performance value对照表
B=10#任务预算暂定为10

list = []#全部数据集


with open('all.txt', 'r') as f:#处理数据
    while(True):
        line = f.readline()
        if not line:
            break
        list.append(line.split())    #所有数据放进list 
for a in list:#初始化mp值
    dict_mdc[a[0]]=0.5
date=1#日期
time=['00','06','09','12','15','18','21']
while date<5:
    j=0#时刻
    while j<7:#一天内各时刻
    #变量声明
        dc_can={}#所有候选dc
        dc_b={}#候选dc的报价
        dc_cansort={}#排序后的候选dc
        dict_sdc={}#记录了各个dc的id与single performance value对照表,每轮任务开始前都要更新
        dc_re_data={}#记录了被雇佣的dc与其感知数据
        dc_re_buck={}#记录了被雇佣的dc与其buck值
        dc_re_b={}#记录了被雇佣的dc与其bid值
        dict_w={}#记录了各个dc的id与权重对照表
        dict_d={}#记录了各个dc的数据与真值距离对照表
        sumb=0#dc的总报价
        sum_m=0#multiple performance value的和
        sum_w=0#w的和
        td=0#上一轮发现的真值
        ctd=0#这一轮发现的真值
        utd=0#一个不重要的参数罢了
        dis=1000#初始距离设为一个很大的值
        i=0#标记了真值发现的轮数
        dissum=0#各个用户数据与真值之间距离的和
        data1_0=[]#一号零点的数据
        temp1_0=[]#一号零点的温度
        for a in list:#初始化所有sp值
            dict_sdc[a[0]]=0
        for a in list:#取出任务的数据放进data1_0
            if float(a[1])==date:
                if a[2].startswith(time[j]):
                    data1_0.append(a)
        for a in data1_0:#提取出所有潜在dc的报价并计算buck值 
            dc_b[a[0]]=random.randint(1,2)
            dc_can[a[0]]=[dict_mdc[a[0]]/dc_b[a[0]],dc_b[a[0]],dict_mdc[a[0]],a[5]]
        dc_cansort=sorted(dc_can.items(),key=lambda x:x[1][0],reverse=True)#将候选dc按照其buck值从高到低排序
        for a in dc_cansort:
            sumb=sumb+a[1][1]#计算bid值的总和
            if sumb<B:#如果没有超过预算，就可以雇佣
                dc_re_data[a[0]]=a[1][3]#提取出雇佣用户的感知数据
                dc_re_buck[a[0]]=a[1][0]#提取出雇佣用户的buck值
                dc_re_b[a[0]]=a[1][1]#提取出雇佣用户的bid值
            else:#否则 停止招聘
                break                
        
        for k,v in dc_re_data.items():#把温度数据提出来   
            temp1_0.append(float(v))
        temp10_std=np.std(temp1_0,ddof=1)#求出标准差
        while dis>0.001:#开始真值发现过程，直到两次真值的距离小于0.001
            i=i+1#轮数加一
            #初始化参数
            utd=0
            sum_m=0
            sum_w=0
            dissum=0
            td=ctd#上一轮计算出的真值作为td
            for k,v in dc_re_data.items():#truth update过程
                if i==1:#如果是第一轮真值发现，那就用dc的mpv
                    sum_m=sum_m+float(dict_mdc[k]) #计算dc的mpv的和作为分母
                    utd=utd+float(dict_mdc[k])*float(v)#计算加权数据的和
                    ctd=utd/sum_m#计算本轮真值
                else:#否则，就用dc的weight
                    sum_w=sum_w+float(dict_w[k])
                    utd=utd+float(dict_w[k])*float(v)
                    ctd=utd/sum_w
            dis=abs(ctd-td)#计算前后两次真值的距离，随后确定第i轮是否收敛
            for k,v in dc_re_data.items():#weight update过程
                dict_d[k]=math.pow((float(v)-float(ctd)),2)/temp10_std
                dissum=dissum+dict_d[k]
            for k,v in dc_re_data.items():
                dict_w[k]=math.log(dissum/dict_d[k])
        print(i)
        print (ctd)

        for k,v in dc_re_data.items():
            dict_sdc[k]=math.exp(-(abs(float(v)-float(ctd))))
            dict_mdc[k]=float(dict_mdc[k])*0.4+float(dict_sdc[k])*0.6
        j=j+1
    date=date+1

            
