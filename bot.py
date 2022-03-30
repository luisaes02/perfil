from youtube_dl import cache
from telethon import TelegramClient, events, sync
import asyncio
import os
import zipfile
import re
import requests
from zipfile import ZipFile , ZipInfo 
import multiFile
import random
from bs4 import BeautifulSoup
from mega import Mega
import Client
import traceback
bot_token = 'TOKEN BOT'

api_id = 13876032
api_hash = 'c87c88faace9139628f6c7ffc2662bff'

links =[]

#Users_Data=[['testray11'],['testray12'],['testray13'],['testray14'],['testray15'],['testray16'],['testray17'],['testray18']]
Users_Data=['USER','ID DE LA PAGINA']
ExcludeFiles = ['bot.py','multiFile.py','Client.py','requirements.txt','Procfile','__pycache__','.git','.profile.d','.heroku','bot.session','bot.session-journal','output']

def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if ExcludeFiles.__contains__(f):
                    print('-----Archivo protegido de cache clear')
                else:
                    print('Borrando'+f)
                    os.remove(f)
        return True            
    except Exception as e:
        print(str(e))
        return False


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size


async def upload_to_moodle(f,msg):
            #rand_user=Users_Data[random.randint(0,len(Users_Data)-1)]
            rand_user=Users_Data
            size = await get_file_size(f)
            try:
                await msg.edit('Subiendo \n ' + '\n'  + str(f) + '\n' + str(sizeof_fmt(size)))
                moodle = Client.Client(rand_user[0],'CONTRASEÑA')
                loged = moodle.login()
                if loged == True:
                    resp = moodle.upload_file(f,rand_user[1])
                    data=str(resp).replace('\\','')
                    await msg.edit(f'Archivo Subido con exito!\n\nUser:{rand_user[0]}\n\nLink:'+data)
                    
                 
            except Exception as e:
                print(traceback.format_exc(),'Error en el upload')
                



async def process_file(file,bot,ev,msg):
    try:

        msgurls = ''
        maxsize = 1024 * 1024 * 1024 * 2
        file_size = await get_file_size(file)
        chunk_size = 1024 * 1024 * 100
        #rand_user=Users_Data[random.randint(0,len(Users_Data)-1)]
        rand_user=Users_Data
        
        if file_size > chunk_size:
            await msg.edit('Comprimiendo \n' + str(file) + '\n' + str(sizeof_fmt(file_size)))
            mult_file =  multiFile.MultiFile(file+'.7z',chunk_size)
            zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
            zip.write(file)
            zip.close()
            mult_file.close()
            nuvContent = ''
            i = 0
            data=''
            for f in multiFile.files:
                await msg.edit('Subiendo \n ' + '\n'  + str(f) + '\n' + str(sizeof_fmt(file_size)))
                moodle = Client.Client(rand_user[0],'CONTRASEÑA')
                loged = moodle.login()
                if loged == True:
                    resp = moodle.upload_file(f,rand_user[1])
                    data=data+'\n\n'+str(resp).replace('\\','')
                    
            await msg.edit(f'Archivo Subido con exito!\n\nUser:{rand_user[0]}\n\nLink:'+data)

        else:
            await upload_to_moodle(file,msg)
            os.unlink(file)

    except Exception as e:
            await msg.edit('(Error Subida) - ' + str(e))


async def processMy(ev,bot):
    try:
        text=ev.message.text
        message = await bot.send_message(ev.chat_id, 'Procesando...')
        if ev.message.file:
            await message.edit('Archivo Econtrado Descargando...')
            file_name = await bot.download_media(ev.message)
            await process_file(file_name,bot,ev,message)
    except Exception as e:
                        await bot.send_message(str(e))


async def down_mega(bot,ev,text):
    mega=Mega()
    msg = await bot.send_message(ev.chat_id,'Procesando link de MEGA')
    try:
        mega.login(email='raidel.reuco@gmail.com',password='kurosaki')
    except:
        await msg.edit('Error en la cuenta de MEGA')
    try:    
        await msg.edit(f'Descargando...')
        path=mega.download_url(text)
        await msg.edit(f'Descargado {path} con exito')
        await process_file(str(path),bot,ev,msg)
    except:
        msg.edit('Error en la descarga')
        print(traceback.format_exc())    

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_url_file_name(url,req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/');
            return tokens[len(tokens)-1]
    except:
           tokens = str(url).split('/');
           return tokens[len(tokens)-1]
    return ''

def save(filename,size):
    mult_file =  multiFile.MultiFile(filename+'.7z',size)
    zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
    zip.write(filename)
    zip.close()
    mult_file.close()

async def upload_to_moodle_url(msg,bot,ev,url):
    rand_user=Users_Data
    await msg.edit('Analizando...')
    html = BeautifulSoup(url, "html.parser")
    print(html.find_all('apk'))
    req = requests.get(url, stream=True, allow_redirects=True)
    if req.status_code == 200:
        try:
            chunk_size=1024 * 1024 * 49
            chunk_sizeFixed=1024 * 1024 * 49
            filename = get_url_file_name(url,req)
            filename = filename.replace('"',"")
            file = open(filename, 'wb')
            await msg.edit('Descargando...'+ filename)
            for chunk in req.iter_content(chunk_size=chunk_sizeFixed):
                if chunk:
                    print(file.tell())
                    file.write(chunk)
                else:
                    print('no hay chunk')    

            file.close()
            await process_file(file.name,bot,ev,msg)
        except:
            print(traceback.format_exc())            

        multiFile.files.clear()    
    pass


async def lista(ev,bot,msg):
    global links
    for message in links:
        try:
            multiFile.clear()
            clear_cache()
            text = message.message.text
            if message.message.file:
                msg = await bot.send_message(ev.chat_id,"Descargando..."+text)
                file_name = await bot.download_media(message.message)
                await process_file(file_name,bot,ev,msg)
            elif 'mega.nz' in text:
                await down_mega(bot,ev,text)
            elif 'https' in text or 'http' in text:
                await upload_to_moodle_url(msg,bot,ev,url=text)       
        except Exception as e:
            await bot.send_message(ev.chat_id,e)
    links=[]                 

def init():
    
    try:
        
        bot = TelegramClient( 
            'bot', api_id=api_id, api_hash=api_hash).start(bot_token=bot_token) 
 
        action = 0
        actual_file = ''
    
        @bot.on(events.NewMessage()) 
        async def process(ev: events.NewMessage.Event):
                global links
                text = ev.message.text
                clear_cache()
                multiFile.clear()
                if '#watch' in text:
                    await bot.send_message(ev.chat_id,'Esperando...')
                elif '#cache' in text:

                    clear_cache()  
                elif 'mega.nz' in text:
                    #await down_mega(bot,ev,text)
                    links.append(ev)
                elif 'https' in text or 'http' in text:
                    msg= await bot.send_message(ev.chat_id,'Link encontrado...')
                    links.append(ev)
                    #await upload_to_moodle_url(msg,url=text)      
                elif '/start' in text:
                    msg = await bot.send_message(ev.chat_id,'Proceso Iniciado!')
                    await lista(ev,bot,msg)
                elif ev.message.file:
                    links.append(ev)    
                    #await processMy(ev,bot)
                elif '#clear' in text:
                    links=[]
                        



        loop = asyncio.get_event_loop() 
        loop.run_forever()
    except:
        print(traceback.format_exc())
        init()


if __name__ == '__main__': 
   init()

