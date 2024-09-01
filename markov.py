from glob import iglob
import re
import MeCab
import markovify
import statistics
from scipy.stats import norm
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import make_interp_spline
from matplotlib import cm
from scipy import optimize
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
# data1 = np.loadtxt("../../data/exp3/data-1.csv", dtype = "str", delimiter = "\t")
# data1 = data1.T
# data = data1[2]
mecab = MeCab.Tagger('-r /etc/mecabrc -d /var/lib/mecab/dic/ipadic-utf8')
def load_from_file(files_pattern):
    text = ""  # ここで初期化
    for path in iglob(files_pattern):
        with open(path, 'r', encoding='utf-8') as f:
            text += f.read().strip()
    unwanted_chars = ['\r', '\u3000', '-', '｜']
    for uc in unwanted_chars:
        text = text.replace(uc, '')
    unwanted_patterns = [re.compile(r'《.*》'), re.compile(r'［＃.*］')]
    for up in unwanted_patterns:
        text = re.sub(up, '', text)
    return text
def split_for_markovify(text):
    splitted_text = ""
    breaking_chars = ['(', ')', '[', ']', '"', "'"]
    for line in text.split():
        mp = mecab.parseToNode(line)
        while mp:
            try:
                if mp.surface not in breaking_chars:
                    splitted_text += mp.surface  # skip if node is markovify breaking char
                if mp.surface != '。' and mp.surface != '、':
                    splitted_text += ' '  # split words by space
                if mp.surface == '。':
                    splitted_text += '\n'  # represent sentence by newline
                if mp.surface == '．':
                    splitted_text += '\n'  # represent sentence by newline
            except UnicodeDecodeError as e:
                # sometimes error occurs
                print(line)
                # pass
            finally:
                mp = mp.next
    return splitted_text
def reply():
    while True:
        rampo_text = load_from_file('*.txt')
        splitted_text = split_for_markovify(rampo_text)
        text_model = markovify.NewlineText(splitted_text, state_size=3)
        sentence = text_model.make_sentence()
        try:
            # with open('learned_data.json', 'w') as f:
                # f.write(text_model.to_json())
            return str(''.join(sentence.split()))
        except: 
            pass
# if __name__ == '__main__':
#     main()
