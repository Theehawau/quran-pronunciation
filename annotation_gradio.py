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

audio_root = "./recordings/"    

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
        x_ = f"{match.group(1)}{match.group(2)}{match.group(3)}"
    return x, x_

file_path = "./Record Prompts - Extra.csv"

texts_instructions = {}

texts_plain_instruction = {}

with open(file_path, "r") as f:
    header = f.readline()
    for line in f:
        data = line.strip().split(",")
        data = [d.replace('\n','')for d in data]
        text = f"{data[0]}{data[1]}{data[2]}"
        if data[3].__contains__("إستبدال"):
            ori, rep = data[3].split("/")
            ori =  ori.replace("إستبدال", "")
            b = " ".join(str(data[0]).replace(" ", "_"))
            e = " ".join(str(data[2]).replace(" ", "_"))
            text_instruction = str(f"{b} {rep}@{ori} {e}")
        
        else:
            b = " ".join(str(data[0]).replace(" ", "_"))
            e = " ".join(str(data[2]).replace(" ", "_"))
            t = " ".join(str(data[1]).replace(" ", "_"))
            text_instruction = str(f"{b} {t} {e}")
        texts_instructions[text] = text_instruction
        
with open(file_path, "r") as f:
    header = f.readline()
    for line in f:
        data = line.strip().split(",")
        data = [d.replace('\n','')for d in data]
        text = f"{data[0]}{data[1]}{data[2]}"
        texts_plain_instruction[text] = '<p style="font-family:"Traditional Arabic",font-size:150px;"><mark>{0}</mark></p>'.format(data[3])
    
def get_separated(text):
    return " ".join([x.replace(" ", "_") for x in text])
    
aud_text_generator = get_audio_path(aud_text[index:])
current_audio, current_text = next(aud_text_generator)
current_text, x_ = read_txt(current_text)
ai_annotation = texts_instructions.get(x_.strip(), get_separated(x_.strip()))
plain_instruction = texts_plain_instruction.get(x_.strip(), "")
# x_ =  " ".join(str(x_).replace(" ", "_"))


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
        ai_annotation = texts_instructions.get(x_.strip(), get_separated(x_.strip()))
        plain_instruction = texts_plain_instruction.get(x_.strip(), "")
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

def begin_annotation(annotator):
    os.makedirs(f"./annotations/{annotator}", exist_ok=True)
    global output_file
    output_file = f"./annotations/{annotator}/annotation.csv"
    return gr.Column(visible=True), gr.Column(visible=False)

    
with gr.Blocks(title = "Transcription Instruction") as instruction:
    # gr.Markdown('<div style="display: flex; justify-content: space-between;"> \
    #              <div style="flex: 1; padding: 0 0;"> \
    #                 <div align="left"> \
    #                     <h2>Quran Pronunciation Annotation</h2> \
    #                 </div> \
    #             </div>')
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
    omnia@lst.uni-saarland.d


    شكراً جزيلاً لتعاونك والتزامك بالدقة
    """)

    
#     gr.Markdown("""
# ### **Original Text:**

# *"إِنَّ مَعَ الْعُسْرِ يُسْرًا"*

# ### **Normalized and Split Text:**

# **إ  ِ ن  ّ  َ _ م  َ ع  َ _ ا ل ع  ُ س ر ِ _ ي  ُ س ر  ً ا**

# - **Explanation:**
#     - Words are separated by **"_"**.
#     - Each word is split into its individual **characters and diacritics**.
#     - **Characters with Sukun** are skipped (since no vowel is pronounced).

# ---

# ### **Stages of Annotation**

# 1. **Listen Carefully:**
#     - Listen to the audio carefully, preferably at reduced speed to catch subtle pronunciation differences.
# 2. **Correct Mispronunciations:**
#     - Compare the speaker's pronunciation with the provided normalized text.
#     - If a mistake is found, annotate it by marking incorrect characters and noting what was said instead.

# ### **Example Annotation**

# ### **Scenario:**

# The speaker made the following errors while reciting:

# 1. Omitted the **shadda** on "نّ".
# 2. Replaced **ع** with **ح** in “**ا ل ع  ُ س ر**”
# 3. Said **يَسْرًا** instead of **يُسْرًا**.

# ## **Annotation Output:**

# ### Case 1: Clear Subsitution Or Omission

# If the speaker substitutes a character or vowel with another **clear** character or vowel or omits it entirely, here is an example:

# **إ  ِ ن   ّ@   َ  _ م  َ ع   َ _ ا ل ع@ح  ُ س ر  ِ  _ ي   ُ@ َ س ر  ً ا**

# - **Explanation of Annotation:**
#     - The **@** symbol marks each incorrect character/diacritic.
#     - After **@**, include the mispronounced version directly.
#     - For example:
#         - **@ن**: The speaker missed the **shadda** on "ن".
#         - **@ح**: The speaker substituted **ح** for **ع**.
#         - **@يَسْرًا**: The speaker incorrectly used a Fatha (**يَ**) instead of a Damma (**يُ**). 
 
# ### Case 2: Ambiguous Substitution

# If the speaker substitutes a character or vowel with an **ambiguous** character or vowel, here is an example:

# - The speaker utters a sound between **م and ن**.
# - A vowel is pronounced with an inclination, such as **َ** blending into **ِ** (a form of **إمالة**).

# **Example 1:**

# **إ  ِ ن@نم ⇒ إ ِ ن**

# **Example 2:**

# **م  َ@ َ ِ ع ⇒ م َ ع**

# The annotation should clarify this by specifying the two characters or vowels involved.

# ### Case 3: Out-of-distribution Substitution

# In this case, you encounter sounds (**V**, **P**, or **G)** that do not naturally exist in Modern Standard Arabic but might appear in dialects due to loanwords or foreign influences. When substituted with closer Arabic sounds, this must be explicitly annotated.

# Here are dialectal examples:

# 1. **Substitution of V**
    
#     In some dialects, **V** may be substituted with **ف**:
    
#     **Example:**
    
#     - **ي ⇒ ف ي V@ف**
# 2. **Substitution of G**
    
    
#     In dialects like Egyptian Arabic, **G** may be substituted with **ج** or **ق**:
    
#     **Example:**
    
#     - **م  َ س ج  ِ د ⇒ G@ج**
# 3. **Substitution of F**
    
#     **P@ب   P@ب**
    
#     Sometimes, **P** from foreign loanwords might be replaced with **B** in certain contexts:
    
#     **Example:**
    
#     - **ب ا ب ⇒ P@ب   P@ب**
# """)

with gr.Blocks(title = "Fix Transcription") as tool:  
    
    with gr.Column(visible=True) as annotation_name:
        annotator_name = gr.Textbox(label="Annotator Name", placeholder="Enter your name", interactive=True)
        begin_annotate = gr.Button("Begin Annotation", variant="primary")
    
    with gr.Column(visible=False) as annotation_block:
        progress = gr.Number(1, label = f"X of {len(aud_text)} audios" ,interactive=False)
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
    
    begin_annotate.click(begin_annotation, [annotator_name], [annotation_block, annotation_name])
    
    get_new_audio.click(save_transcription, [audio_file_name, transcription, additional_errors], [get_new_audio]).\
        then(give_audio_text, outputs=[audio,audio_file_name, transcription, original_text, original_annotation]).\
            then(activate_button, outputs=[get_new_audio]).then(increase,progress, progress)
    
    
    
demo = gr.TabbedInterface([instruction, tool], ["Instructions", "Annotate"])
    
if __name__ == "__main__":
    demo.launch(share=True)
    
    