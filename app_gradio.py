import random
import gradio as gr
import pandas as pd
import os
import random
import soundfile as sf
from utils import *


with gr.Blocks(title = "Quran Pronunciation") as demo:  
    dummy = gr.State(value=0)
    transcription_index = gr.State(value=0)
    current_text = "<p></p>"
    current_instruction = "<p></p>"
    audio_name = gr.State(value="")
    recorder_path = gr.State(value="")       
       
    gr.Markdown('<div style="display: flex; justify-content: space-between;"> \
                    <div style="flex: 1; padding: 0 10px;"> \
                        <div align="center"> \
                        <h2>Quran Pronunciation</h2> \
                        </div> \
                    </div>')  
    
    
    instructions = gr.Markdown('<div style="display: flex; justify-content: space-between;"> \
                <div style="flex: 1; padding: 0px 0px;"> \
                    <div align="left"> \
                        <h4 align="right">اتبع التعليمات الاتية </h4> \
                        <p align="right"> .ستقوم بتسجيل صوتي لجمل . الجمل تحتوي علي أخطاء (مميزة بالون الأحمر)</p> \
                            <p align="right">  .يرجى قراءة الجملة بالخطأ الموضح مرة قبل التسجيل</p> \
                            <p align="right">  .اتبع التعليمات المميزة باللون الأصفر </p> \
                            <p align="right"> .يرجى قراءة الجملة بدون ترتيل أو قواعد تجويد </p> \
                            <p align="right">  .يرجي التسجيل في مكان هادئ </p> \
                            <p align="right">  .يمكنك الرجوع إلي العينة كمثال </p> \
                        <p align="right">شكرا</p> \
                    </div> \
                </div>')
    
    with gr.Accordion("Sample") as sample_rec:
            gr.Markdown('<p align="right"> وَإِنَّا لَنَحْنُ نُحْيِي وَنُمِيتُ وَنَحْنُ الْوَارِثُونَ</p>')
            gr.Audio(value="Sample_verse.wav")

    with gr.Column() as recorder_details:
        gr.Markdown('<h3> Give some demography details to begin/continue.</h3>')
        with gr.Row():
            recorder_name = gr.Textbox(label="Recorder Name", placeholder="Enter your name")    
            recorder_dialect = gr.Dropdown(
            ["saudi", "emirati", "egyptian", "tunisian", "morrocan", "algerian", "syrian", "jordanian","sudanese","non-native"], label="Native Arabic Dialect", info="Will add more dialects later!"
            )
            gender = gr.Radio(
                ["Female", "Male"], label="Gender"
            )
            age = gr.Dropdown(
                ["18-50","<10", ">50"], label="Age Group"
            )
        consent = gr.Checkbox(label="I agree to donate my recordings for research purposes, your identity is protected.")
        begin_session_btn = gr.Button("Begin Recording", variant="primary",visible=False)
        
        
    with gr.Column(visible=False) as recording_block:
        progress = gr.Number(1, label = "X of 50 audios" ,interactive=False)
        gr.Markdown('<h3>Error Details:</h3>')
        instruction = gr.Markdown(value=current_instruction)
        gr.Markdown('<h3>Transcription:</h3>')
        transcription = gr.Markdown(value=current_text)
        
        audio_file_name = gr.Textbox(value=audio_name.value, label="Audio File Name", interactive=False, visible=True)
        
        audio = gr.Audio(sources=["microphone"], label="Begin Recording", type="numpy",
                        waveform_options={"sample_rate": 16000})
        
        get_new_audio = gr.Button("Save Audio",
                                variant="primary", visible=False)

        
        audio.stop_recording(save_audio, [], [dummy, get_new_audio])
        audio.clear(save_audio, [], [dummy, get_new_audio])
    
                # .then(clear, [], [audio,get_new_audio])\
    
    get_new_audio.click(save_transcription, [audio, audio_file_name, transcription, recorder_path],
                        [get_new_audio])\
                .then(record_new, [recorder_path,transcription_index,audio_name],
                      outputs=[transcription,instruction,audio_name,transcription_index, audio_file_name,progress])\
                .then(activate_button, outputs=[get_new_audio, audio])
    
    consent.select(show_button,[], begin_session_btn)
    
    begin_session_btn.click(begin_session,
                            inputs=[recorder_name, gender, age, recorder_dialect],
                            outputs=[dummy, recorder_path])\
                    .then(clear_markdown, [], instructions)\
                    .then(begin_record, [recorder_path, audio_name,transcription_index],
                           [recording_block, recorder_details, transcription,instruction,
                            audio_name,transcription_index, audio_file_name, progress])
                                
                                
if __name__ == "__main__":   
    # demo.queue()   
    demo.launch(share=True)