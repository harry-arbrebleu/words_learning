import discord
from discord.ext import commands
import requests
from pprint import pprint
import aiohttp
import word_test
from discord import app_commands, ui
from discord.ui import Select, View
from discord.app_commands import CommandTree
from dotenv import load_dotenv
import numpy as np
import time
import os
import random
from bidi.algorithm import get_display
import arabic_reshaper

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
    def select_problem(self, problem_type):
        self.data = list()
        self.asked = self.correct = 0
        self.path = "./data/" + str(self.user_id) + "/" + problem_type
        print(self.path)
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
        print(self.data[self.use[self.asked][3]])
        self.asked += 1
    def update_wrong_answer(self):
        self.data[self.use[self.asked][3]][0] = 0
        print(self.data[self.use[self.asked][3]])
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
async def on_ready():
    await tree.sync()
    print("Successfully logged in")
    await bot.change_presence(activity=discord.Game("Python"))
@bot.event
async def on_interaction(inter: discord.Interaction):
    try:
        if inter.data['component_type'] == 2:
            await on_button_click(inter)
        elif inter.data['component_type'] == 3:
            await on_dropdown(inter)
    except KeyError:
        pass
async def on_button_click(inter: discord.Interaction):
    user_id = inter.user.id
    if user_id not in user_data_dict:
        user_data_dict[user_id] = UserData(inter.user.name)
    user_info = user_data_dict[user_id]
    returned_ans = inter.data["custom_id"]
    if returned_ans.startswith("problm"):
        problem_type = returned_ans[6:]
        user_info.select_problem(problem_type)
        await select_number(inter)
    elif returned_ans.startswith("number"):
        number_of_problems = int(returned_ans[6:])
        user_info.generate_problems(number_of_problems)
        await manage_flow(inter, user_info)
    elif returned_ans.startswith("ans"):
        if returned_ans.startswith("anscrr"):
            user_info.update_correct_answer()
            embed = discord.Embed(
                title = "正解",
                color = discord.Colour.blue(),
                description = user_info.get_score()
            )
            await inter.response.send_message(embed=embed)
        elif returned_ans.startswith("answng"):
            user_info.update_wrong_answer()
            embed = discord.Embed(
                title = "不正解",
                color = discord.Colour.red(),
                description = f"{user_info.get_score()}\n {user_info.use[user_info.asked - 1][1]}: {user_info.ask[user_info.correct_ans]}"
            )
            await inter.response.send_message(embed=embed)
        await manage_flow(inter, user_info)
async def manage_flow(inter: discord.Interaction, user_info: UserData):
    if user_info.asked < user_info.number_of_problems:
        question_title, ask = user_info.prepare_question()
        embed = discord.Embed(
            title=question_title,
            color=discord.Colour.green(),
        )
        for j in range(1, 10):
            embed.add_field(name=str(j), value=ask[j])
        if not inter.response.is_done():
            await inter.response.send_message(embed=embed)
        else:
            await inter.followup.send(embed=embed)
        await make_options(inter, ask, user_info.correct_ans)
    else:
        await terminate_test(inter, user_info)
async def make_options(inter: discord.Interaction, ask, correct_ans):
    view = discord.ui.View()
    for i in range(1, 10):
        button = discord.ui.Button(
            label=str(i), 
            style=discord.ButtonStyle.green, 
            custom_id="anscrr" + str(i) if i == correct_ans else "answng" + str(i)
        )
        view.add_item(button)
    await inter.followup.send("答えを1つ選びなさい", view=view)
async def select_number(inter: discord.Interaction):
    view = discord.ui.View()
    number_candicates = [10, 30, 50, 100]
    for i in range(4):
        button = discord.ui.Button(
            label=str(number_candicates[i]), 
            style=discord.ButtonStyle.green, 
            custom_id="number" + str(number_candicates[i])
        )
        view.add_item(button)
    await inter.response.send_message("問題数を選びなさい", view=view)
async def terminate_test(inter: discord.Interaction, user_info: UserData):
    statement = user_info.end_test()
    embed = discord.Embed(
        title="テスト終了",
        color=discord.Colour.green(),
        description=statement
    )
    await inter.followup.send(embed=embed)
@tree.command(name="test", description="単語テストを作成")
async def select_problem(inter: discord.Interaction):
    view = discord.ui.View()
    file_candidates = os.listdir("data/" + str(inter.user.name))
    for x in file_candidates:
        x_non_ext = str()
        for i in range(len(x)):
            if x[i] == ".":
                x_non_ext = x[: i]
        button = discord.ui.Button(label=x_non_ext, style=discord.ButtonStyle.green, custom_id="problm" + str(x))
        view.add_item(button)
    await inter.response.send_message("テストの種類を選びなさい", view=view)
@tree.command(name="register", description="利用開始")
async def register(inter: discord.Interaction):
    if not os.path.isdir("data/" + str(inter.user.name)):
        os.mkdir("data/" + str(inter.user.name))
        await inter.response.send_message("登録完了")
    else:
        await inter.response.send_message("登録済み")

@tree.command(name="test",description="テストコマンドです")
@app_commands.describe(picture="ここに画像をアップロード")#使われている引数の名前="詳細"
async def test_command(interaction: discord.Interaction,picture:discord.Attachment):
    embed=discord.Embed(title="画像",color=0xff0000)
    embed.set_image(url=picture.url)
    await interaction.response.send_message(embed=embed)
bot.run(TOKEN)
