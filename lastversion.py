import math

class node():
    '''
    节点类型
    '''
    step=0
    def __init__(self,array,f,d):
        array=str(array)
        self.origin=array
        self.grids=[list(array[:3]),list(array[3:6]),list(array[6:])]
        self.number = node.step
        self.depth=d
        if f!=None:
            self.father=[f,f.find_space()]
        else:
            self.father=[f,None]
        node.step+=1
    def ef(self,target,function_choice):   #estimate_funciton
        '''
        评价函数1: g=节点深度，h=不同的将牌个数
        :param target: 目标状态
        评价函数2： g=节点深度 h=p+3*s
    #     p=每个牌离目标位置最短距离之和

        '''
        if function_choice==1:
            h = 8
            array = list(self.origin)
            target = list(str(target))
            for i in range(9):
                if array[i] == target[i] and array[i] != '0':
                    h -= 1
            f = self.depth + h

        else:
            p = 0
            W=3
            array = list(self.origin)
            target = list(str(target))
            for i in range(1,9):
                i = str(i)
                s0 = target.index(i)
                s = array.index(i)
                dis = abs(s0 - s) // 3 + abs(s0 - s) % 3
                p += dis

            h=0
            for i in range(1,9):
                i = str(i)
                s0 = target.index(i)
                s = array.index(i)
                if s==4:
                    h+=1
                elif array[find_next(s)]==target[find_next(s0)]:
                    h+=0
                else:
                    h+=2
            f = p + W*h
        return f
    def init_number(self):
        node.step=1
        self.number=0

    def find_space(self):
        array=list(self.origin)
        return array.index('0')
    def show(self):
        print(self.origin[:3])
        print(self.origin[3:6])
        print(self.origin[6:])
    def expand(self):
        expansion=[]
        dict_move = {0: [1, 3], 1: [0, 2, 4], 2: [1, 5], 3: [0, 4, 6],
                     4: [1, 3, 5, 7], 5: [2, 4, 8], 6: [3, 7], 7: [4, 6, 8], 8: [5, 7]}
        space=self.find_space()
        move_list = dict_move[space]
        # print(move_list)
        if self.father[1]!=None:
            # print(self.father[1])
            move_list.remove(self.father[1])
        for i in move_list:
            array=list(self.origin)
            # print('yes')
            # print(array)
            array[i],array[space]=array[space],array[i]
            result = ''.join(array)
            # print(result)
            new=node(result,self,self.depth+1)
            expansion.append(new)
        return expansion

def find_next(num):
    if num==0 or num==1:
        return num+1
    elif num==2 or num==5:
        return num+3
    elif num==8 or num==7:
        return num-1
    elif num==3 or num==6:
        return num-3
    else:
        return num


def estimate(origin,destination):
    #若两个状态的逆序奇偶性相同，则可相互到达，否则不可相互到达。
    lis=list(str(i) for i in range(9))
    origin=list(str(origin))
    destination=list(str(destination))
    for i in origin:
        if i not in lis:
            print(i)
            return True
    ori = 0
    dest = 0
    for i in range(1, 9):
        fist = 0
        for j in range(0, i):
            if origin[j] > origin[i] and origin[i] != '0':
                fist = fist + 1
        ori = ori + fist
    for i in range(1, 9):
        fist = 0
        for j in range(0, i):
            if destination[j] > destination[i] and destination[i] != '0':
                fist = fist + 1
        dest = dest + fist
    if (ori % 2) != (dest % 2) or len(origin)!=9:  # 一个奇数一个偶数，不可达
        return True
    else:
        print('目标可达')
        return False

def open_rank(open,target,f):
    open.sort(key=lambda x:x.ef(target,f))
    return open

def bfs(start,target,f):
    '''

    :param start: 起始情形 一列数
    :param target: 目标状态
    :return: 若有解，返回过程，若无解，返回None
    '''
    if estimate(start,target)==True:
        print('目标布局不可达')
        return None,None,0,0

    s0=node(start,None,0)
    s0.init_number()
    opens=[s0]
    closeds=[]
    results=[]
    T=0
    L=-1
    while len(opens)!=0:
        process=[]
        opens=open_rank(opens,target,f)
        N=opens[0]
        opens.remove(N)
        closeds.append(N)
        o= []
        cl= []
        for j in opens:
            o.append(j.number)
        for j in closeds:
            cl.append(j.number)
        process.append(o)
        process.append(cl)
        process.append(N)
        process.append(N.father[0])


        if N.origin==str(target):
            Optional=[]
            a=N
            while a!=None:
                L+=1
                Optional.append(a)
                a=a.father[0]
            Optional=list(reversed(Optional))
            process.append([])
            results.append(process)
            return results,Optional,L,T
        else:
            expansions=N.expand()
            develops = []
            if len(expansions)!=0:
                for i in expansions:
                    opens.append(i)
                    T+=1
                    develops.append(i)
                process.append(develops)
            results.append(process)
            # print(process)2


    if len(opens)==0:
        return None,None,0,0


def main(start, target, f):
    re,op,L,T=bfs(start,target,f)
    if op==None:
        return False
    results=[]
    for time in range(len(re)):
        i=re[time]
        process=[]
        process.append(i[0])
        process.append(i[1])
        now=i[2]
        process.append([i[2].origin,i[2].number,i[2].ef(target,f)])
        if time>0:
            process.append([i[3].origin, i[3].number, i[3].ef(target,f)])
        else:
            process.append([None])
        develop=[]
        for v in i[4]:
            node=[v.origin,v.number,v.ef(target,f)]
            develop.append(node)
        process.append(develop)
        brothers=[]
        if time>0:
            for j in re[time-1][4]:
                if j!=now:
                    node = [j.origin, j.number, j.ef(target,f)]
                    brothers.append(node)
        process.append(brothers)
        results.append(process)
    # print(results)
    return [L / T, results]
