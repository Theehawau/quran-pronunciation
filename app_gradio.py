import random
import gradio as gr
import pandas as pd
import os
import random
import soundfile as sf
from utils import *


# current_audio, _, current_text = give_audio_text()
callback = gr.CSVLogger()

with gr.Blocks(title = "Fix Transcription") as demo:  
    dummy = gr.State(value=0)
    transcription_index = gr.State(value=0)
    current_text = "<p></p>"
    current_instruction = "<p></p>"
    audio_name = gr.State(value="")
    recorder_path = gr.State(value="")
 # <p> Record an audio by reading the transcription with the errors (in red text). Follow the instructions highlighted in yellow when provided.</p> \
    gr.Markdown('<div style="display: flex; justify-content: space-between;"> \
                 <div style="flex: 1; padding: 0 10px;"> \
                    <div align="left"> \
                        <h2>Quran Pronunciation</h2> \
                        <h4>Instructions</h4> \
                        <p> سجل تسجيلًا صوتيًا بقراءة النص مع الأخطاء (بالنص الأحمر). اتبع التعليمات المميزة باللون الأصفر عند وجودها </p> \
                        <p> </p> \
                        <h4>Thanks</h4> \
                    </div> \
                </div>')
    
    with gr.Column() as recorder_details:
        gr.Markdown('<h3> Give some demography details to begin/continue.</h3>')
        with gr.Row():
            recorder_name = gr.Textbox(label="Recorder Name", placeholder="Enter your name")    
            recorder_dialect = gr.Dropdown(
            ["saudi", "emirati", "egyptian", "iran", "tunisian", "morrocan", "algerian"], label="Native Arabic Dialect", info="Will add more dialects later!"
            )
            gender = gr.Radio(
                ["Female", "Male"], label="Gender"
            )
            age = gr.Radio(
                ["Adult", "child"], label="Age Group"
            )
        consent = gr.Checkbox(label="I agree to donate my recordings for research purposes, your identity is protected.")
        begin_session_btn = gr.Button("Begin Recording", variant="primary")
        
        
    with gr.Column(visible=False) as recording_block:
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
        
    get_new_audio.click(save_transcription, [audio, audio_file_name, transcription, recorder_path],
                        [get_new_audio])\
                .then(clear, [], [audio,get_new_audio])\
                .then(record_new, [recorder_path,transcription_index,audio_name],
                      outputs=[transcription,instruction,audio_name,transcription_index, audio_file_name])\
                .then(activate_button, outputs=[get_new_audio, audio])
            
    begin_session_btn.click(begin_session,
                            inputs=[recorder_name, gender, age, recorder_dialect],
                            outputs=[dummy, recorder_path])\
                     .then(begin_record, [recorder_path, audio_name,transcription_index],
                           [recording_block, recorder_details, transcription,instruction,
                            audio_name,transcription_index, audio_file_name])
                                
                                
if __name__ == "__main__":   
    demo.queue()   
    demo.launch(share=True)