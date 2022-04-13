from datetime import *
from abc import ABC , abstractmethod
from operator import attrgetter
from functools import cached_property
from functools import cache

filename = 'test.in'

Tday = date.today()
predictspendday = 0
danwei = {'青菜':'斤', '土豆':'个', '生菜':'颗'}
#Ver
# ptype = {'绿叶菜':['青菜', '生菜'], '其他蔬菜':['土豆'], '肉类':['鸡','鸭','鱼',''], '点心':[]}

with open(filename) as file:
    lines = file.readlines()

_no_default = object()

class Validator(ABC):
    @abstractmethod
    def __init__(self , default = _no_default):
        self.default = _no_default

    def __set_name__(self , owner , name):
        self.private_name = f'_{name}'
        self.public_name = name

    def __set__(self , obj ,value):
        self.validate(value)
        setattr(obj , self.private_name ,value)

    def __get__(self , obj , objtype = None):
        return getattr(obj , self.private_name)

    @abstractmethod
    def validate(self , value):
        pass

class Strof(Validator):
    def __init__(self):
        super().__init__()

    def validate(self , value):
        if not isinstance(value , str):
            raise f'{value} 不是名称'


class Dateof(Validator):
    def __init__(self):
        super().__init__()

    def validate(self , value):
        if not isinstance(value , type(Tday)):
            raise f'{value} 不是日期'


class Intof(Validator):
    def __init__(self):
        super().__init__()

    def validate(self , value):
        if not isinstance(value , int) and not isinstance(value , float):
            raise f'{value} 不是数字'

class Product:
    name = Strof()
    currentweight = Intof()
    leftdate = Intof()
    startdate = Dateof()
    costday = Intof()
    producttype = Strof()
    saveday = Intof()

    def __init__(self , name , currentweight, startdate, saveday, ptype, cost):
        self.name = name    #名称
        self.currentweight = currentweight  #总重量
        self.startdate = date(int(startdate[0]), int(startdate[1]), int(startdate[2]))  #开始储存的日期
        self.saveday = saveday  #保质期,包括当天，无论当天何时记录数据
        self.leftdate =self.saveday - (Tday - self.startdate ).days    #剩余天数,保质期天数减去度过的天数
        self.costday = cost/2   #可以吃的天数
        # if self.costday < 0.5:
        #     self.costday = 0.5
        self.producttype = ptype    #食物类型
        self.min = self.mincost     #可用的最短天数

    @cached_property
    def mincost(self):
        if self.costday < self.leftdate:
            return self.costday
        else:
            return self.leftdate
    

###Ver1.0
    # def __str__(self):
    #     return '\t'.join((f'{self.name}    剩余数量：{self.currentweight}斤   保质期： {self.leftdate}天',  f'预期能吃{self.costday}天' if self.costday > 0 else f'{self.name}坏了'))
###Ver2.0
    def __str__(self):
        return '\t'.join((f'{self.name} \t还能吃{self.min}天\t',f'距离坏了还有{int(self.leftdate)}天' if self.leftdate > 0 else f'{self.name}坏了'))

ProductList = []
totalday = 0 #度过的天数
mindate = date.max

product = None
for line in lines:
    product = line.split()
    if product[0] == '名称':
        continue
    if len(product) > 4:
        p = Product(product[0] , float(product[1][: -1]) , product[2].split('.'), float(product[3][: -1 ]) , product[4], int(product[5]))
        if mindate > p.startdate and p.leftdate > 0 and p.costday > 0:
            mindate = p.startdate
        ProductList.append(p)
    else:
        raise f'{product}无效数据'
# totalday = totalday - (Tday - mindate).days
for sd in sorted(ProductList,key = attrgetter('saveday','leftdate') ):
    if (sd.leftdate - totalday) > 0:    #判断剩余可用的天数大于度过的天数，说明这东西还能用
        if sd.saveday - totalday  > sd.min: #判断可用的情况下，该物品的保质期和可用天数哪个多一点（预测天数增加，保质期天数会缩短甚至小于可消耗的天数）
            totalday = totalday + sd.min
        else:
            totalday = sd.leftdate
            print(f'{sd.name}会浪费一些')
        # print(sd.name , sd.costday , sd.min ,totalday)
    else:
        print(f'{sd.name}会坏，{sd.min}')
    print(sd)
print(totalday)

