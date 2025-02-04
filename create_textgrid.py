import os
import re
import soundfile as sf

from glob import glob

# change recording root to the location of the recordings
audio_root = "./recordings_OI" 

recorders = [x for x in os.walk(audio_root)][0][1] 
wav_files = []
    
wav_files = list(glob(f"{audio_root}/*/*.wav"))

txt_files=[x.replace(".wav",".txt") for x in wav_files]

aud_text = list(zip(wav_files, txt_files))

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

file_path = "./Record Prompts - Sheet3.csv"

texts_instructions = {}

texts_plain_instruction = {}
def get_separated(text):
    return " ".join([x.replace("  "," ").replace(" ", "_") for x in text])\
            .replace(" @ ","@")
            
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
        text = f"{data[1]}{data[2]}{data[3]}"
        text = text.replace(" ", "")
        texts_plain_instruction[text] = '{0}'.format(data[4])

TextGrid = '''File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0 
xmax = {0} 
tiers? <exists> 
size = 3 
item []: 
    item [1]:
        class = "IntervalTier" 
        name = "Original Text" 
        xmin = 0 
        xmax = {0}  
        intervals: size = 1 
        intervals [1]:
            xmin = 0 
            xmax = {0}  
            text = "{1}"

    item [2]:
        class = "IntervalTier" 
        name = "Error Details" 
        xmin = 0 
        xmax = {0}
        intervals: size = 1 
        intervals [1]:
            xmin = 0 
            xmax = {0} 
            text = "{2}"

    item [3]:
        class = "IntervalTier" 
        name = "Annotation" 
        xmin = 0 
        xmax = {0} 
        intervals: size = 1 
        intervals [1]:
            xmin = 0 
            xmax = {0} 
            text = "{3}" 
'''


for audio, text in aud_text:
    
    _, text = read_txt(text)
    flipped_text = ' '.join(text.split()[::-1])
    wav,sr = sf.read(audio)
    audio_length = str(round(len(wav)/sr,2))
    
    text = text.replace(" ", "")
    text_grid_file = audio.replace('.wav', '.TextGrid')
    if text in texts_instructions:
        instruction = texts_plain_instruction[text]
        flipped_instruction = ' '.join(instruction.split()[::-1])
        annotation = "بداية _ " + texts_instructions[text] + " _ نهاية"
        # flipped_annotation = ' '.join(annotation.split()[::-1])
        with open(text_grid_file,"w") as w:
            w.write(TextGrid.format(audio_length,flipped_text,flipped_instruction,annotation))
        w.close()
        print("Created", text_grid_file)
        print("Source", audio)
    else:
        instruction = ""
        annotation = "بداية _ " + text + " _ نهاية"
        t = TextGrid.format(audio_length,flipped_text,instruction,annotation)
        with open(text_grid_file,"w") as w:
            w.write(TextGrid.format(audio_length,flipped_text,flipped_instruction,annotation))
        w.close()
        print("Created", text_grid_file)
        print("Source", audio)
        