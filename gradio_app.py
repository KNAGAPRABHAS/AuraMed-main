#SMTP_USER=aura.med.ai.doctor@gmail.com
#SMTP_PASS=nwdlhupervkudtke
#
import gradio as gr
import os
from dotenv import load_dotenv
from auth_utils import send_otp, verify_otp
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

load_dotenv()


system_prompt = """
You have to act as a professional doctor, I know you are not, but this is for learning purposes. 
What's in this image? Do you find anything wrong with it medically? 
If you make a differential, suggest some remedies for them. Do not add any numbers or special characters in 
your response. Your response should be in one long paragraph. Also, always answer as if you are answering a real person.
Do not say 'In the image I see' but say 'With what I see, I think you have ....'
Don't respond as an AI model in markdown, your answer should mimic that of an actual doctor, not an AI bot. 
Keep your answer concise  and also give medical prescription like what medicines to use in detail including the dosage of medicines to be used in bullet point without asterisk or any symbols . No preamble, start your answer right away, please.
"""

# Session state to track logged-in users
session_state = {"logged_in": False, "otp": "", "user_contact": ""}

def login(user_input):
    otp = send_otp(user_input)
    session_state["otp"] = otp
    session_state["user_contact"] = user_input
    return f"OTP sent to {user_input}"

def verify_user(input_otp):
    if verify_otp(input_otp, session_state["otp"]):
        session_state["logged_in"] = True
        return "Login successful!"
    else:
        return "Invalid OTP. Please try again."

def process_inputs(audio_filepath, image_filepath):
    if not session_state["logged_in"]:
        return "Please log in first.", "", None

    if audio_filepath:
        speech_to_text_output = transcribe_with_groq(
            GROQ_API_KEY=os.getenv("GROQ_API_KEY"), 
            audio_filepath=audio_filepath,
            stt_model="whisper-large-v3"
        )
    else:
        speech_to_text_output = "No audio input provided"

    if image_filepath:
        try:
            query = system_prompt + speech_to_text_output
            doctor_response = analyze_image_with_query(
                query=query, 
                encoded_image=encode_image(image_filepath), 
                model="meta-llama/llama-4-scout-17b-16e-instruct"
            )
        except Exception as e:
            doctor_response = f"Error analyzing image: {str(e)}"
    else:
        doctor_response = "No image provided for analysis"

    try:
        output_filepath = "final.mp3"
        text_to_speech_with_gtts(input_text=doctor_response, output_filepath=output_filepath)
        voice_of_doctor = output_filepath
    except Exception as e:
        voice_of_doctor = None
        doctor_response += f"\nError generating voice: {str(e)}"

    return speech_to_text_output, doctor_response, voice_of_doctor

with gr.Blocks(theme=gr.themes.Default(primary_hue="blue")) as demo:
    gr.Markdown("# 🩺 AI Doctor Assistant")

    with gr.Tab("Login"):
        user_input = gr.Textbox(label="Email")
        send_button = gr.Button("Send OTP")
        otp_input = gr.Textbox(label="Enter OTP")
        verify_button = gr.Button("Verify OTP")
        login_status = gr.Textbox(label="Status")

        send_button.click(fn=login, inputs=[user_input], outputs=[login_status])
        verify_button.click(fn=verify_user, inputs=[otp_input], outputs=[login_status])

    with gr.Tab("Doctor Interface"):
        lang_select = gr.Dropdown(choices=["en"], label="Language", value="en", visible=False)
        audio = gr.Audio(sources=["microphone"], type="filepath", label="Audio Input (Speech)")
        image = gr.Image(type="filepath", label="Image Input (Diagnosis)")
        stt_output = gr.Textbox(label="Speech to Text")
        doctor_text = gr.Textbox(label="Doctor's Response")
        doctor_audio = gr.Audio(label="Doctor's Voice Response")
        diagnose_button = gr.Button("Diagnose")

        diagnose_button.click(fn=process_inputs, inputs=[audio, image], outputs=[stt_output, doctor_text, doctor_audio])

demo.launch(share=True)
