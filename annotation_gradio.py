import os
import re
import random

import gradio as gr
import pandas as pd

from glob import glob
from pathlib import Path

output_file = "annotation.csv"
current_audio="Sample_verse.wav"
current_text = " ".join(str("طَيِّ السِّجِلِّ لِلْكُتُبِ").replace(" ", "_"))

audio_root = "./recordings_OI" 

wav_files= list(glob(f"{audio_root}/*/*.wav"))
txt_files=[x.replace(".wav",".txt") for x in wav_files]

aud_text = list(zip(wav_files, txt_files))

global index
with open(output_file, 'r') as f:
    index = sum(1 for line in f)

def get_audio_path(aud_text):
    for i in aud_text:
        yield i
     
pattern = r'>(.*?)<span style=".*?">(.*?)</span>(.*?)</p>'   
def read_txt(path):
    with open(path,"r") as f:
        x = f.readline().strip()
        match = re.search(pattern, x)
        if match is not None:
            x_ = f"{match.group(1)}{match.group(2)}{match.group(3)}"
        else:
            x_ = x.replace("<p>", "").replace("</p>", "")\
                .replace('<span style="color:red;">', "").replace("</span>", "")\
                .replace('<h4>', "").replace("</h4>", "")
    return x, x_

# file_path = "./Record Prompts - Extra.csv"
file_path = "./Record Prompts - Sheet3.csv"

texts_instructions = {}

texts_plain_instruction = {}
def get_separated(text):
    return " ".join([x.replace("  "," ").replace(" ", "_") for x in text])

with open(file_path, "r") as f:
    header = f.readline()
    for line in f:
        data = line.strip().split(",")
        data = [d.replace('\n','').replace("  "," ") for d in data]
        # text = f"{data[0]}{data[1]}{data[2]}"
        text = f"{data[1]}{data[2]}{data[3]}"
        # texts_instructions[text] = get_separated(data[0])
        text = text.replace(" ", "")
        texts_instructions[text] = get_separated(data[0])
        
        
with open(file_path, "r") as f:
    header = f.readline()
    for line in f:
        data = line.strip().split(",")
        data = [d.replace('\n','').replace("  "," ") for d in data]
        # text = f"{data[0]}{data[1]}{data[2]}"
        text = f"{data[1]}{data[2]}{data[3]}"
        text = text.replace(" ", "")
        texts_plain_instruction[text] = '<p style="font-family:"Traditional Arabic",font-size:150px;"><mark>{0}</mark></p>'.format(data[4])

def give_audio_text(gen=None):
    global current_audio
    global current_text
    global aud_text_generator
    global index, ai_annotation, plain_instruction
    # Use the passed generator or default to the global one
    if gen is None:
        gen = aud_text_generator
    try:
        current_audio, current_text = next(gen)
        current_text, x_ = read_txt(current_text)
        ai_annotation = texts_instructions.get(x_.strip().replace(" ", "").replace("ۚ",""), get_separated(x_.strip()))
        plain_instruction = texts_plain_instruction.get(x_.strip().replace(" ", "").replace("ۚ",""), "")
        # x_ = " ".join(str(x_).replace(" ", "_"))
        index +=1
        return current_audio, current_audio, ai_annotation ,current_text, plain_instruction
    
    except StopIteration:
        aud_text_generator = get_audio_path(aud_text) # Reset the generator
        current_audio = next(aud_text_generator)  # Start from the beginning
        print("Current Audio after reset: ", current_audio)
        gr.Info("Annotation Completed! Thank you for your time. Please close the tab!", duration=0)
        return current_audio, current_audio, current_text,current_text, current_text

def save_transcription(path, text, additional_errors=""):
    with open(f"{output_file}", "a") as f:
        f.write(f"{path}\t{text}\t{additional_errors}\n")
    return gr.Button("Get New Audio/Save updated transcription",interactive=False)

def activate_button():
    return gr.Button("Get New Audio/Save updated transcription",interactive=True)

def increase(num):
    if num == len(aud_text):
        return 1
    return num + 1

start_index = 1

def begin_annotation(annotator):
    os.makedirs(f"./annotations/{annotator}", exist_ok=True)
    global output_file, index, current_audio, current_text, ai_annotation, plain_instruction, start_index
    output_file = f"./annotations/{annotator}/annotation.csv"
    with open(output_file, 'r') as f:
        index = sum(1 for line in f)
    start_index = index
    aud_text_generator = get_audio_path(aud_text[index:])
    current_audio, current_text = next(aud_text_generator)
    current_text, x_ = read_txt(current_text)
    ai_annotation = texts_instructions.get(x_.strip().replace(" ", "").replace("ۚ",""), get_separated(x_.strip()))
    plain_instruction = texts_plain_instruction.get(x_.strip().replace(" ", "").replace("ۚ",""), "")
    return gr.Column(visible=True), gr.Column(visible=False), \
        start_index, current_audio,current_audio, current_text,plain_instruction, ai_annotation

aud_text_generator = get_audio_path(aud_text[index:])
current_audio, current_text = next(aud_text_generator)
current_text, x_ = read_txt(current_text)
ai_annotation = texts_instructions.get(x_.strip().replace(" ", "").replace("ۚ",""), get_separated(x_.strip()))
plain_instruction = texts_plain_instruction.get(x_.strip().replace(" ", "").replace("ۚ",""), "")
    
with gr.Blocks(title = "Transcription Instruction") as instruction:
    gr.Markdown("""
    <div align="center"> 
        <h2>Quran Pronunciation Annotation</h2> 
    </div> 
                
    # **الغرض من العمل**

    ستقوم بتحديد الأخطاء النطقية التي يقوم بها المتكلم أثناء نطقه للجمل، وفقًا للإرشادات التالية

    # **خطوات العمل**

    1. استمع بعناية للتسجيل الصوتي المرفق. تأكد من متابعة كل كلمة بدقة.
    2. قبل البدء، اقرأ وصف الخطأ المطلوب (مثال: استبدال الفتحة بالكسرة، أو نطق الحرف بطريقة غير صحيحة).
    3. افهم الجملة المتوقعة مع تمييز الخطأ المطلوب فيها باللون الأحمر.
    4. استمع مجددًا للتسجيل الصوتي للتحقق مما إذا كان المتكلم قد قام بالخطأ النطقي المطلوب.
    5. إذا لاحظت وجود أي أخطاء إضافية قام بها المتكلم ولم يتم تحديدها مسبقًا، قم بتوثيقها أيضًا.
    6. راجع كل كلمة منطوقة لتحديد أي انحراف إضافي عن النطق الصحيح.
    7. قم بتوثيق الأخطاء بطريقة منظمة وواضحة، مع الإشارة إلى نوع الخطأ وموقعه في الجملة.
    8. إستخدم الرمز @ للإشارة إلى كل حرف أو حركة خاطئة.
    9. بعد رمز @، قم بإضافة النسخة التي نُطقت بشكل خاطئ.
    10. يوجد ثلاث أنواع للاخطاء: استبدال , حذف أو أضافة:

    ## **الاستبدال**

    - إستبدال حرف بحرف أو حركة بحركة
    - مثال استبدال العين بالحاء في العسر الي الحسر. تكتب ا ل ع@ح ُ س ر

    ## **حذف**

    - حذف حرف أو حركة
    - مثال حذف التشديد في أنَّ الي أنَ. تكتب إ ِ نّ@  َ. يوجد مسافة بعد ال@ في حالة الحذف.

    ## **إضافة**

    - إضافة حرف أو حركة
    - مثال إضافة حرف في العُسر الي العُوسر. تكتب ا ل ع ُ @و س ر. يوجد مسافة قبل ال @ في حالة الأضافة.

    في حال وجود أي استفسارات أو مواجهة أي مشكلات، يمكنك التواصل عبر البريد الإلكتروني التالي:
    omnia@lst.uni-saarland.de


    شكراً جزيلاً لتعاونك والتزامك بالدقة
    """)

with gr.Blocks(title = "Fix Transcription") as tool:  
    
    with gr.Column(visible=True) as annotation_name:
        annotator_name = gr.Textbox(label="Annotator Name", placeholder="Enter your name", interactive=True)
        begin_annotate = gr.Button("Begin Annotation", variant="primary")
    
    with gr.Column(visible=False) as annotation_block:
        progress = gr.Number(start_index, label = f"X of {len(aud_text)} audios" ,interactive=False)
        audio = gr.Audio(label="Audio", interactive=False, value=current_audio, autoplay=True)
        audio_file_name = gr.Textbox(value=current_audio, label="Audio File Name", interactive=False, visible=False)
        
        gr.Markdown('<h3>Expected Transcription:</h3>')
        original_text = gr.Markdown(value=current_text)
        gr.Markdown('<h3>Error Details:</h3>')
        original_annotation = gr.Markdown(f"{plain_instruction}")
        
        transcription = gr.Textbox(label="Actual transcription (editable)", value=ai_annotation, interactive=True, rtl=True)

        additional_errors = gr.Textbox(label="Additional Errors (optional)", value="", placeholder="Enter additional errors", interactive=True, rtl=True)
        get_new_audio = gr.Button("Get New Audio/Save updated transcription",
                            variant="primary")
    
    begin_annotate.click(begin_annotation, [annotator_name], \
                         [annotation_block, annotation_name, progress, audio, audio_file_name,\
                             original_text, original_annotation, transcription])
    
    get_new_audio.click(save_transcription, [audio_file_name, transcription, additional_errors], [get_new_audio]).\
        then(give_audio_text, outputs=[audio,audio_file_name, transcription, original_text, original_annotation]).\
            then(activate_button, outputs=[get_new_audio]).then(increase,progress, progress)
    
    
    
demo = gr.TabbedInterface([instruction, tool], ["Instructions", "Annotate"])
    
if __name__ == "__main__":
    demo.launch(share=True)
    
    