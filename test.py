import numpy as np
import time
import os
import random
path = "words1.txt"
tp = input("1-3の中でどれをやりたいですか？\n")
path = "words" + tp + ".txt"
data = np.loadtxt(path, dtype = "str", delimiter = "\t", encoding = "utf-16")
l = list()
alr = 0
for i in range(len(data)):
    l.append([int(data[i][0]), str(data[i][1]), str(data[i][2]), i])
    if l[i][0] >= 2:
        alr += 1
miss = dict()
print(f"習得率は{(alr * 100) / len(l)}%です．")
print(f"10問以上{len(l)}問以下出題できます．出題数を入力してください．")
a = int(input())
l.sort()
use = []
i = 0
while len(use) < a:
    if l[i][0] <= 1:
        use.append(l[i])
        i += 1
    else:
        re = a - len(use)
        cnd = l[i:]
        random.shuffle(cnd)
        for ii in range(re):
            use.append(cnd[ii])
random.shuffle(use)
crr = 0
shutsudai = 1
for i in range(a):
    tmp = set()
    tmp.add(use[i][2])
    while len(tmp) != 8:
        t = random.randint(0, len(use) - 1)
        tmp.add(use[t][2])
    tmp = list(tmp)
    ask = dict()
    ans = -1
    ask[9] = "わからない"
    stm = ""
    cnt = 1
    random.shuffle(tmp)
    for j in range(8):
        ask[j + 1] = tmp[j]
        if tmp[j] == use[i][2]:
            ans = j + 1
        stm += f"{cnt}: {tmp[j]}"
        stm += "\t\t"
        if cnt % 3 == 0:
            stm += "\n"
        cnt += 1
    stm += f"9: {ask[9]}"
    # print(ans)
    print("以下の選択肢から選んで解答してください．")
    print(f"{shutsudai}: {use[i][1]} ")
    print(stm)
    k = int(input())
    if k == ans:
        crr += 1
        print("正解！")
        print(f"{a}問中{crr}問正解！")
        l[use[i][3]][0] += 1
    else:
        print("不正解！")
        print(f"{a}問中{crr}問正解！")
        print(f"{use[i][1]}: {ask[ans]}")
        miss[l[use[i][3]][1]] = ask[ans]
        l[use[i][3]][0] = 0
    # time.sleep(0.2)
    shutsudai += 1
    print()
    print()
print(f"{a}問中{crr}問正解で正答率は{(crr * 100) / a}%でした．")
os.remove(path)
f = open(path, 'w')
shu = 0
ich = 0
l.sort()
with open(path, mode = 'w', encoding = "utf-16") as f:
    wr = ""
    for i in range(len(l)):
        if l[i][0] >= 2:
            shu += 1
        if l[i][0] == 1:
            ich += 1
        wr += str(l[i][0]) + "\t" + l[i][1] + "\t" + l[i][2] + "\n"
    f.write(wr)
print(f"全てで{len(l)}単語のうち，修得: {shu}単語, 点検中: {ich}単語です．")
print(f"新たに{shu - alr}単語修得しました．")
print(f"習得率は{(shu * 100) / len(l)}%です．")
f.close()
