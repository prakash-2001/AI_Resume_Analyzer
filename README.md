# AI Resume Analyzer

A Streamlit web app that lets users upload a resume PDF, extracts the resume text, and uses a Hugging Face-hosted LLM to generate resume feedback and improvement suggestions.

## Features

- Upload a PDF resume from the browser
- Extract readable text using PyPDF2
- Show resume word and character counts
- Preview extracted resume text
- Analyze the resume using Hugging Face Inference Providers
- Return structured feedback:
  - Overall summary
  - Key strengths
  - Weaknesses or missing details
  - ATS improvement suggestions
  - Skills to add or highlight
  - Improved bullet point examples
  - Final action checklist

## Tech Stack

- Python
- Streamlit
- PyPDF2
- Hugging Face Hub / Inference Providers

## Project Structure

```text
AI_Resume_Analyzer/
|
+-- app.py
+-- requirements.txt
+-- README.md
|
+-- prompts/
|   +-- resume_prompt.py
|
+-- services/
|   +-- huggingface_service.py
|
+-- utils/
|   +-- pdf_reader.py
|
+-- .streamlit/
    +-- secrets.example.toml
    +-- secrets.toml
```

`secrets.toml` stores the private Hugging Face token and is ignored by Git.

## Setup

1. Clone or open the project folder.

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create a Hugging Face token:

Go to:

```text
https://huggingface.co/settings/tokens
```

Create a fine-grained token and enable:

```text
Make calls to Inference Providers
```

4. Create this file:

```text
.streamlit/secrets.toml
```

Add your token:

```toml
HF_TOKEN = "your_hugging_face_token_here"
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
```

Do not commit `secrets.toml`.

## Run Locally

```powershell
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## How It Works

1. User uploads a PDF resume in the Streamlit app.
2. `utils/pdf_reader.py` extracts text from the PDF using PyPDF2.
3. `app.py` displays upload status, resume stats, and extracted text preview.
4. `prompts/resume_prompt.py` defines the resume analysis instructions.
5. `services/huggingface_service.py` sends the resume text to Hugging Face.
6. The model response is displayed in the Analysis section.

## Hugging Face Errors

If you see:

```text
403 Forbidden
```

your token does not have permission to call Inference Providers. Create a new fine-grained token with:

```text
Make calls to Inference Providers
```

If you see:

```text
429
```

you may have hit a rate limit. Wait and try again, or use a different model/provider.

## Deployment On Streamlit Cloud

1. Push the project to GitHub.
2. Deploy the repo on Streamlit Cloud.
3. In Streamlit Cloud app settings, add secrets:

```toml
HF_TOKEN = "your_hugging_face_token_here"
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
```

4. Start the app with:

```text
app.py
```

## Notes

- This app works best with text-based PDFs.
- Scanned image PDFs may return little or no text because OCR is not implemented.
- The resume text and analysis are stored only in the current Streamlit session.
- Keep all API tokens private.
