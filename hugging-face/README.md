# Hugging Face Library

A collection of small, self‑contained experiments that explore different parts of the Hugging Face ecosystem—from zero‑shot pipelines to multi‑modal apps built with Streamlit. Some modules are polished demonstrations, others are rapid prototypes that may evolve over time.

---

## Current Directory

| Path | What it shows off | Key libraries |
|------|-------------------|---------------|
| `sentiment_pipe_test.py` | One‑liner sentiment analysis with the public **`distilbert‑base‑uncased‑finetuned‑sst‑2-english`** model —just run & print | `transformers` pipeline API :contentReference[oaicite:0]{index=0} |
| `star_classifier.py` | Custom LangChain wrapper around the multilingual **BERT sentiment** model (`nlptown/bert‑base‑multilingual-uncased-sentiment`) plus a simple prompt template | `langchain`, `huggingface_hub` :contentReference[oaicite:1]{index=1} |
| `huggingface_salesforce_imagetext.py` | Minimal CLI script that captions `sample.jpg` with **BLIP‑large** | `transformers` pipeline, `Pillow` :contentReference[oaicite:2]{index=2} |
| `hf_sf_test.py` | Streamlit demo: BLIP caption → T5 summary | `streamlit`, `transformers` :contentReference[oaicite:3]{index=3} |
| `hf_sf_t2.py` | Extended Streamlit app: BLIP caption → T5 summary → image Q‑and‑A powered by **Mistral‑7B‑Instruct** | `streamlit`, `transformers`, GPU optional :contentReference[oaicite:4]{index=4} |
| `hf_sf_t3.py` | Same flow as above but swaps in **Falcon‑7B‑Instruct** for Q‑and‑A | `streamlit`, `transformers` :contentReference[oaicite:5]{index=5} |

---

## Setup

```bash
# 1. Clone & enter
git clone https://github.com/your‑username/hf‑playground.git
cd hf‑playground

# 2. Create env (choose one)
conda create -n hf python=3.11 && conda activate hf
# or
python -m venv .venv && source .venv/bin/activate

# 3. Install core deps
pip install -r requirements.txt   # transformers, streamlit, langchain, pillow, python‑dotenv, etc.

# 4. (Optional) enable GPU / Flash‑Attention / bits‑and‑bytes for faster inference
```

Add a `.env` file or export an environment variable if you need private access tokens:

APIKEY =

---
## Running the Demos

|Demo|Command|
|---|---|
|Sentiment pipeline test|`python sentiment_pipe_test.py`|
|LangChain star classifier|`python star_classifier.py`|
|Caption & summary CLI|`python huggingface_salesforce_imagetext.py`|
|Caption & summary (Streamlit)|`streamlit run hf_sf_test.py`|
|Caption → summary → Q‑A (Mistral)|`streamlit run hf_sf_t2.py`|
|Caption → summary → Q‑A (Falcon)|`streamlit run hf_sf_t3.py`|

---
### License

MIT