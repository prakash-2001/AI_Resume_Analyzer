from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

from prompts.resume_prompt import RESUME_ANALYSIS_PROMPT


DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def analyze_resume_with_huggingface(
    resume_text: str,
    hf_token: str,
    model: str = DEFAULT_MODEL,
) -> str:
    """Send resume text to Hugging Face and return improvement suggestions."""
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not hf_token.strip():
        raise ValueError("Hugging Face token is missing.")

    client = InferenceClient(
        model=model,
        provider="auto",
        token=hf_token,
        timeout=60,
    )

    messages = [
        {"role": "system", "content": RESUME_ANALYSIS_PROMPT},
        {"role": "user", "content": resume_text},
    ]

    try:
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=1200,
            temperature=0.3,
        )
    except HfHubHTTPError as error:
        error_text = str(error)

        if "401" in error_text or "Unauthorized" in error_text:
            raise RuntimeError(
                "Your Hugging Face token is invalid or missing required access. "
                "Create a new token and update .streamlit/secrets.toml."
            ) from error

        if "403" in error_text or "Forbidden" in error_text:
            raise RuntimeError(
                "Your Hugging Face token does not have permission to call "
                "Inference Providers. Create a fine-grained token with the "
                "'Make calls to Inference Providers' permission, then update "
                ".streamlit/secrets.toml."
            ) from error

        if "402" in error_text or "payment" in error_text.lower():
            raise RuntimeError(
                "Your Hugging Face account does not have available inference credits "
                "for this model/provider."
            ) from error

        if "429" in error_text:
            raise RuntimeError(
                "Hugging Face rate limit reached. Wait a minute and try again."
            ) from error

        raise RuntimeError(f"Hugging Face API error: {error}") from error
    except Exception as error:
        raise RuntimeError(f"Could not analyze resume with Hugging Face: {error}") from error

    return response.choices[0].message.content
