import importlib
from app.core.config import settings

# Import google.generativeai dynamically to avoid static import-resolution errors in editors/linters.
try:
    genai = importlib.import_module("google.generativeai")
except ModuleNotFoundError:
    genai = None

# Configure Gemini if the library is available
if genai is not None:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_response(prompt: str) -> str:
    """
    Sends a prompt to Gemini model and returns the generated text.
    """
    if genai is None:
        raise RuntimeError(
            "google.generativeai is not installed; install the package before calling generate_response."
        )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
