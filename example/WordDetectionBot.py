import discord
from WordDetection import WordDetection
BOT_TOKEN = 'Your Bot Token'

client = discord.Client()
a = WordDetection()
a.LoadData()
a.LoadBadWordData()


@client.event
async def on_ready():
    print('욕설 감지 봇 가동시작')


@client.event
async def on_message(message):
    word = str(message.content)
    a.input=word
    a.W2NR()
    a.lime_compare(a.BwT , a.WTD[0] , 0.9)
    result = a.result
    a.lime_compare(a.BwT , a.WTD[1] , 0.9)
    result += a.result
    if len(result) == 0:
        return None
    for j in result:
            word = word[0:j[0]] + '-'*(j[1]-j[0]+1) + word[j[1]+1:]
    embed = discord.Embed(title = '욕설이 감지됨' , color = 0xFFE400)
    embed.add_field(name = '필터링된 채팅' , value = word)
    embed.add_field(name = '보낸 사람' , value = str(message.author))
    await message.channel.send(embed = embed)
    await message.delete()
        
client.run(BOT_TOKEN)