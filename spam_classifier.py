import sys
import subprocess
import importlib.util
import urllib.request
import csv
import io
from pathlib import Path

# Automatically install required libraries

required_packages = {
"pandas": "pandas",
"sklearn": "scikit-learn",
"streamlit": "streamlit",
}

for module, package in required_libraries.items():
    if importlib.util.find_spec(module) is None:
        # Existing code inside this if statement should be indented here
print(f"Installing {package}...")
subprocess.check_call(
[sys.executable, "-m", "pip", "install", package]
)

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import joblib

Project files are saved beside this Python file

BASE_DIR = Path(file).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

DATA_FILE = DATA_DIR / "spam.csv"
MODEL_FILE = MODEL_DIR / "spam_model.joblib"

Download a public SMS spam dataset if no dataset exists.

This is an SMS dataset, not a real email dataset.

DATASET_URL = (
"https://raw.githubusercontent.com/"
"justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
)

def download_dataset():
if DATA_FILE.exists():
return

print("Downloading the sample spam dataset...")

try:
    request = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read().decode("utf-8")

    df = pd.read_csv(
        io.StringIO(content),
        sep="\t",
        header=None,
        names=["label", "message"],
    )

    df.to_csv(DATA_FILE, index=False)
    print("Dataset downloaded successfully.")

except Exception as error:
    raise RuntimeError(
        "Dataset download failed. Check your internet connection "
        "or place a labelled CSV file at data/spam.csv. "
        "Supported columns: label/text, category/message, or v1/v2."
    ) from error

def load_dataset():
download_dataset()

df = pd.read_csv(DATA_FILE)
df.columns = [str(col).strip().lower() for col in df.columns]

if {"label", "message"}.issubset(df.columns):
    label_col, text_col = "label", "message"
elif {"category", "message"}.issubset(df.columns):
    label_col, text_col = "category", "message"
elif {"label", "text"}.issubset(df.columns):
    label_col, text_col = "label", "text"
elif {"v1", "v2"}.issubset(df.columns):
    label_col, text_col = "v1", "v2"
else:
    raise ValueError(
        f"Unsupported CSV columns: {list(df.columns)}"
    )

df = df[[label_col, text_col]].copy()
df.columns = ["label", "message"]

df = df.dropna()
df["label"] = df["label"].astype(str).str.strip().str.lower()
df["message"] = df["message"].astype(str).str.strip()

df["label"] = df["label"].replace({
    "ham": "not spam",
    "legitimate": "not spam",
})

df = df[df["label"].isin(["spam", "not spam"])]
df = df[df["message"] != ""]
df = df.drop_duplicates(subset=["message"])

if df["label"].nunique() != 2:
    raise ValueError(
        "Dataset must contain both spam and not spam messages."
    )

return df

@st.cache_resource
def train_or_load_model():
if MODEL_FILE.exists():
try:
return joblib.load(MODEL_FILE)
except Exception:
MODEL_FILE.unlink(missing_ok=True)

df = load_dataset()

X_train, X_test, y_train, y_test = train_test_split(
    df["message"],
    df["label"],
    test_size=0.20,
    random_state=42,
    stratify=df["label"],
)

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            max_features=30000,
        ),
    ),
    ("classifier", MultinomialNB()),
])

model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("\nMODEL EVALUATION")
print("----------------")
print(f"Test accuracy: {accuracy:.2%}")
print(
    classification_report(
        y_t
