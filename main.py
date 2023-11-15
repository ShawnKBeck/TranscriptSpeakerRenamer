import streamlit as st
from docx import Document
from striprtf.striprtf import rtf_to_text
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64
import requests


def process_transcript(file, file_type, speaker_names):
    if file_type == 'txt':
        content = file.getvalue().decode('utf-8')
    elif file_type == 'docx':
        doc = Document(file)
        content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_type == 'rtf':
        rtf_content = file.getvalue().decode('utf-8')
        content = rtf_to_text(rtf_content)

    for speaker_id, name in speaker_names.items():
        content = content.replace(f"Speaker {speaker_id}", name)
    
    return content

def export_to_pdf(content):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text_object = c.beginText(40, 750)  # Starting position
    text_object.setFont("Times-Roman", 12)  # Font and size

    for line in content.split('\n'):
        text_object.textLine(line)
        if text_object.getY() < 40:  # Check if we are close to the bottom of the page
            c.drawText(text_object)
            c.showPage()  # Create a new page
            text_object = c.beginText(40, 750)  # Reset text object to top of new page
            text_object.setFont("Times-Roman", 12)

    c.drawText(text_object)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.title("Transcript Speaker Renamer")

    if 'processed_content' not in st.session_state:
        st.session_state['processed_content'] = None

    transcript_file = st.file_uploader("Upload Transcript", type=['txt', 'docx', 'rtf'])

    num_speakers = st.selectbox("Select the number of speakers", range(1, 11), index=3)
    speaker_names = {}
    for i in range(num_speakers):
        name = st.text_input(f"Name for Speaker {i}", key=f"speaker_{i}")
        if name:
            speaker_names[i] = name

    if st.button("Process Transcript"):
        if transcript_file is not None and speaker_names:
            file_type = transcript_file.name.split('.')[-1]
            st.session_state['processed_content'] = process_transcript(transcript_file, file_type, speaker_names)
            st.text_area("Processed Transcript", st.session_state['processed_content'], height=250)

    if st.session_state['processed_content']:
        if st.button("Export as PDF"):
            pdf = export_to_pdf(st.session_state['processed_content'])
            b64 = base64.b64encode(pdf).decode()
            href = f'<a href="data:file/pdf;base64,{b64}" download="processed_transcript.pdf">Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
