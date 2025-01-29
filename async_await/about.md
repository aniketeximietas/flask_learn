Yes, you'll need to install several Python packages. Here's the complete list of pip installations needed for the resume matching system:

```bash
pip install pandas numpy scikit-learn transformers torch PyPDF2 spacy
```

And then you'll need to download the English language model for spaCy:

```bash
python -m spacy download en_core_web_sm
```


optional: if you want to use the BERT model for semantic embeddings, you'll need to install the transformers package:


Additionally, you'll need to install sentence-transformers specifically for the BERT model we're using:

```bash
pip install sentence-transformers
```

I would recommend creating a virtual environment first:

```bash
# Create virtual environment
python -m venv resume_matcher_env

# Activate it (on Windows)
resume_matcher_env\Scripts\activate

# Activate it (on Linux/Mac)
source resume_matcher_env/bin/activate

# Then install the packages
pip install pandas numpy scikit-learn transformers torch PyPDF2 spacy sentence-transformers
python -m spacy download en_core_web_sm
```

This will help keep your dependencies isolated and avoid any conflicts with other Python projects.


THE CODE
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from transformers import AutoTokenizer, AutoModel
import torch
import PyPDF2
import re
import spacy
from typing import List, Tuple, Dict
import logging
import os

class ResumeMatchingSystem:
    def __init__(self):
        # Initialize BERT model for semantic embeddings
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')

        # Initialize Spacy for text processing
        self.nlp = spacy.load('en_core_web_sm')

        # Initialize classifiers
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)

        # Initialize vectorizers
        self.tfidf = TfidfVectorizer(max_features=5000)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return self._preprocess_text(text)
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            return ""

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess extracted text."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        # Remove common stop words while keeping important resume/job terms
        doc = self.nlp(text)
        tokens = [token.text for token in doc if not token.is_stop or token.text in ['experience', 'skills', 'education']]
        return ' '.join(tokens)

    def get_bert_embedding(self, text: str) -> np.ndarray:
        """Generate BERT embeddings for text."""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Use mean pooling of last hidden states
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.numpy()
        except Exception as e:
            self.logger.error(f"Error generating BERT embeddings: {str(e)}")
            return np.zeros((1, 768))  # Return zero vector if error occurs

    def create_feature_vector(self, resume_text: str, jd_text: str, fit_tfidf: bool = False) -> np.ndarray:
        """Create combined feature vector from resume and job description."""
        # Get BERT embeddings
        resume_embedding = self.get_bert_embedding(resume_text)
        jd_embedding = self.get_bert_embedding(jd_text)

        # Get TF-IDF features
        combined_text = f"{resume_text} {jd_text}"
        if fit_tfidf:
            tfidf_features = self.tfidf.fit_transform([combined_text]).toarray()
        else:
            tfidf_features = self.tfidf.transform([combined_text]).toarray()

        # Calculate cosine similarity between resume and JD embeddings
        similarity = np.dot(resume_embedding, jd_embedding.T) / (
            np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding)
        )

        # Combine all features
        return np.concatenate([
            resume_embedding.flatten(),
            jd_embedding.flatten(),
            tfidf_features.flatten(),
            similarity.flatten()
        ])

    def train(self, resume_paths: List[str], jd_paths: List[str], labels: List[int]):
        """Train the model using historical data."""
        self.logger.info("Starting model training...")

        # Validate inputs and log training data structure
        self.logger.info(f"Training with {len(resume_paths)} resume-JD pairs")
        self.logger.info(f"Unique JDs: {len(set(jd_paths))}")
        self.logger.info(f"Label distribution: {np.unique(labels, return_counts=True)}")

        # Extract text from all PDFs
        resume_texts = []
        jd_texts = []

        for i, (resume_path, jd_path) in enumerate(zip(resume_paths, jd_paths)):
            resume_text = self.extract_text_from_pdf(resume_path)
            jd_text = self.extract_text_from_pdf(jd_path)

            self.logger.info(f"\nPair {i+1}:")
            self.logger.info(f"Resume: {os.path.basename(resume_path)}")
            self.logger.info(f"JD: {os.path.basename(jd_path)}")
            self.logger.info(f"Label: {labels[i]}")
            self.logger.info(f"Resume text length: {len(resume_text)}")
            self.logger.info(f"JD text length: {len(jd_text)}")

            resume_texts.append(resume_text)
            jd_texts.append(jd_text)

        # First, fit TF-IDF on all combined texts
        all_combined_texts = [f"{resume_text} {jd_text}"
                            for resume_text, jd_text in zip(resume_texts, jd_texts)]
        self.tfidf.fit(all_combined_texts)

        # Create feature vectors and log dimensions
        X = np.vstack([
            self.create_feature_vector(resume_text, jd_text, fit_tfidf=False)
            for resume_text, jd_text in zip(resume_texts, jd_texts)
        ])

        self.logger.info(f"\nFeature vector shape: {X.shape}")

        # Split with stratification to maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels,
            test_size=0.2,
            random_state=42,
            stratify=labels if len(np.unique(labels)) > 1 else None
        )

        # Train classifier with class weight adjustment
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            class_weight='balanced',
            random_state=42
        )
        self.classifier.fit(X_train, y_train)

        # Evaluate and log detailed metrics
        train_score = self.classifier.score(X_train, y_train)
        test_score = self.classifier.score(X_test, y_test)

        self.logger.info(f"\nTraining complete:")
        self.logger.info(f"Train accuracy: {train_score:.3f}")
        self.logger.info(f"Test accuracy: {test_score:.3f}")

        # Log feature importances
        if hasattr(self.classifier, 'feature_importances_'):
            importances = self.classifier.feature_importances_
            self.logger.info(f"\nTop feature importance: {max(importances):.3f}")

        # Extract text from all PDFs
        resume_texts = [self.extract_text_from_pdf(path) for path in resume_paths]
        jd_texts = [self.extract_text_from_pdf(path) for path in jd_paths]

        # First, fit TF-IDF on all combined texts
        all_combined_texts = [f"{resume_text} {jd_text}" for resume_text, jd_text in zip(resume_texts, jd_texts)]
        self.tfidf.fit(all_combined_texts)

        # Create feature vectors for all pairs
        X = np.vstack([
            self.create_feature_vector(resume_text, jd_text, fit_tfidf=False)
            for resume_text, jd_text in zip(resume_texts, jd_texts)
        ])

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

        # Train classifier
        self.classifier.fit(X_train, y_train)

        # Evaluate
        train_score = self.classifier.score(X_train, y_train)
        test_score = self.classifier.score(X_test, y_test)

        self.logger.info(f"Training complete. Train accuracy: {train_score:.3f}, Test accuracy: {test_score:.3f}")

    def predict_match(self, resume_path: str, jd_path: str) -> Tuple[float, Dict[str, float]]:
        """Predict match score for new resume-JD pair."""
        # Extract text
        resume_text = self.extract_text_from_pdf(resume_path)
        jd_text = self.extract_text_from_pdf(jd_path)

        self.logger.info(f"\nPrediction request:")
        self.logger.info(f"Resume: {os.path.basename(resume_path)}")
        self.logger.info(f"JD: {os.path.basename(jd_path)}")

        # Create feature vector
        features = self.create_feature_vector(resume_text, jd_text)

        # Get raw prediction probabilities
        probas = self.classifier.predict_proba([features])[0]
        self.logger.info(f"Raw prediction probabilities: {probas}")

        # Calculate semantic similarity
        resume_emb = self.get_bert_embedding(resume_text).flatten()
        jd_emb = self.get_bert_embedding(jd_text).flatten()
        similarity_score = float(np.dot(resume_emb, jd_emb) / (
            np.linalg.norm(resume_emb) * np.linalg.norm(jd_emb)
        ))

        # Combine model confidence with semantic similarity for final score
        match_probability = float(probas[-1])  # Probability of positive class
        final_score = 0.7 * match_probability + 0.3 * similarity_score  # Weighted combination

        metrics = {
            'model_score': match_probability,
            'semantic_similarity': similarity_score,
            'final_score': final_score,
            'confidence': float(max(probas))
        }

        return final_score, metrics

        metrics = {
            'overall_match_score': match_probability,
            'semantic_similarity': float(similarity_score),
            'confidence': float(np.max(self.classifier.predict_proba([features])))
        }

        return match_probability, metrics



if __name__ == "__main__":
    # Initialize system
    matcher = ResumeMatchingSystem()

    # Base paths
    base_path = "/Users/aniketsahoo/Developer/ofc/resume_score_model/jd"

    # Training data
    resume_paths = [
        os.path.join(base_path, "jd-1/athiya -s.pdf"),
        os.path.join(base_path, "jd-1/harini-r.pdf"),
        os.path.join(base_path, "jd-2/resume (14).pdf"),
        os.path.join(base_path, "jd-1/sharvaree-r.pdf"),
        os.path.join(base_path, "jd-1/sunku-s.pdf"),
        os.path.join(base_path, "jd-2/s1.pdf"),
        os.path.join(base_path, "jd-2/s2.pdf"),
        os.path.join(base_path, "jd-2/s3.pdf"),
        os.path.join(base_path, "jd-2/resume (12).pdf"),
        os.path.join(base_path, "jd-2/resume (13).pdf"),
    ]

    jd_paths = [
        os.path.join(base_path, "jd-1/jd-1.pdf"),
        os.path.join(base_path, "jd-1/jd-1.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
        os.path.join(base_path, "jd-1/jd-1.pdf"),
        os.path.join(base_path, "jd-1/jd-1.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
        os.path.join(base_path, "jd-2/jd-2.pdf"),
    ]

    labels = [1, 0, 0, 0, 1, 1, 1, 1, 0, 0]  # 1 for selected, 0 for rejected

    # Train the system
    matcher.train(resume_paths, jd_paths, labels)

    # Make prediction
    test_resume = os.path.join(base_path, "jd-1/manas-s.pdf")
    test_jd = os.path.join(base_path, "jd-1/jd-1.pdf")

    score, metrics = matcher.predict_match(test_resume, test_jd)

    print("\nPrediction Results:")
    print(f"Final Match Score: {score:.3f}")
    print("\nDetailed Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.3f}")

```
