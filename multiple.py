import multiprocessing as mp
import threading as td

# 多线程执行函数
# ts: 将大任务分配给线程数
# taskSize: 任务大小，一个整数
# job: 每个线程要执行的任务
def thds(ts, taskSize, job):
    threads = []
    step = int(taskSize / ts)
    for i in range(ts):
        t = td.Thread(target=job, args=(i*step, (i+1)*step))
        t.start()
        threads.append(t)
    
    for th in threads:
        th.join()
        
# 多进程执行函数，参数：
# processes：将大任务分配给进程数
# job：每个进程要执行的任务
# taskSize：任务大小，一个整数

def mtpcs(processes, taskSize, job):
    pcs = []
    step = int(taskSize / processes)
    q = mp.Queue()
    #计数器
    cnt = mp.Value('i', 0)
    res = []
    for i in range(processes):
        a = i*step
        b = (i+1)*step
        if b > taskSize:
            b = taskSize
        p = mp.Process(target=job, args=(q, cnt, a, b))
        pcs.append(p)
        
    for item in pcs:
        item.start()
    
    for item in pcs:
        item.join(3)
    
    for _ in range(processes):
        arr = q.get()
        for j in range(len(arr)):
            res.append(arr[j])
    return res
    
# 测试用例
def Job(q, a, b):
    arr = []
    for i in range(a, b):
        arr.append(i)
    
    q.put(arr)
    

if __name__ == '__main__':
    res = mtpcs(2,20,Job)
    print(res)