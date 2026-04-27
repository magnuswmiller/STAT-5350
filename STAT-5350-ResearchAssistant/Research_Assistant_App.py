'''
Research_Assistant_App.py

*** TODO Add intro write-up here
'''

# Import required libraries
import gradio as gr
from config import OPENAI_CHAT_MODEL, USE_OPENAI

# Build App UI
def build_ui()->gr.Blocks:
    # TODO add LLM backend selection
    active_chat_model = "open ai chat"
    active_embed_model = "nomic embed"

    backend_label = f"OpenAI ({OPENAI_CHAT_MODEL})" if USE_OPENAI else f"Ollama Chat: {active_chat_model} | Ollama Embeddings: {active_embed_model}"

    # Background UI
    with gr.Blocks(title="Research Paper Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"""
                    # Research Paper Assistant

                    **AI-Powered Summarization, Citation Extraction, and Q/A**

                    Backend: `{backend_label}`
                    """)

        # Upload Documents UI
        with gr.Tab("Upload Documents"):
            gr.Markdown("Upload one or more PDF files to get started."
                        "The app will ingest, extract, embed, and chunk them for search.")
            upload_box = gr.File(label="Drag & Drop Files Here", file_types=[".pdf"], file_count="multiple")
            ingest_button = gr.Button("Ingest Files", variant='primary')
            ingest_status = gr.Textbox(label="Status", lines=4, interactive=False)
            reset_button = gr.Button("Clear Documents", variant='stop')

            # TODO Add ingest_button click event to handle file ingestion
            # TODO add reset_button click event to handle clearing

        with gr.Tab("Q & A"):
            gr.Markdown("Ask questions about your uploaded documents."
                        "Answers are based on uploaded materials (RAG).")
            chatbot = gr.Chatbot(label="Research Assistant", height=400)
            with gr.Row():
                question_box = gr.Textbox(label="Your Question", placeholder="e.g What methodologies did the authors use?", scale=5)
                send_button = gr.Button("Send Question", variant='primary', scale=1)
                clear_button = gr.Button("Clear Chat")
            
            # TODO Send button event handling
            # TODO Question box handling
            # TODO Clear button event handling
    
    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)