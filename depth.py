dict_move={0:[1,3],1:[0,2,4],2:[1,5],3:[0,4,6],
           4:[1,3,5,7],5:[2,4,8],6:[3,7],7:[4,6,8],8:[5,7]}

def swap(list,i,j):
    """
    在九宫中交换i和j的位置
    """
    if i>j:
        i,j=j,i
    list1=list[:i]+list[j]+list[i+1:j]+list[i]+list[j+1:]
    return list1

def process(origin,destination, dm=10):
    """
    origin是初始状态，destination是目标状态
    求解过程
    """
    # 判断初始状态是否可以到达目标状态
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
    if (ori % 2) != (dest % 2):  # 一个奇数一个偶数，不可达
        return None

    #深度搜索
    result=[]
    dict_process={}
    dict_process[origin]=-1
    number=0
    node_now=[origin,number,0]
    open=[]
    close=[]
    open.append(node_now)

    while(len(open)>0):
        open_number=[]
        close_number=[]
        son_node=[]
        brother_node=[]
        father_node=None
        current=open.pop()
        close.append(current)
        for node in open:
            open_number.append(node[1])
        for node in close:
            close_number.append(node[1])
        father=dict_process[current[0]]
        for node in close:
            if father==node[0]:
                father_node=node
        brother=[k for k, v in dict_process.items() if v == father]
        brother.remove(current[0])
        for value in brother:
            for node in open:
                if value==node[0]:
                    brother_node.append(node)
            for node in close:
                if value==node[0]:
                    brother_node.append(node)
        if current[0]==destination:
            break
        if current[2]<dm:
            zero=current[0].index("0")  #0所在的位置
            shift=dict_move[zero]    #找出可以移动的位置
            for i in shift:
                new=[swap(current[0],i,zero),number+1,current[2]+1]
                number=number+1
                if dict_process.get(new[0])==None:    #判断新得到的状态是否出现过，若没有，则添加入open表中
                    dict_process[new[0]]=current[0]
                    open.append(new)
                    son_node.append(new)
        else:
            son_node.append('None')
        result.append([open_number, close_number, current, father_node, son_node, brother_node])
    result.append([open_number, close_number, current, father_node, son_node, brother_node])
    return result
