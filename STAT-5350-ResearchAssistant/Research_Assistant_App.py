'''
Research_Assistant_App.py

Defines and launches the Gradio web UI, wiring together all tabs and user interactions to the
underlying feature and RAG modules.
'''

# Import required libraries
import rag
import features
import gradio as gr
from config import OPENAI_CHAT_MODEL, USE_OPENAI
from llm import active_embed_model, active_chat_model

# Build App UI
def build_ui()->gr.Blocks:
    backend_label = f"OpenAI ({OPENAI_CHAT_MODEL})" if USE_OPENAI else f"Ollama Chat: {active_chat_model} | Ollama Embeddings: {active_embed_model}"

    # Background UI
    with gr.Blocks(title="Research Paper Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"""
                    # Research Paper Assistant

                    **AI-Powered Summarization, Citation Extraction, and Q/A**

                    Backend: `{backend_label}`
                    """)

        # Upload Documents UI tab
        with gr.Tab("Upload Documents"):
            gr.Markdown("Upload one or more PDF files to get started."
                        " The app will ingest, extract, embed, and chunk them for search.")
            upload_box = gr.File(label="Drag & Drop Files Here", file_types=[".pdf"], file_count="multiple")
            ingest_button = gr.Button("Ingest Files", variant='primary')
            ingest_status = gr.Textbox(label="Status", lines=4, interactive=False)
            reset_button = gr.Button("Clear Documents", variant='stop')

            ingest_button.click(fn=lambda files:rag.ingest_documents(files, active_embed_model),
                                inputs=upload_box,
                                outputs=ingest_status,)
            reset_button.click(fn=rag.reset,
                               outputs=ingest_status)


        # Q & A UI tab
        with gr.Tab("Q & A"):
            gr.Markdown("Ask questions about your uploaded documents."
                        " Answers are based on uploaded materials (RAG).")
            chatbot = gr.Chatbot(label="Research Assistant", height=400)
            with gr.Row():
                question_box = gr.Textbox(label="Your Question", placeholder="e.g What methodologies did the authors use?", scale=5)
                send_button = gr.Button("Send Question", variant='primary', scale=1)
                clear_button = gr.Button("Clear Chat")
            
            send_button.click(features.answer_question,
                              inputs=[question_box, chatbot],
                              outputs=[question_box, chatbot])
            question_box.submit(features.answer_question,
                                inputs=[question_box, chatbot],
                                outputs=[question_box, chatbot])
            # TODO Clear button event handling
            clear_button.click(fn=lambda: [],
                               outputs=chatbot)
        
        # Summarization UI tab
        with gr.Tab("Summarize"):
            gr.Markdown("Generate a structured summary (Title/Author/Date/Summary) for each file."
                        " Select a specific file or summarize all at once.")
            with gr.Row():
                document_dropdown = gr.Dropdown(label="Select File", choices=[], interactive=True, scale=4)
                refresh_button = gr.Button("Refresh File List", scale=1)
            with gr.Row():
                summary_one_button = gr.Button("Summarize Selected File", variant='primary')
                summary_all_button = gr.Button("Summarize All Files")
            summary_out = gr.Markdown()

            refresh_button.click(fn=lambda: gr.Dropdown(choices=rag.get_document_list()),
                                 outputs=document_dropdown)
            summary_one_button.click(features.summarize_document,
                                     inputs=document_dropdown,
                                     outputs=summary_out)
            summary_all_button.click(features.summarize_all,
                                     outputs=summary_out)

        # Bibliography UI tab
        with gr.Tab("Create Bibliography"):
            gr.Markdown("Extract citation data and compile into APA 7th edition bibliography."
                        " Download the generated bibliography as a .pdf file.")
            biblio_button = gr.Button("Generate Bibliography")
            biblio_text = gr.Markdown()
            biblio_pdf = gr.File(label="Download Bibliography", visible=True, interactive=False)

            def on_bib_click():
                text, pdf_path = features.create_bibliography()
                if pdf_path:
                    return text, pdf_path
                return text, None
 
            biblio_button.click(fn=on_bib_click, outputs=[biblio_text, biblio_pdf])

    
    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)