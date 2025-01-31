import discord
from discord import *
import re
import os
from dotenv import load_dotenv
from discord.ext import commands
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="deepseek-r1:14b") #requires you to have the ollama model installed

load_dotenv()

token = os.getenv("BOT_TOKEN")

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

context_dict = {}

@client.event
async def on_ready():    
    print(f"We have logged in as {client.user}")
    
    try:
        synced = await tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


@tree.command(name="chat", description="ask the bot a question")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def Chat(interaction: discord.Interaction, prompt: str):
    if len(prompt) <= 1:
        await interaction.response.send_message("Please enter a prompt that is greater than 1 character", ephemeral=True)
        return
    
    prompt2 = ChatPromptTemplate.from_template(template)
    chain = prompt2 | model
    
    await interaction.response.defer()
    
    result = chain.invoke({"context": "", "question": prompt})
    
    view = EmbedView(result)
    await interaction.followup.send(embed=view.build())
    
    
    
async def RespondAsync(interaction : discord.Interaction, prompt : str):
    
    prompt2 = ChatPromptTemplate.from_template(template)
    chain = prompt2 | model
    
    result = chain.invoke({"context": "", "question": prompt})
    
    view = EmbedView(result)
    await interaction.followup.send(embed=view.build())

class EmbedView:
    def __init__(self, result: str):
        self.result = result
        
    def build(self):
        think_content = re.findall(r"<think>(.*?)</think>", self.result, re.DOTALL)
        outside_content = re.sub(r"<think>.*?</think>", "", self.result, flags=re.DOTALL).strip()
            
        embed = discord.Embed(title="Response")
        embed.add_field(name="Thinking", value=think_content[0][:1024] if think_content else "No thinking", inline=False)
        #embed.add_field(name="Response", value="\u200b", inline=False)
        for i in range(0, len(outside_content), 1024):
            chunk = outside_content[i:i + 1024]
            embed.add_field(name= "\u200b" if i != 0 else "Response", value=chunk, inline=False)
        
        return embed
    
client.run(token)
