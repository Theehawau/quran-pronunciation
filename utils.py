import os
import sys
import random
import datetime
import pandas as pd
import gradio as gr
import soundfile as sf

global samples_to_record

with open("Record Prompts - Extra.csv", "r") as f: 
        header = f.readline()
        samples_to_record =  [(index, line.strip()) for index, line in enumerate(f)]
        # shuffle the samples
        random.shuffle(samples_to_record)
        samples_to_record = random.choices(samples_to_record, k=50)

def load_data():
    with open("Record Prompts - Extra.csv", "r") as f: 
        global samples_to_record
        header = f.readline()
        samples_to_record =  [(index, line.strip()) for index, line in enumerate(f)]
        # shuffle the samples
        random.shuffle(samples_to_record)
        
global index

def save_audio():
    return gr.Info("Recording done, play to doublecheck or click on 'Save Audio' to save the audio", duration=5), gr.Button(visible=True)

def save_transcription(audio, file_name, text,recorder_path):
    if os.path.exists(file_name):
        file_name = file_name.replace('.wav', f'{random.randint(0, 1000)}.wav')
    sf.write(file_name, audio[1], 16000)
    text_file = file_name.replace('.wav', '.txt')
    os.system(f"touch {text_file}")
    os.system(f"echo '{text}' >> {text_file}")
    os.system(f"echo '{file_name}\t{text}' >> {recorder_path}/recordings.txt")
    return gr.Button("Save Audio",interactive=False)

def activate_button():
    return gr.Button("Save Audio",interactive=True), gr.Audio(sources=["microphone"], label="Begin Presenting", type="numpy")

def clear():
  return None,gr.Button(visible=False)

def clear_markdown():
    return gr.Markdown(value="")

def show_button():
    return gr.Button(visible=True)

def record_new(recorder_dir, transcription_index, audio_name):
    with open(f"{recorder_dir}/recordings.txt", "r") as f:
        done = len(f.readlines())
        if done >= len(samples_to_record):
            # return gr.Column(visible=False), gr.Column(visible=False), gr.Markdown(value="All recordings done!"), "", -1, ""
            done = random.randint(0, len(samples_to_record)-1)
            # gr.Info("Minimum recordings done! Please exit the application.", duration=15)
    ind, text = samples_to_record[done]
    st,err,end,instruction=text.split(',')
    transcription_index=ind
    audio_name = f"{recorder_dir}/{ind:05}.wav"
    return gr.Markdown(value=highlight_template.format(st,err,end)),gr.Markdown(value=instruction_template.format(instruction)), \
            audio_name, transcription_index, audio_name,done

def begin_session(name, gender, age, dialect):
    os.makedirs(f"recordings/{name}-{gender}-{dialect}", exist_ok=True)
    current_time = datetime.datetime.now()
    os.system(f"echo -e 'Login on: {current_time} \nName: {name}\nGender: {gender}\nAge: {age}\nDialect: {dialect}' >> recordings/{name}-{gender}-{dialect}/info.txt")
    if os.path.exists(f"recordings/{name}-{gender}-{dialect}/recordings.txt"):
        return gr.Info("Welcome back! Please continue from where you stopped", duration=3), f"recordings/{name}-{gender}-{dialect}"
    else:
        os.system(f"touch recordings/{name}-{gender}-{dialect}/recordings.txt")
        return gr.Info("Welcome! Please begin your session", duration=3), f"recordings/{name}-{gender}-{dialect}"
    
highlight_template = '<p style="font-family:"Traditional Arabic",font-size:150px;">{0}<span style="color:red;">{1}</span>{2}</p>'

instruction_template = '<p style="font-family:"Traditional Arabic",font-size:150px;"><mark>{0}</mark></p>'

def begin_record(recorder_dir, audio_name, transcription_index):
    load_data()
    with open(f"{recorder_dir}/recordings.txt", "r") as f:
        done = len(f.readlines())
        if done >= len(samples_to_record):
            # return gr.Column(visible=False), gr.Column(visible=False), gr.Markdown(value="All recordings done!"), "", -1, ""
            done = random.randint(0, len(samples_to_record)-1)
    ind, text = samples_to_record[done]
    st,err,end,instruction=text.split(',')
    i = audio_name
    audio_name = f"{recorder_dir}/{ind:05}.wav"
    transcription_index=ind
    return gr.Column(visible=True), gr.Column(visible=False), \
        gr.Markdown(value=highlight_template.format(st,err,end)),gr.Markdown(value=instruction_template.format(instruction)), \
            audio_name, transcription_index, audio_name, done

def increase(num):
    if num == 15:
        return 1
    return num + 1