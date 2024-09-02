import os
import numpy as np
from gtts import gTTS

def make_audio(path, data, user_name):
    # path = path[: len(path) - 4]
    if not os.path.isdir(path):
        os.mkdir(path)
    for x in data:
        language = "en"
        text = x[1]
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(path+ "/" + text + ".mp3")
def select_problem(path: str) -> list:
    data = np.loadtxt(path, dtype="str", delimiter="\t", encoding="utf-8")
    data = data.tolist()
    for i in range(len(data)):
        data[i][0] = int(data[i][0])
    return data
path = "data/harry_arbrebleu/test"
data = select_problem(path + ".csv")
user_name = "harry_arbrebleu"
make_audio(path, data, user_name)