import discord
import word_test
from discord import app_commands
from dotenv import load_dotenv
import os
import io
import csv
import shutil

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
class UserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = []
        self.number_of_problems = 0
        self.use = []
        self.asked = 0
        self.correct = 0
        self.ask = []
        self.correct_ans = 0
        self.path = ""
        self.already_learnt = []
        self.used_buttons = set()
    def reset(self):
        self.data = []
        self.number_of_problems = 0
        self.use = []
        self.asked = 0
        self.correct = 0
        self.ask = []
        self.correct_ans = 0
        self.path = ""
        self.already_learnt = []
        self.used_buttons = set()
    def select_problem(self, problem_type):
        self.data = list()
        self.asked = self.correct = 0
        self.path = "./data/" + str(self.user_id) + "/" + problem_type
        self.data = word_test.select_problem(self.path)
        return self.data
    def generate_problems(self, number_of_problems):
        self.number_of_problems = number_of_problems
        use_and_already_learnt = word_test.generate_problems(self.data, self.number_of_problems)
        self.use = use_and_already_learnt[0]
        self.already_learnt = use_and_already_learnt[1]
    def update_correct_answer(self):
        self.correct += 1
        self.data[self.use[self.asked][3]][0] += 1
        self.asked += 1
    def update_wrong_answer(self):
        self.data[self.use[self.asked][3]][0] = 0
        self.asked += 1
    def prepare_question(self):
        correct_ans_and_problem = word_test.submit_question(self.asked, self.use)
        self.correct_ans = correct_ans_and_problem[1]
        self.ask = correct_ans_and_problem[2]
        return self.use[self.asked][1], self.ask
    def get_score(self):
        return f"{self.asked}問中{self.correct}問正解！"
    def end_test(self):
        statement = word_test.ending_test(self.path, self.data, self.already_learnt)
        return statement

user_data_dict = {}
@bot.event
async def on_ready() -> None:
    await tree.sync()
    print("Successfully logged in")
    await bot.change_presence(activity=discord.Game("Python"))

@bot.event
async def on_interaction(inter: discord.Interaction) -> None:
    try:
        if (inter.data['component_type'] == 2):
            await on_button_click(inter)
    except KeyError:
        pass

async def on_button_click(inter: discord.Interaction) -> None:
    user_id = inter.user.id
    if (user_id not in user_data_dict):
        user_data_dict[user_id] = UserData(inter.user.name)
    user_info = user_data_dict[user_id]
    returned_ans = inter.data["custom_id"]
    if (returned_ans.startswith("problm")):
        problem_type = returned_ans[6:]
        user_info.select_problem(problem_type)
        await select_number(inter)
    elif (returned_ans.startswith("number")):
        number_of_problems = int(returned_ans[6:])
        user_info.generate_problems(number_of_problems)
        await manage_flow(inter, user_info)
    elif (returned_ans.startswith("ans")):
        if (returned_ans.startswith("anscrr")):
            user_info.update_correct_answer()
            embed = discord.Embed(
                title = "正解",
                color = discord.Colour.blue(),
                description = user_info.get_score()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        elif (returned_ans.startswith("answng")):
            user_info.update_wrong_answer()
            embed = discord.Embed(
                title = "不正解",
                color = discord.Colour.red(),
                description = f"{user_info.get_score()}\n {user_info.use[user_info.asked - 1][1]}: {user_info.ask[user_info.correct_ans]}"
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        await manage_flow(inter, user_info)

async def manage_flow(inter: discord.Interaction, user_info: UserData) -> None:
    if (user_info.asked < user_info.number_of_problems):
        question_title, ask = user_info.prepare_question()
        embed = discord.Embed(
            title="\n" + question_title,
            color=discord.Colour.green(),
        )
        for j in range(1, 10):
            embed.add_field(name=str(j), value=ask[j])
        if (not inter.response.is_done()):
            await inter.response.send_message(embed=embed, ephemeral=True)
        else:
            await inter.followup.send(embed=embed, ephemeral=True)
        audio_source = user_info.path[:-4] + "/" + question_title + ".mp3"
        await play(inter, audio_source)
        await make_options(inter=inter, ask=ask, correct_ans=user_info.correct_ans)
    else:
        await terminate_test(inter=inter, user_info=user_info)

async def make_options(inter: discord.Interaction, ask, correct_ans) -> None:
    view = discord.ui.View()
    for i in range(1, 10):
        button = discord.ui.Button(
            label=str(i),
            style=discord.ButtonStyle.green, 
            custom_id="anscrr" + str(i) if i == correct_ans else "answng" + str(i),
            disabled=False
        )
        view.add_item(button)
    await inter.followup.send("答えを1つ選んでください．", view=view, ephemeral=True)

async def select_number(inter: discord.Interaction) -> None:
    view = discord.ui.View()
    number_candicates = [10, 30, 50, 100]
    for i in range(4):
        button = discord.ui.Button(
            label=str(number_candicates[i]), 
            style=discord.ButtonStyle.green, 
            custom_id="number" + str(number_candicates[i]),
            disabled=False
        )
        view.add_item(button)
    await inter.response.send_message("問題数を選んでください．", view=view, ephemeral=True)

async def terminate_test(inter: discord.Interaction, user_info: UserData) -> None:
    statement = user_info.end_test()
    embed = discord.Embed(
        title="テスト終了",
        color=discord.Colour.green(),
        description=statement,
    )
    await inter.followup.send(embed=embed)
    await leave(inter)

@tree.command(name="test", description="単語テストを開始．")
async def select_problem(inter: discord.Interaction) -> None:
    view = discord.ui.View()
    joined = await join(inter)
    if (not joined):
        return
    dir_path = "data/" + str(inter.user.name)
    file_candidates = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    for x in file_candidates:
        x_non_ext = os.path.splitext(x)[0]
        button = discord.ui.Button(label=x_non_ext, style=discord.ButtonStyle.green, custom_id="problm" + str(x))
        view.add_item(button)
    await inter.response.send_message("テストの種類を選んでください．", view=view)

@tree.command(name="register", description="利用を開始します．")
async def register(inter: discord.Interaction) -> None:
    if not os.path.isdir("data/" + str(inter.user.name)):
        os.mkdir("data/" + str(inter.user.name))
    await inter.response.send_message("登録中です．", ephemeral=True)
    if not str(inter.user.name) == "harry_arbrebleu":
        shutil.copy("data/harry_arbrebleu/アラビア語1.csv", "data/" + str(inter.user.name))
        shutil.copy("data/harry_arbrebleu/フランス語1.csv", "data/" + str(inter.user.name))
        shutil.copy("data/harry_arbrebleu/英語1.csv", "data/" + str(inter.user.name))
    path1 = "data/" + str(inter.user.name) + "/アラビア語1.csv"
    path2 = "data/" + str(inter.user.name) + "/フランス語1.csv"
    path3 = "data/" + str(inter.user.name) + "/英語1.csv"
    word_test.make_audio(path1, "ar")
    word_test.make_audio(path2, "fr")
    word_test.make_audio(path3, "en-uk")
    await inter.followup.send("登録完了しました。")

@tree.command(name="add_file", description="英語: en-uk, フランス語: fr, アラビア語: ar")
@app_commands.describe(new_file="ここにファイルをアップロード．")
async def add_via_file(inter: discord.Interaction, new_file: discord.Attachment, lang_in: str) -> None:
    csv_data = await new_file.read()
    csv_text = csv_data.decode()
    new_words = list(csv.reader(io.StringIO(csv_text), delimiter=','))
    if (not os.path.isdir("data/" + str(inter.user.name))):
        os.mkdir("data/" + str(inter.user.name))
    i = 1
    lang_dict = {"en": "英語", "fr": "フランス語", "ar": "アラビア語"}
    if (lang_in not in lang_dict):
        await inter.response.send_message("言語を入力してやり直してください", ephemeral=True)
        return
    lang = lang_dict[lang_in]
    while True:
        csv_path = "data/" + str(object=inter.user.name) + "/" + lang + str(object=i) + ".csv"
        if (not os.path.isfile(csv_path)):
            os.mkdir("data/" + str(object=inter.user.name) + "/" + lang + str(object=i))
            with open(csv_path, mode="a+", encoding="utf-8") as f:
                wrt = str()
                for i in range(len(new_words)):
                    wrt += "0," + new_words[i][1] + "," + new_words[i][2] + "\n"
                f.write(wrt)
                f.close()
            await inter.response.send_message("新規単語の登録が完了しました．", ephemeral=True)
            word_test.make_audio(csv_data_path=csv_path, language=lang_in)
            return
        else:
            i += 1

@tree.command(name="add_word",description="新しい単語1つずつを追加します．")
async def add_via_text(inter: discord.Interaction, foreign_lang: str, japanese: str, destination: str) -> None:
    if not os.path.isdir("data/" + str(inter.user.name)):
        os.mkdir("data/" + str(inter.user.name))
    with open("data/" + str(inter.user.name) + "/" + destination + ".csv", mode="a+", encoding="utf-8") as f:
        wrt = str()
        wrt += "0," + foreign_lang + "," + japanese + "\n"
        f.write(wrt)
        f.close()
    await inter.response.send_message("新規単語の登録が完了しました．", ephemeral=True)

@tree.command(name="help", description="このbotの使い方を説明します．")
async def help(inter: discord.Interaction):
    embed = discord.Embed(title="使いかた", description="このbotの使い方を説明します．このbotは単語テストを実施するものです．間違えた単語が優先して出題されます．単語の追加もできます．デフォルトで英語とフランス語とアラビア語の単語が入っています．", color=0xffff00)
    embed.set_author(name="Words_master", url="https://github.com/harry-arbrebleu/words_learning")
    embed.add_field(name="/register", value="botの利用を開始します．", inline= False)
    embed.add_field(name="/test", value="単語テストを実施します．問題種別，問題数を選択できます．", inline= False)
    embed.add_field(name="/new_file", value="[ファイル][ファイルの保存名]\n新たに単語をまとめて追加できます．追加できるファイルはtab区切りのcsvファイルのみです．1列目には学習している外国語，2列目にはその訳を付けてください．\n(例)\n aller, 行く\n venir,行く\n", inline= False)
    embed.add_field(name="/new_word", value="[外国語][訳][ファイルの保存名]\n1単語ずつ追加します．", inline= False)
    embed.add_field(name="/help", value="このメッセージを表示します．", inline= False)
    embed.set_footer(text="タイトルのリンクからこのbotのGitHubページに飛べます．興味があれば覗いてみてください．")
    await inter.response.send_message(embed=embed, ephemeral=True)

async def join(inter: discord.Interaction) -> bool:
    if (inter.user.voice):
        channel = inter.user.voice.channel
        await channel.connect()
        return True
    else:
        await inter.response.send_message(content="ボイスチャンネルに接続していません．")
        return False

async def leave(inter: discord.Interaction) -> None:
    await inter.guild.voice_client.disconnect()

async def play(inter: discord.Interaction, dir: str) -> None: 
    if (inter.guild.voice_client is None):
        await inter.response.send_message(content="ボイスチャンネルに接続してください．")
        return
    audio_source = discord.FFmpegPCMAudio(dir)
    inter.guild.voice_client.play(audio_source)

bot.run(TOKEN)