import os
import logging
import requests

logger = logging.getLogger(__name__)

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def _generate_rule_based_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """Clinical rule-engine fallback based on standard laboratory reference ranges."""
    observations = []

    # Fasting Glucose evaluation (mg/dL)
    if glucose < 70:
        observations.append(f"Low blood glucose ({glucose} mg/dL) indicating hypoglycemia risk.")
    elif 70 <= glucose <= 99:
        observations.append(f"Normal fasting glucose ({glucose} mg/dL).")
    elif 100 <= glucose <= 125:
        observations.append(f"Elevated fasting glucose ({glucose} mg/dL) indicating impaired glucose tolerance (pre-diabetes range).")
    else:
        observations.append(f"High blood glucose ({glucose} mg/dL) in diabetic hyperglycemia range.")

    # Haemoglobin evaluation (g/dL)
    if haemoglobin < 12.0:
        observations.append(f"Low haemoglobin ({haemoglobin} g/dL) suggestive of anemia.")
    elif 12.0 <= haemoglobin <= 17.5:
        observations.append(f"Normal haemoglobin levels ({haemoglobin} g/dL).")
    else:
        observations.append(f"Elevated haemoglobin ({haemoglobin} g/dL) suggestive of hemoconcentration or polycythemia.")

    # Total Cholesterol evaluation (mg/dL)
    if cholesterol < 200:
        observations.append(f"Desirable total cholesterol ({cholesterol} mg/dL).")
    elif 200 <= cholesterol <= 239:
        observations.append(f"Borderline elevated total cholesterol ({cholesterol} mg/dL).")
    else:
        observations.append(f"High total cholesterol ({cholesterol} mg/dL) associated with elevated cardiovascular risk.")

    has_abnormalities = (
        glucose < 70 or glucose >= 100 or
        haemoglobin < 12.0 or haemoglobin > 17.5 or
        cholesterol >= 200
    )

    if not has_abnormalities:
        return (
            f"All biomarker parameters (Glucose: {glucose} mg/dL, Haemoglobin: {haemoglobin} g/dL, "
            f"Cholesterol: {cholesterol} mg/dL) are within optimal clinical reference ranges. "
            f"Continue routine monitoring and healthy lifestyle practices."
        )

    summary_text = " ".join(observations)
    recommendation = (
        " Dietary modifications, cardiovascular risk assessment, and clinical consultation "
        "are recommended for abnormal values."
    )
    return summary_text + recommendation


def generate_biomarker_remarks(glucose: float, haemoglobin: float, cholesterol: float) -> str:
    """Generates clinical remarks using Groq AI (llama-3.1-8b-instant) with rule-engine fallback."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        logger.info("GROQ_API_KEY not set. Using clinical rule-engine fallback.")
        return _generate_rule_based_remarks(glucose, haemoglobin, cholesterol)

    prompt = (
        f"Patient Lab Biomarkers:\n"
        f"- Fasting Glucose: {glucose} mg/dL (Normal: 70-99 mg/dL)\n"
        f"- Haemoglobin: {haemoglobin} g/dL (Normal: 12.0-17.5 g/dL)\n"
        f"- Total Cholesterol: {cholesterol} mg/dL (Desirable: <200 mg/dL)\n\n"
        f"Provide a concise clinical interpretation (2 to 3 sentences). "
        f"State which values are normal or abnormal, potential clinical implications, and general guidance."
    )

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert clinical medical analyst. Provide concise, professional, "
                    "objective laboratory evaluation summaries without preamble. Do not hallucinate."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 160,
    }

    try:
        response = requests.post(
            GROQ_ENDPOINT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=8,
        )

        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if content:
                return content
            logger.warning("Empty response from Groq API. Falling back to rule-engine.")
        else:
            logger.warning(
                f"Groq API returned status {response.status_code}: {response.text}. Using rule-engine fallback."
            )
    except Exception as exc:
        logger.warning(f"Error calling Groq API ({exc}). Using clinical rule-engine fallback.")

    return _generate_rule_based_remarks(glucose, haemoglobin, cholesterol)
