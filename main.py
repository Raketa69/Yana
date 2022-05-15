# ЯНА v 1.0
import os
import sys
import vosk
import json
import time
import queue
import config
import datetime
import playsound
import webbrowser
from gtts import gTTS
import sounddevice as sd
from fuzzywuzzy import fuzz

print(f"{config.VA_NAME} (v{config.VA_VER}) почав свою роботу ...")

model = vosk.Model("model_main")
samplerate = 16000
device = 1
q = queue.Queue()


def respond(voice: str):
    print("respond: " + voice)
    # print(recognize(voice))
    if voice.startswith(config.VA_ALIAS):
        # обращаются к ассистенту
        cmd = recognize(filter_cmd(voice))
        # print(cmd)
        if cmd['cmd'] not in config.VA_CMD_LIST.keys():
            speak("Слухаю")
        else:
            execute_cmd(cmd['cmd'])
    else:
        cmd = recognize(filter_cmd(voice))
        execute_cmd(cmd['cmd'])


def execute_cmd(cmd: str):
    if cmd == 'ctime':
        # current time
        now = datetime.datetime.now()
        text = "Зараз " + str(now.hour) + ":" + str(now.minute)
        speak(text)
        pass
    elif cmd == 'open_browser':
        opera_path = 'C:/Users/RAKETA/AppData/Local/Programs/Opera GX/launcher.exe %s'
        webbrowser.get(opera_path).open("")
    # elif cmd == 'help':
    #    # help
    #    text = "Я можу: ..."
    #    text += " повідомити час ..."
    #    text += "розповідати анекдоти ..."
    #    text += "та відкривати браузер"
    #    speak(text)
    elif cmd == 'radio':
        opera_path = 'C:/Users/RAKETA/AppData/Local/Programs/Opera GX/launcher.exe %s'
        webbrowser.get(opera_path).open("https://www.youtube.com")

    elif cmd == 'joke':
        speak(config.VA_JKS)
    elif cmd == 'hi1':
        speak("Героям Слава")
    elif cmd == 'hi2':
        speak("Смерть ворогам")
    elif cmd == 'hi3':
        speak("Понад усе")


def filter_cmd(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in config.VA_CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def speak(text):
    print(text)
    tts = gTTS(text=text, lang="uk")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    time.sleep(1)
    os.remove(filename)


def greeting():
    speak("Доброго вечора, Владиславе")


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def listen(callback):
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16',
                           channels=1, callback=q_callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                # print(rec.Result())
                res = json.loads(rec.Result())
                # print(res['text'])
                # print("listen: ")
                # recognized_data = rec.FinalResult()[:]
                # print(recognized_data)
                callback(res['text'])


greeting()
listen(respond)
