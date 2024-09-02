import numpy as np
import time
import os
import random
from gtts import gTTS

def make_audio(path, data, user_name):
    path = path[: len(path) - 4]
    if not os.path.isdir(path):
        os.mkdir(path)
    for x in data:
        language = "en"
        text = x[1]
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save("data/" + user_name + "/" + text + ".mp3")
def select_problem(path: str) -> list:
    data = np.loadtxt(path, dtype="str", delimiter="\t", encoding="utf-8")
    data = data.tolist()
    for i in range(len(data)):
        data[i][0] = int(data[i][0])
    return data
def generate_problems(data: list, number_of_problems: int) -> list:
    l = list()
    print(data)
    already_learnt = 0
    for i in range(len(data)):
        l.append([int(data[i][0]), str(data[i][1]), str(data[i][2]), i])
        # print(int(data[i][0]), str(data[i][1]), str(data[i][2]), i)
        if l[i][0] >= 2:
            already_learnt += 1
    miss = dict()
    # print(f"習得率は{(already_learnt * 100) / len(data)}%です．")
    # print(f"10問以上{len(l)}問以下出題できます．出題数を入力してください．")
    l.sort()
    use = []
    i = 0
    print(l)
    while len(use) <= number_of_problems:
        print(i)
        if l[i][0] <= 1:
            use.append(l[i])
            i += 1
        else:
            cnd = l[i:]
            random.shuffle(cnd)
            for ii in range(number_of_problems - len(use)):
                use.append(cnd[ii])
    random.shuffle(use)
    return [use, already_learnt]
def manage_problems(data: list, use: list, number_of_problems: int) -> list:
    correct = 0
    asked = 0
    # print(number_of_problems)
    for i in range(number_of_problems):
        correct_ans_and_problem = submit_question(i, use)
        # print(use[i][1])
        # print(correct_ans_and_problem[0])
        correct_ans = correct_ans_and_problem[1]
        ask = correct_ans_and_problem[2]
        asked += 1
        # ans_given = int(input())
        ans_given = correct_ans # あとで消す
        bl = receive_answer(data, ask, i, use, ans_given, correct_ans, asked, correct)
        if bl: correct += 1
    print(f"{asked}問中{correct}問正解で正答率は{(correct * 100) / asked}%でした．")
    return data
def submit_question(i: int, use: list) -> list:
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
    return [stm, ans, ask]
def receive_answer(data: list, ask: dict, i: int, use: list, ans_given: int, correct_ans: int, asked: int, correct: int) -> bool:
    if correct_ans == ans_given:
        print("正解！")
        print(f"{asked}問中{correct + 1}問正解！")
        data[use[i][3]][0] += 1
        return True
    else:
        print("不正解！")
        print(f"{asked}問中{correct}問正解！")
        print(f"{use[i][1]}: {ask[correct_ans]}")
        data[use[i][3]][0] = 0
        return False
def ending_test(path: str, data: list, already_learnt: int) -> bool:
    data.sort()
    shu = 0
    ich = 0
    with open(path, mode = 'w', encoding = "utf-8") as f:
        wr = ""
        for i in range(len(data)):
            if data[i][0] >= 2:
                shu += 1
            if data[i][0] == 1:
                ich += 1
            wr += str(data[i][0]) + "\t" + data[i][1] + "\t" + data[i][2] + "\n"
        f.write(wr)
    f.close()
    ret = f"全てで{len(data)}単語のうち，習得: {shu}単語, 点検中: {ich}単語です．\n新たに{shu - already_learnt}単語習得しました．\n習得率は{(shu * 100) / len(data)}%です．"
    return ret
# def make_audio(path, data):
#     path = path[: len(path) - 4]
#     if not os.path.isdir(path):
#         os.mkdir(path)
#     for x in data:
#         language = "en"
#         text = x[1]
#         tts = gTTS(text=text, lang=language, slow=False)
#         tts.save("data/" + user_name + "/" + text + ".mp3")
def main():
    # name_of_test = input("1-7の中でどれをやりたいですか？\n")
    name_of_test = "1"
    data = select_problem(name_of_test = "1")
    # number_of_problems = int(input(f"10問以上{len(data)}問以下出題できます．出題数を入力してください．"))
    number_of_problems = 10
    use_and_already_learnt = generate_problems(data, number_of_problems)
    use = use_and_already_learnt[0]
    already_learnt = use_and_already_learnt[1]
    data = manage_problems(data, use, number_of_problems)
    path = "./data/words/" + name_of_test + ".csv"
    ending_test(path, data, already_learnt)
if __name__ == "__main__":
    main()