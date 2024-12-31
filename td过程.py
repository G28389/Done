import random
import string
import numpy as np 
import math
dict_mdc={}#记录了各个dc的id与multiple performance value对照表
B=30#任务预算

list = []#全部数据集
y=1#参数

with open('all.txt', 'r') as f:#处理数据
    while(True):
        line = f.readline()
        if not line:
            break
        list.append(line.split())    #所有数据放进list 
for a in list:#初始化mp值
    dict_mdc[a[0]]=0.5
date=4#日期
time=['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
while date<5:
    j=0#时刻
    while j<24:#一天内各时刻
        data=[]#目标任务的候选数据
        dc_b={}#dc随机生成的报价

        #离线参数
        offdc_sort=[]#离线招聘下排序后的候选dc列表
        offdc_re=[]#离线招聘的dc
        offsum_mdc=0#离线招聘下的mpv和
        offsumb=0#离线招聘下dc报价之和
        offtemp_std=0#离线场景下的数据标准差
        offtemp=[]
        redc_data=[]
        #在线参数
        dc_ob=[]#观察集
        dc_obsort=[]#排序后的观察集
        sumb=0#在线招聘下dc的报价之和
        dc_sam=[]#在线招聘下的采样集
        dc_samsort=[]#排序后的采样集
        dcnum=0#在线招聘下预估招聘人数
        renum=0#实际招聘人数
        bp_sum=0#在线招聘下基础工资之和
        sum_mdc=0#在线招聘下的mpv和
        dc_re=[]#在线招聘的dc
        temp_std=0#在线场景下的数据标准差
        dict_w={}#记录了各个dc的id与权重对照表
        dict_d={}#记录了各个dc的数据与真值距离对照表
        avesum=0
        for a in list:#取出任务的数据放进data
            if float(a[1])==date:
                if a[2].startswith(time[j]):
                    data.append(a)
        for a in data:
            dc_b[a[0]]=random.uniform(0,2)#随机生成各个dc的报价，此报价同时适用于在线和离线
            a[1]=dict_mdc[a[0]]/dc_b[a[0]]#buck值
            a[2]=0#bp
            a[3]=0#ap
            a[4]=0#sp
        #先进行离线招聘
        offdc_sort=sorted(data,key=lambda x:x[1],reverse=True)#将候选dc按照其buck值从高到低排序
        for a in offdc_sort:
            offsumb=offsumb+y*dc_b[a[0]]#计算bid值的总和
            if offsumb<B:#如果没有超过预算，就可以雇佣
                offdc_re.append(a)
                offsum_mdc=offsum_mdc+dict_mdc[a[0]]
            else:#否则 停止招聘
                break
        #再进行在线招聘
        datanum=len(data)#总候选人数
        n=0#观察人数
        for a in data:
            if n==datanum//2.7:#如果观察人数够了 就停止观察
                break
            dc_ob.append(a)#加入观察集
            n=n+1#观察集人数加一
        del data[0:n]#删除已经被观察的元素 不再参与招聘  
        dc_obsort=sorted(dc_ob,key=lambda x:x[1],reverse=True)#将候选dc按照其buck值从高到低排序 
        for a in dc_obsort:
            sumb=sumb+y*dc_b[a[0]]#计算bid值的总和
            if sumb<B:#如果没有超过预算，就可以作为采样集
                dc_sam.append(a)
                dcnum=dcnum+1
            else:#否则 停止采样
                break
        temp=[]
        for a in data:#开始在线招聘
        #确定各种阈值
            if renum==dcnum:#当实际招聘人数等于预估招聘人数时，招聘停止
                break
            if bp_sum>=B:#如果基础工资大于B，招聘停止
                break
            mbuck=10200#初始化buck阈值
            mdc='x'#初始化dc
            mb=0#初始化竞价阈值
            dc_samsort=sorted(dc_sam,key=lambda x:x[1],reverse=True)#将采样集按照buck值从高到低排序
            dc_sam=dc_samsort
            mbuck=dc_sam[len(dc_sam)-1][1]#最小的buck值即为阈值
            mdc=dc_sam[len(dc_sam)-1][0]#这个人的id就是mdc
            mb=dc_b[mdc]#这个人的bid就是mb
        #开始招聘
            if a[1]>mbuck:#如果新来一个dc的buck值大于阈值
                dc_sam.pop()#踢出去mdc
                dc_sam.append(a)#再把这个人放进采样集
                if dc_b[a[0]]<mb:#如果这个人的竞价还能小于mb，就可以招聘了
                    a[2]=dict_mdc[a[0]]/mbuck#把a[2]覆盖为基础工资
                    dc_re.append(a)#招聘
                    sum_mdc=sum_mdc+dict_mdc[a[0]]
                    renum=renum+1#招聘人数加一
                    bp_sum=bp_sum+a[2]
        for a in dc_re:#初始化所有sp值
            temp.append(float(a[5]))
        for a in offdc_re:#初始化所有sp值
            offtemp.append(float(a[5]))
        offtemp_std=np.std(offtemp,ddof=1)#求出所有dc感知数据的标准差
        temp_std=np.std(temp,ddof=1)#求出所有dc感知数据的标准差
        for a in dc_re:
            avesum=avesum+float(a[5])
        avesum=avesum/len(dc_re)
        print(avesum)
        #在线数据的真值发现过程
        dis=100
        ctd=0
        td=0
        i=0
        while dis>0.001:#开始真值发现过程，直到两次真值的距离小于0.001
            #初始化参数
            i=i+1
            utd=0
            sum_m=0
            sum_w=0
            dissum=0
            td=ctd#上一轮计算出的真值作为td
            for a in dc_re:#truth update过程
                if i==1:#如果是第一轮真值发现，那就用dc的mpv
                    sum_m=sum_m+float(dict_mdc[a[0]]) #计算dc的mpv的和作为分母
                    utd=utd+float(dict_mdc[a[0]])*float(a[5])#计算加权数据的和
                    ctd=utd/sum_m#计算本轮真值
                else:#否则，就用dc的weight
                    sum_w=sum_w+float(dict_w[a[0]])
                    utd=utd+float(dict_w[a[0]])*float(a[5])
                    ctd=utd/sum_w
            dis=abs(ctd-td)#计算前后两次真值的距离，随后确定第i轮是否收敛
            for a in dc_re:#weight update过程
                dict_d[a[0]]=math.pow((float(a[5])-float(ctd)),2)/temp_std
                dissum=dissum+dict_d[a[0]]
            for a in dc_re:
                dict_w[a[0]]=math.log(dissum/dict_d[a[0]])
        dc_ap=[]
        print(ctd)
        j=j+1
    date=date+1
