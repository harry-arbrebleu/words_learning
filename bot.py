import discord
from discord.ext import commands
import markov
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
    returned_ans = inter.data["custom_id"]
    global data, number_of_problems, use, asked, correct, ask, correct_ans, path, already_learnt
    if returned_ans[:6] == "problm":
        data = list()
        asked = correct = 0
        problem_type = returned_ans[6:]
        path =  "./data/" + str(inter.user.name) + "/" + problem_type + ".csv"
        print(path)
        data = word_test.select_problem(path)
        await select_number(inter)
    elif returned_ans[:6] == "number":
        number_of_problems = int(returned_ans[6:])
        use_and_already_learnt = word_test.generate_problems(data, number_of_problems)
        use = use_and_already_learnt[0]
        already_learnt = use_and_already_learnt[1]
        await manage_flow(inter, data, use, number_of_problems, 0, 0)
    elif returned_ans[:3] == "ans":
        if returned_ans[3:6] == "crr":
            correct += 1
            embed = discord.Embed(
                title = "正解",
                color = discord.Colour.blue(),
                description = f"{asked + 1}問中{correct}問正解！"
            )
            await inter.response.send_message(embed=embed)
            data[use[asked][3]][0] += 1
            print(data[use[asked][3]])
            asked += 1
        elif returned_ans[3:6] == "wng":
            embed = discord.Embed(
                title = "不正解",
                color = discord.Colour.red(),
                description = f"{asked + 1}問中{correct}問正解！\n {use[asked][1]}: {ask[correct_ans]}"
            )
            await inter.response.send_message(embed=embed)
            data[use[asked][3]][0] = 0
            print(data[use[asked][3]])
            asked += 1
        await manage_flow(inter, data, use, number_of_problems, asked, correct)

async def manage_flow(inter: discord.Interaction, data: list, use: list, number_of_problems: int, asked: int, correct: int):
    global ask, correct_ans, path
    if asked < number_of_problems:
        correct_ans_and_problem = word_test.submit_question(asked, use)
        correct_ans = correct_ans_and_problem[1]
        ask = correct_ans_and_problem[2]
        embed = discord.Embed(
            title=use[asked][1],
            color=discord.Colour.green(),
        )
        for j in range(1, 10):
            embed.add_field(name=str(j), value=ask[j])
        if not inter.response.is_done():
            await inter.response.send_message(embed=embed)
        else:
            await inter.followup.send(embed=embed)
        await make_options(inter, ask, correct_ans, correct)
    else:
        await terminate_test(inter)

async def make_options(inter: discord.Interaction, ask, correct_ans, correct):
    view = discord.ui.View()
    for i in range(1, 10):
        if i == correct_ans:
            button = discord.ui.Button(label=str(i), style=discord.ButtonStyle.primary, custom_id="anscrr" + str(i))
        else:
            button = discord.ui.Button(label=str(i), style=discord.ButtonStyle.primary, custom_id="answng" + str(i))
        view.add_item(button)
    await inter.followup.send("答えを1つ選びなさい", view=view)  # followupを使用してレスポンスを送信

async def select_number(inter: discord.Interaction):
    view = discord.ui.View()
    number_candicates = [10, 30, 50, 100]
    for i in range(4):
        button = discord.ui.Button(label=str(number_candicates[i]), style=discord.ButtonStyle.primary, custom_id="number" + str(number_candicates[i]))
        view.add_item(button)
    await inter.response.send_message("問題数を選びなさい", view=view)

async def terminate_test(inter: discord.Interaction):
    statement = word_test.ending_test(path, data, already_learnt)
    embed = discord.Embed(
        title="テスト終了",
        color=discord.Colour.green(),
        description=statement
    )
    await inter.followup.send(embed=embed)

@tree.command(name="test", description="単語テストを作成")
async def select_problem(inter: discord.Interaction):
    view = discord.ui.View()
    number_candicates = [1, 2, 3, 4]
    for i in range(4):
        button = discord.ui.Button(label=str(number_candicates[i]), style=discord.ButtonStyle.primary, custom_id="problm" + str(number_candicates[i]))
        view.add_item(button)
    await inter.response.send_message("テストの種類を選びなさい", view=view)

bot.run(TOKEN)
