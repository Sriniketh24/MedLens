#!/usr/bin/env python3
"""Generate a labeled evaluation set using MeSH term overlap for relevance."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from supabase import create_client

EVAL_QUERIES = [
    {"query": "What are first-line treatments for community-acquired pneumonia in children?", "mesh_terms": ["pneumonia", "pediatric", "treatment", "antibiotic"]},
    {"query": "How effective is chest CT compared to X-ray for lung cancer screening?", "mesh_terms": ["lung cancer", "screening", "CT", "chest radiograph"]},
    {"query": "What is the role of corticosteroids in acute respiratory distress syndrome?", "mesh_terms": ["corticosteroids", "ARDS", "respiratory distress", "treatment"]},
    {"query": "What are the diagnostic criteria for tuberculosis using imaging?", "mesh_terms": ["tuberculosis", "diagnosis", "imaging", "chest"]},
    {"query": "How does deep learning compare to radiologists in detecting pneumonia?", "mesh_terms": ["deep learning", "pneumonia", "detection", "radiology"]},
    {"query": "What are the current guidelines for hypertension management in adults?", "mesh_terms": ["hypertension", "management", "guidelines", "treatment"]},
    {"query": "What biomarkers predict severity in COVID-19 patients?", "mesh_terms": ["COVID-19", "biomarkers", "severity", "prognosis"]},
    {"query": "How effective is mammography screening for early breast cancer detection?", "mesh_terms": ["mammography", "breast cancer", "screening", "detection"]},
    {"query": "What are the mechanisms of antibiotic resistance in gram-negative bacteria?", "mesh_terms": ["antibiotic resistance", "gram-negative", "mechanisms"]},
    {"query": "What imaging findings differentiate viral from bacterial pneumonia?", "mesh_terms": ["viral pneumonia", "bacterial pneumonia", "imaging", "differentiate"]},
    {"query": "How does echocardiography aid in diagnosing heart failure?", "mesh_terms": ["echocardiography", "heart failure", "diagnosis"]},
    {"query": "What is the sensitivity of MRI for detecting acute stroke?", "mesh_terms": ["MRI", "stroke", "sensitivity", "detection"]},
    {"query": "What are the side effects of metformin in type 2 diabetes management?", "mesh_terms": ["metformin", "diabetes", "side effects"]},
    {"query": "How does COPD exacerbation management differ from stable COPD?", "mesh_terms": ["COPD", "exacerbation", "management", "treatment"]},
    {"query": "What machine learning approaches are used for medical image segmentation?", "mesh_terms": ["machine learning", "segmentation", "medical image"]},
    {"query": "What are the risk factors for nosocomial pneumonia?", "mesh_terms": ["nosocomial", "pneumonia", "risk factors", "hospital"]},
    {"query": "How does pulmonary rehabilitation improve outcomes in COPD?", "mesh_terms": ["pulmonary rehabilitation", "COPD", "outcomes"]},
    {"query": "What is the accuracy of AI-based diabetic retinopathy screening?", "mesh_terms": ["AI", "diabetic retinopathy", "screening", "accuracy"]},
    {"query": "What are the indications for bronchoscopy in pneumonia?", "mesh_terms": ["bronchoscopy", "pneumonia", "indications"]},
    {"query": "How effective are vaccines at preventing pneumococcal pneumonia?", "mesh_terms": ["vaccine", "pneumococcal", "pneumonia", "prevention"]},
    {"query": "What neuroimaging markers predict Alzheimer's disease progression?", "mesh_terms": ["neuroimaging", "Alzheimer", "progression", "markers"]},
    {"query": "What are optimal ventilator settings for ARDS patients?", "mesh_terms": ["ventilator", "ARDS", "settings", "mechanical ventilation"]},
    {"query": "How does cardiac MRI compare to echocardiography for valve assessment?", "mesh_terms": ["cardiac MRI", "echocardiography", "valve"]},
    {"query": "What are the radiological features of COVID-19 pneumonia?", "mesh_terms": ["COVID-19", "radiological", "features", "pneumonia"]},
    {"query": "What is the role of PCT (procalcitonin) in guiding antibiotic therapy?", "mesh_terms": ["procalcitonin", "antibiotic", "therapy", "guide"]},
    {"query": "How does transfer learning improve medical image classification?", "mesh_terms": ["transfer learning", "medical image", "classification"]},
    {"query": "What are the long-term outcomes of statin therapy for cardiovascular disease?", "mesh_terms": ["statin", "cardiovascular", "outcomes", "long-term"]},
    {"query": "What is the diagnostic accuracy of point-of-care ultrasound for pneumothorax?", "mesh_terms": ["ultrasound", "pneumothorax", "diagnostic accuracy"]},
    {"query": "How do convolutional neural networks detect nodules on chest CT?", "mesh_terms": ["CNN", "nodules", "chest CT", "detection"]},
    {"query": "What are evidence-based approaches to sepsis management?", "mesh_terms": ["sepsis", "management", "evidence-based", "treatment"]},
    {"query": "What is the role of PET-CT in staging lung cancer?", "mesh_terms": ["PET-CT", "staging", "lung cancer"]},
    {"query": "How effective is non-invasive ventilation for acute respiratory failure?", "mesh_terms": ["non-invasive ventilation", "respiratory failure", "acute"]},
    {"query": "What are the imaging characteristics of pulmonary embolism?", "mesh_terms": ["imaging", "pulmonary embolism", "characteristics"]},
    {"query": "How do randomized trials compare surgery vs radiation for early lung cancer?", "mesh_terms": ["surgery", "radiation", "lung cancer", "randomized"]},
    {"query": "What is the role of artificial intelligence in pathology?", "mesh_terms": ["artificial intelligence", "pathology", "digital"]},
    {"query": "What antibiotic regimens are recommended for multidrug-resistant TB?", "mesh_terms": ["antibiotic", "multidrug-resistant", "tuberculosis"]},
    {"query": "How does sleep apnea affect cardiovascular risk?", "mesh_terms": ["sleep apnea", "cardiovascular", "risk"]},
    {"query": "What are the benefits of early mobilization in ICU patients?", "mesh_terms": ["early mobilization", "ICU", "outcomes"]},
    {"query": "What is the accuracy of CXR for detecting pleural effusion?", "mesh_terms": ["chest X-ray", "pleural effusion", "accuracy", "detection"]},
    {"query": "How do GLP-1 receptor agonists compare to insulin for type 2 diabetes?", "mesh_terms": ["GLP-1", "insulin", "diabetes", "comparison"]},
    {"query": "What are the complications of mechanical ventilation in neonates?", "mesh_terms": ["mechanical ventilation", "neonates", "complications"]},
    {"query": "How effective is immunotherapy for advanced non-small cell lung cancer?", "mesh_terms": ["immunotherapy", "lung cancer", "non-small cell"]},
    {"query": "What are the radiological signs of congestive heart failure?", "mesh_terms": ["radiological", "congestive heart failure", "signs"]},
    {"query": "How does federated learning address privacy in healthcare AI?", "mesh_terms": ["federated learning", "privacy", "healthcare", "AI"]},
    {"query": "What is the role of bronchodilators in managing asthma exacerbations?", "mesh_terms": ["bronchodilators", "asthma", "exacerbation"]},
    {"query": "What are the predictors of mortality in ICU pneumonia patients?", "mesh_terms": ["predictors", "mortality", "ICU", "pneumonia"]},
    {"query": "How does contrast-enhanced CT improve detection of liver metastases?", "mesh_terms": ["contrast-enhanced", "CT", "liver metastases", "detection"]},
    {"query": "What are the effects of smoking cessation on lung function recovery?", "mesh_terms": ["smoking cessation", "lung function", "recovery"]},
    {"query": "How accurate are rapid antigen tests for influenza diagnosis?", "mesh_terms": ["rapid antigen", "influenza", "diagnosis", "accuracy"]},
    {"query": "What is the evidence for prone positioning in severe ARDS?", "mesh_terms": ["prone positioning", "ARDS", "severe", "evidence"]},
]


def label_relevance(paper_title: str, paper_abstract: str, mesh_terms: list[str]) -> bool:
    """Simple MeSH-overlap relevance labeling."""
    text = (paper_title + " " + paper_abstract).lower()
    matches = sum(1 for term in mesh_terms if term.lower() in text)
    return matches >= 2


def main():
    settings = get_settings()
    client = create_client(settings.supabase_url, settings.supabase_key)

    eval_set = []

    for item in EVAL_QUERIES:
        query = item["query"]
        mesh_terms = item["mesh_terms"]

        result = client.table("papers").select("pmid, title, abstract").limit(200).execute()
        papers = result.data or []

        relevant_pmids = []
        for paper in papers:
            if label_relevance(paper["title"], paper["abstract"], mesh_terms):
                relevant_pmids.append(paper["pmid"])

        eval_set.append({
            "query": query,
            "mesh_terms": mesh_terms,
            "relevant_pmids": relevant_pmids,
            "num_relevant": len(relevant_pmids),
        })

    output_path = Path(__file__).parent.parent / "eval_set.json"
    with open(output_path, "w") as f:
        json.dump(eval_set, f, indent=2)

    total_relevant = sum(item["num_relevant"] for item in eval_set)
    print(f"Generated eval set: {len(eval_set)} queries, {total_relevant} total relevant judgments")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
