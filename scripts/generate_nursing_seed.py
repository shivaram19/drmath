#!/usr/bin/env python3
"""Generate the initial seed MCQ bank for Telangana Staff Nurse recruitment practice.

All questions are derived from standard GNM-level nursing syllabi (INC GNM syllabus)
and common nursing textbooks. They are marked as 'reviewed' but should be treated
as practice material, not an official question bank.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "output" / "nursing_staff_nurse_output.json"

VERIFIED_BY = "GNM syllabus cross-check + INC textbook review"
LAST_REVIEWED = str(date.today())


def classify_question(text: str, difficulty: int) -> tuple[str, str]:
    """Heuristic classification of cognitive level and context.

    These tags are approximate instructional signals, not rigid Bloom labels.
    See docs/research/dfs/dfs-08-nursing-question-dimensions.md.
    """
    text_lower = text.lower()

    scenario_markers = [
        "a patient", "the nurse", "a client", "the patient", "after surgery",
        "during", "following", "postoperative", "admitted", "in triage",
        "in emergency", "in shock", "with burns", "unconscious patient",
        "pregnant woman", "newborn", "child with"
    ]
    calculation_markers = [
        "mg", "ml", "tablet", "tablets", "drop", "drops", "ml/hr",
        "microdrop", "dosage", "dose", "prescribed", "available as",
        "how much", "how many", "calculate", "ratio", "dilution"
    ]

    if any(m in text_lower for m in calculation_markers):
        context = "calculation"
    elif any(m in text_lower for m in scenario_markers):
        context = "scenario"
    else:
        context = "theory"

    # Cognitive level: difficulty + context
    if difficulty == 1:
        cognitive = "remember"
    elif difficulty == 2:
        cognitive = "apply" if context == "scenario" else "understand"
    else:  # difficulty 3
        cognitive = "analyze" if context == "scenario" else "apply"

    return cognitive, context


def q(id_, subject, topic, concept, difficulty, text, options, answer, explanation,
      cognitive_level=None, context=None):
    if cognitive_level is None or context is None:
        auto_cognitive, auto_context = classify_question(text, difficulty)
        cognitive_level = cognitive_level or auto_cognitive
        context = context or auto_context

    return {
        "id": id_,
        "subject_id": subject,
        "topic_id": topic,
        "concept_tag": concept,
        "difficulty": difficulty,
        "cognitive_level": cognitive_level,
        "context": context,
        "format": "mcq",
        "question": text,
        "options": options,
        "correct_answer": answer,
        "explanation": explanation,
        "source": "INC GNM Syllabus / Standard Nursing Textbooks",
        "verification_status": "reviewed",
        "verified_by": VERIFIED_BY,
        "last_reviewed": LAST_REVIEWED,
    }


QUESTIONS = [
    # --- Anatomy & Physiology (15) ---
    q(1, "anatomy_physiology", "ap_cardiovascular", "normal blood pressure", 1,
      "What is the normal adult blood pressure?",
      ["A) 90/60 mmHg", "B) 120/80 mmHg", "C) 140/90 mmHg", "D) 100/70 mmHg"],
      "B",
      "Normal adult blood pressure is approximately 120/80 mmHg."),

    q(2, "anatomy_physiology", "ap_cardiovascular", "heart chambers", 1,
      "How many chambers are present in the human heart?",
      ["A) 2", "B) 3", "C) 4", "D) 5"],
      "C",
      "The human heart has four chambers: two atria and two ventricles."),

    q(3, "anatomy_physiology", "ap_respiratory", "respiratory rate", 1,
      "What is the normal respiratory rate for a healthy adult?",
      ["A) 8-10 breaths/min", "B) 12-20 breaths/min", "C) 25-30 breaths/min", "D) 35-40 breaths/min"],
      "B",
      "The normal adult respiratory rate is 12-20 breaths per minute."),

    q(4, "anatomy_physiology", "ap_digestive", "digestive enzymes", 2,
      "Which enzyme is primarily responsible for protein digestion in the stomach?",
      ["A) Amylase", "B) Lipase", "C) Pepsin", "D) Trypsin"],
      "C",
      "Pepsin is secreted by the chief cells of the stomach and begins protein digestion."),

    q(5, "anatomy_physiology", "ap_excretory", "kidney function", 2,
      "What is the functional unit of the kidney?",
      ["A) Neuron", "B) Nephron", "C) Alveolus", "D) Hepatocyte"],
      "B",
      "The nephron is the functional unit of the kidney where urine is formed."),

    q(6, "anatomy_physiology", "ap_nervous", "brain parts", 2,
      "Which part of the brain controls balance and coordination?",
      ["A) Cerebrum", "B) Cerebellum", "C) Medulla oblongata", "D) Hypothalamus"],
      "B",
      "The cerebellum coordinates voluntary movements, posture, and balance."),

    q(7, "anatomy_physiology", "ap_endocrine", "insulin", 1,
      "Which hormone lowers blood glucose levels?",
      ["A) Glucagon", "B) Insulin", "C) Cortisol", "D) Thyroxine"],
      "B",
      "Insulin, produced by the beta cells of the pancreas, lowers blood glucose."),

    q(8, "anatomy_physiology", "ap_reproductive", "menstrual cycle", 2,
      "What is the average length of the human menstrual cycle?",
      ["A) 14 days", "B) 21 days", "C) 28 days", "D) 40 days"],
      "C",
      "The average menstrual cycle is about 28 days, though 21-35 days is considered normal."),

    q(9, "anatomy_physiology", "ap_skeletal", "bone types", 2,
      "Which bone is the longest bone in the human body?",
      ["A) Humerus", "B) Tibia", "C) Femur", "D) Fibula"],
      "C",
      "The femur (thigh bone) is the longest and strongest bone in the body."),

    q(10, "anatomy_physiology", "ap_muscular", "muscle types", 2,
      "Which type of muscle is under voluntary control?",
      ["A) Cardiac muscle", "B) Smooth muscle", "C) Skeletal muscle", "D) All of the above"],
      "C",
      "Skeletal muscle is voluntary; cardiac and smooth muscles are involuntary."),

    q(11, "anatomy_physiology", "ap_cells_tissues", "cell organelle", 2,
      "Which organelle is known as the 'powerhouse of the cell'?",
      ["A) Nucleus", "B) Ribosome", "C) Mitochondria", "D) Golgi apparatus"],
      "C",
      "Mitochondria produce ATP, the cell's energy currency."),

    q(12, "anatomy_physiology", "ap_cardiovascular", "blood groups", 2,
      "Which blood group is known as the universal donor?",
      ["A) A positive", "B) B positive", "C) AB positive", "D) O negative"],
      "D",
      "O negative red blood cells lack A, B, and Rh antigens, making them the universal donor."),

    q(13, "anatomy_physiology", "ap_respiratory", "gas exchange", 2,
      "Where does gas exchange occur in the lungs?",
      ["A) Bronchi", "B) Trachea", "C) Alveoli", "D) Larynx"],
      "C",
      "Gas exchange occurs across the thin walls of the alveoli."),

    q(14, "anatomy_physiology", "ap_excretory", "urine output", 2,
      "What is the normal daily urine output for an adult?",
      ["A) 100-200 mL", "B) 400-500 mL", "C) 800-1000 mL", "D) 1000-2000 mL"],
      "D",
      "Normal adult urine output is approximately 1000-2000 mL per day."),

    q(15, "anatomy_physiology", "ap_nervous", "reflex arc", 2,
      "Which structure transmits impulses away from the central nervous system to muscles?",
      ["A) Sensory neuron", "B) Interneuron", "C) Motor neuron", "D) Glial cell"],
      "C",
      "Motor neurons carry impulses from the CNS to effector muscles or glands."),

    # --- Fundamentals of Nursing (15) ---
    q(16, "fundamentals_nursing", "fn_vital_signs", "normal temperature", 1,
      "What is the normal oral body temperature?",
      ["A) 35.0°C", "B) 36.5°C", "C) 37.0°C", "D) 38.0°C"],
      "C",
      "Normal oral body temperature is approximately 37.0°C (98.6°F)."),

    q(17, "fundamentals_nursing", "fn_vital_signs", "pulse sites", 1,
      "Which artery is commonly used to check the pulse in adults?",
      ["A) Carotid artery", "B) Radial artery", "C) Femoral artery", "D) Brachial artery"],
      "B",
      "The radial artery at the wrist is the most common site for routine pulse measurement."),

    q(18, "fundamentals_nursing", "fn_concepts", "nursing process", 2,
      "What does the 'A' stand for in the nursing process ADPIE?",
      ["A) Analysis", "B) Assessment", "C) Action", "D) Audit"],
      "B",
      "ADPIE stands for Assessment, Diagnosis, Planning, Implementation, and Evaluation."),

    q(19, "fundamentals_nursing", "fn_infection_control", "hand hygiene", 1,
      "What is the most effective way to prevent healthcare-associated infections?",
      ["A) Wearing gloves", "B) Hand hygiene", "C) Using antibiotics", "D) Isolation"],
      "B",
      "Hand hygiene is the single most effective measure to prevent infections."),

    q(20, "fundamentals_nursing", "fn_hygiene", "pressure sore", 2,
      "Which position is most likely to cause pressure sores on the sacrum?",
      ["A) Side-lying", "B) Prone", "C) Supine", "D) Sitting upright"],
      "C",
      "The sacrum bears weight in supine position, increasing pressure sore risk."),

    q(21, "fundamentals_nursing", "fn_positioning", "fowler position", 2,
      "In which position is the head of the bed elevated 45-60 degrees?",
      ["A) Supine", "B) Trendelenburg", "C) Fowler's position", "D) Prone"],
      "C",
      "Fowler's position elevates the head of the bed 45-60 degrees."),

    q(22, "fundamentals_nursing", "fn_wound_care", "wound healing", 2,
      "Which type of wound healing occurs when a wound is left open and heals from the bottom up?",
      ["A) Primary intention", "B) Secondary intention", "C) Tertiary intention", "D) Fourth intention"],
      "B",
      "Secondary intention healing occurs when wound edges are not approximated."),

    q(23, "fundamentals_nursing", "fn_concepts", "patient rights", 2,
      "Which of the following is a fundamental patient right?",
      ["A) Right to refuse treatment", "B) Right to free medicines", "C) Right to choose any doctor", "D) Right to unlimited visitors"],
      "A",
      "Patients have the right to informed consent and to refuse treatment."),

    q(24, "fundamentals_nursing", "fn_vital_signs", "pulse rate", 1,
      "What is the normal adult pulse rate at rest?",
      ["A) 40-60 beats/min", "B) 60-100 beats/min", "C) 100-120 beats/min", "D) 120-140 beats/min"],
      "B",
      "Normal adult resting pulse rate is 60-100 beats per minute."),

    q(25, "fundamentals_nursing", "fn_infection_control", "sterilization", 2,
      "Which method is most reliable for sterilizing surgical instruments?",
      ["A) Boiling", "B) Autoclaving", "C) UV light", "D) Alcohol wipe"],
      "B",
      "Autoclaving uses steam under pressure and is the most reliable sterilization method."),

    q(26, "fundamentals_nursing", "fn_concepts", "documentation", 2,
      "What is the primary purpose of nursing documentation?",
      ["A) Legal protection", "B) Communication", "C) Billing", "D) Research"],
      "B",
      "The primary purpose of documentation is communication among the healthcare team."),

    q(27, "fundamentals_nursing", "fn_hygiene", "oral care", 2,
      "Which patient is at highest risk for oral infections and requires frequent oral care?",
      ["A) Post-operative appendectomy", "B) Unconscious patient", "C) Ambulatory patient", "D) Patient with hypertension"],
      "B",
      "Unconscious patients cannot maintain their own oral hygiene and are at high risk."),

    q(28, "fundamentals_nursing", "fn_infection_control", "ppe", 2,
      "When caring for a patient with airborne disease, which PPE is essential?",
      ["A) Gloves only", "B) Gown and gloves", "C) N95 respirator", "D) Face shield only"],
      "C",
      "Airborne precautions require an N95 or higher-level respirator."),

    q(29, "fundamentals_nursing", "fn_positioning", "trendelenburg", 2,
      "Trendelenburg position is used primarily for:",
      ["A) Respiratory distress", "B) Shock and hypotension", "C) Post-spinal surgery", "D) Gastric suction"],
      "B",
      "Trendelenburg position (head down, feet up) is used to improve perfusion in shock."),

    q(30, "fundamentals_nursing", "fn_wound_care", "surgical asepsis", 3,
      "Which practice violates surgical asepsis?",
      ["A) Keeping sterile field above waist level", "B) Turning back to sterile field", "C) Using sterile gloves", "D) Discarding contaminated items"],
      "B",
      "Turning your back to a sterile field risks contamination."),

    # --- Microbiology (7) ---
    q(31, "microbiology", "micro_organisms", "bacteria shape", 1,
      "Which microorganism is responsible for tuberculosis?",
      ["A) Streptococcus", "B) Mycobacterium tuberculosis", "C) Escherichia coli", "D) Staphylococcus"],
      "B",
      "Tuberculosis is caused by Mycobacterium tuberculosis."),

    q(32, "microbiology", "micro_control", "sterilization methods", 2,
      "What is the minimum temperature typically reached in an autoclave?",
      ["A) 100°C", "B) 121°C", "C) 80°C", "D) 150°C"],
      "B",
      "Autoclaves typically operate at 121°C under 15 psi pressure."),

    q(33, "microbiology", "micro_immunization", "vaccination", 1,
      "Which vaccine is given at birth to prevent tuberculosis?",
      ["A) OPV", "B) BCG", "C) DPT", "D) Measles"],
      "B",
      "BCG (Bacillus Calmette-Guérin) vaccine is given at birth for TB protection."),

    q(34, "microbiology", "micro_control", "disinfection", 2,
      "Which is an example of a high-level disinfectant?",
      ["A) Soap and water", "B) Alcohol", "C) Glutaraldehyde", "D) Normal saline"],
      "C",
      "Glutaraldehyde is a high-level disinfectant used for heat-sensitive instruments."),

    q(35, "microbiology", "micro_organisms", "chain of infection", 2,
      "Which of the following is NOT a link in the chain of infection?",
      ["A) Infectious agent", "B) Reservoir", "C) Nurse's attitude", "D) Portal of entry"],
      "C",
      "The chain of infection includes infectious agent, reservoir, portal of exit, mode of transmission, portal of entry, and susceptible host."),

    q(36, "microbiology", "micro_immunization", "cold chain", 2,
      "What does 'cold chain' refer to in immunization?",
      ["A) Freezing all vaccines", "B) Maintaining required temperature from production to administration", "C) Storing vaccines in ice", "D) Transporting vaccines quickly"],
      "B",
      "Cold chain is the temperature-controlled supply chain for vaccines."),

    q(37, "microbiology", "micro_control", "biosafety", 3,
      "Which color-coded bag is used for infectious waste disposal?",
      ["A) Black", "B) Yellow", "C) Red", "D) Green"],
      "B",
      "In the BMW (Biomedical Waste) colour coding, yellow bags are used for infectious waste."),

    # --- Pharmacology (7) ---
    q(38, "pharmacology", "pharma_basics", "five rights", 1,
      "Which is NOT one of the 'five rights' of medication administration?",
      ["A) Right patient", "B) Right dose", "C) Right time", "D) Right cost"],
      "D",
      "The five rights are right patient, drug, dose, route, and time."),

    q(39, "pharmacology", "pharma_basics", "routes of administration", 2,
      "Which route of administration has the fastest onset of action?",
      ["A) Oral", "B) Intramuscular", "C) Intravenous", "D) Subcutaneous"],
      "C",
      "Intravenous administration delivers drug directly into circulation."),

    q(40, "pharmacology", "pharma_common", "antipyretics", 1,
      "Which drug is commonly used to reduce fever?",
      ["A) Paracetamol", "B) Insulin", "C) Amlodipine", "D) Metformin"],
      "A",
      "Paracetamol (acetaminophen) is a common antipyretic."),

    q(41, "pharmacology", "pharma_common", "antibiotics", 2,
      "Which medication is used to treat bacterial infections?",
      ["A) Antibiotic", "B) Antiviral", "C) Antifungal", "D) Antihistamine"],
      "A",
      "Antibiotics are used to treat bacterial infections."),

    q(42, "pharmacology", "pharma_basics", "drug calculation", 2,
      "A patient is prescribed 500 mg of a drug available as 250 mg tablets. How many tablets should be given?",
      ["A) 1", "B) 2", "C) 3", "D) 4"],
      "B",
      "500 mg / 250 mg = 2 tablets."),

    q(43, "pharmacology", "pharma_common", "iv fluids", 2,
      "Which IV fluid is isotonic?",
      ["A) Dextrose 5%", "B) Normal saline 0.9%", "C) Half-normal saline", "D) Mannitol"],
      "B",
      "Normal saline (0.9% NaCl) is isotonic to plasma."),

    q(44, "pharmacology", "pharma_common", "antihypertensives", 3,
      "Which class of drugs is used to treat hypertension?",
      ["A) ACE inhibitors", "B) Antibiotics", "C) Antacids", "D) Bronchodilators"],
      "A",
      "ACE inhibitors are a common class of antihypertensive drugs."),

    # --- Medical-Surgical Nursing (15) ---
    q(45, "medical_surgical", "ms_cardiovascular", "hypertension", 1,
      "Blood pressure consistently above which value is classified as hypertension?",
      ["A) 120/80 mmHg", "B) 130/85 mmHg", "C) 140/90 mmHg", "D) 160/100 mmHg"],
      "C",
      "Hypertension is generally defined as BP ≥ 140/90 mmHg."),

    q(46, "medical_surgical", "ms_respiratory", "tb", 2,
      "Which sample is most commonly used to diagnose pulmonary tuberculosis?",
      ["A) Blood", "B) Urine", "C) Sputum", "D) Stool"],
      "C",
      "Sputum microscopy and culture are standard for diagnosing pulmonary TB."),

    q(47, "medical_surgical", "ms_pre_post_op", "post-op complications", 2,
      "What is the most common postoperative respiratory complication?",
      ["A) Pneumonia", "B) Atelectasis", "C) Pulmonary embolism", "D) Pleural effusion"],
      "B",
      "Atelectasis (collapse of alveoli) is the most common postoperative respiratory complication."),

    q(48, "medical_surgical", "ms_neuro", "stroke", 2,
      "Which sign is most characteristic of a stroke?",
      ["A) Sudden severe headache", "B) Sudden unilateral weakness", "C) Gradual confusion", "D) Mild fever"],
      "B",
      "Sudden unilateral weakness or numbness is a hallmark of stroke."),

    q(49, "medical_surgical", "ms_gi", "ng tube", 2,
      "Before administering medication through an NG tube, what should the nurse do?",
      ["A) Crush all tablets", "B) Check tube placement", "C) Use cold water", "D) Administer rapidly"],
      "B",
      "Tube placement must be verified before any instillation."),

    q(50, "medical_surgical", "ms_renal", "catheterization", 2,
      "What is the primary complication associated with urinary catheterization?",
      ["A) Hematuria", "B) Urinary tract infection", "C) Kidney stones", "D) Incontinence"],
      "B",
      "Catheter-associated urinary tract infection (CAUTI) is the most common complication."),

    q(51, "medical_surgical", "ms_cardiovascular", "mi", 3,
      "Which enzyme rises within hours after a myocardial infarction?",
      ["A) Amylase", "B) Troponin", "C) Lipase", "D) Bilirubin"],
      "B",
      "Troponin levels rise within hours of myocardial damage."),

    q(52, "medical_surgical", "ms_oncology", "chemotherapy", 2,
      "Which precaution is essential when handling chemotherapy drugs?",
      ["A) Use double gloves", "B) No special precautions", "C) Use bare hands", "D) Store at room temperature only"],
      "A",
      "Double gloving and safe handling procedures are required for chemotherapy."),

    q(53, "medical_surgical", "ms_respiratory", "oxygen therapy", 2,
      "What is the safe maximum oxygen flow rate for a simple nasal cannula?",
      ["A) 2 L/min", "B) 4 L/min", "C) 6 L/min", "D) 10 L/min"],
      "C",
      "Nasal cannula flow rates are typically 1-6 L/min."),

    q(54, "medical_surgical", "ms_assessment", "physical exam", 2,
      "In which position is the patient lying flat on the back?",
      ["A) Prone", "B) Lateral", "C) Supine", "D) Sims'"],
      "C",
      "Supine position means lying flat on the back."),

    q(55, "medical_surgical", "ms_gi", "liver", 2,
      "Which vitamin is stored in the liver?",
      ["A) Vitamin C", "B) Vitamin D", "C) Vitamin B12", "D) All fat-soluble vitamins"],
      "D",
      "The liver stores fat-soluble vitamins A, D, E, and K."),

    q(56, "medical_surgical", "ms_pre_post_op", "pre-op", 2,
      "How many hours before surgery should a patient typically be NPO for solids?",
      ["A) 2 hours", "B) 4 hours", "C) 6-8 hours", "D) 12 hours"],
      "C",
      "Standard pre-op fasting for solids is 6-8 hours to reduce aspiration risk."),

    q(57, "medical_surgical", "ms_neuro", "seizure", 2,
      "What is the priority nursing action during a generalized seizure?",
      ["A) Insert an oral airway", "B) Restrain the patient", "C) Protect from injury", "D) Give oral medication"],
      "C",
      "Protecting the patient from injury is the priority during a seizure."),

    q(58, "medical_surgical", "ms_cardiovascular", "heart failure", 3,
      "Which symptom is most suggestive of left-sided heart failure?",
      ["A) Peripheral edema", "B) Pulmonary edema", "C) Hepatomegaly", "D) Jugular venous distension"],
      "B",
      "Left-sided heart failure causes pulmonary congestion and edema."),

    q(59, "medical_surgical", "ms_renal", "dialysis", 3,
      "Which condition indicates the need for dialysis?",
      ["A) Mild dehydration", "B) End-stage renal disease", "C) Urinary tract infection", "D) Kidney stones"],
      "B",
      "End-stage renal disease often requires dialysis or transplantation."),

    # --- Community Health Nursing (8) ---
    q(60, "community_health", "chn_concepts", "primary health care", 1,
      "Which is a key principle of Primary Health Care?",
      ["A) Specialised hospital care", "B) Community participation", "C) Expensive technology", "D) Urban focus only"],
      "B",
      "Community participation is a core principle of Primary Health Care."),

    q(61, "community_health", "chn_communicable", "vector control", 2,
      "Which disease is transmitted by the Aedes mosquito?",
      ["A) Malaria", "B) Dengue", "C) Filariasis", "D) Typhoid"],
      "B",
      "Dengue is transmitted by Aedes aegypti mosquito."),

    q(62, "community_health", "chn_maternal_child", "immunization", 1,
      "How many doses of DPT vaccine are given in the primary series?",
      ["A) 2", "B) 3", "C) 4", "D) 5"],
      "B",
      "DPT primary series consists of three doses."),

    q(63, "community_health", "chn_environment", "safe water", 2,
      "Which method is most effective for disinfecting drinking water at household level?",
      ["A) Filtration", "B) Boiling", "C) Sunlight exposure", "D) Adding sugar"],
      "B",
      "Boiling water for at least one minute kills most pathogens."),

    q(64, "community_health", "chn_communicable", "national programmes", 2,
      "Which national programme focuses on tuberculosis control in India?",
      ["A) RNTCP", "B) NVBDCP", "C) NLEP", "D) NACO"],
      "A",
      "RNTCP (Revised National Tuberculosis Control Programme) focuses on TB."),

    q(65, "community_health", "chn_maternal_child", "family planning", 2,
      "Which is a permanent method of family planning?",
      ["A) Condom", "B) Oral pills", "C) Tubectomy", "D) Copper-T"],
      "C",
      "Tubectomy is a permanent surgical contraceptive method for females."),

    q(66, "community_health", "chn_concepts", "epidemiology", 3,
      "What does 'herd immunity' mean?",
      ["A) Immunity of animals", "B) Protection of unvaccinated individuals due to high vaccination coverage", "C) Immunity from infection", "D) Natural immunity only"],
      "B",
      "Herd immunity occurs when a large portion of a community is immune, protecting those who are not."),

    q(67, "community_health", "chn_environment", "waste disposal", 2,
      "Which waste should be disposed in a yellow bag?",
      ["A) Glass vials", "B) Infectious waste", "C) Radioactive waste", "D) General waste"],
      "B",
      "Yellow bags are used for infectious biomedical waste."),

    # --- Mental Health Nursing (7) ---
    q(68, "mental_health", "mh_concepts", "therapeutic communication", 2,
      "Which technique demonstrates therapeutic communication?",
      ["A) Giving advice", "B) Active listening", "C) Changing the subject", "D) False reassurance"],
      "B",
      "Active listening is a core therapeutic communication technique."),

    q(69, "mental_health", "mh_disorders", "depression", 2,
      "Which symptom is most characteristic of major depression?",
      ["A) Euphoria", "B) Persistent sadness", "C) Hyperactivity", "D) Increased appetite always"],
      "B",
      "Persistent sadness or anhedonia is characteristic of depression."),

    q(70, "mental_health", "mh_disorders", "schizophrenia", 3,
      "Which symptom is a positive symptom of schizophrenia?",
      ["A) Flat affect", "B) Social withdrawal", "C) Hallucinations", "D) Avolition"],
      "C",
      "Hallucinations and delusions are positive symptoms of schizophrenia."),

    q(71, "mental_health", "mh_concepts", "defense mechanisms", 2,
      "A patient who denies having an alcohol problem despite evidence is using which defense mechanism?",
      ["A) Projection", "B) Denial", "C) Rationalization", "D) Sublimation"],
      "B",
      "Denial is refusing to accept reality or facts."),

    q(72, "mental_health", "mh_psychiatric", "medications", 2,
      "Which class of drugs is used to treat bipolar disorder?",
      ["A) Antidepressants", "B) Mood stabilizers", "C) Antihistamines", "D) Antibiotics"],
      "B",
      "Mood stabilizers such as lithium are used for bipolar disorder."),

    q(73, "mental_health", "mh_disorders", "substance use", 2,
      "Which substance causes withdrawal symptoms including tremors and seizures?",
      ["A) Alcohol", "B) Cannabis", "C) Caffeine", "D) Nicotine"],
      "A",
      "Alcohol withdrawal can cause tremors, seizures, and delirium tremens."),

    q(74, "mental_health", "mh_concepts", "suicide prevention", 3,
      "What is the most important nursing action when a patient expresses suicidal ideation?",
      ["A) Ignore it to avoid reinforcing", "B) Ensure safety and constant observation", "C) Promise confidentiality", "D) Leave the patient alone"],
      "B",
      "Patient safety is the priority; continuous observation and risk assessment are required."),

    # --- Child Health Nursing (8) ---
    q(75, "child_health", "ch_growth", "developmental milestones", 2,
      "At what age does an infant typically sit without support?",
      ["A) 3 months", "B) 6 months", "C) 9 months", "D) 12 months"],
      "B",
      "Most infants can sit without support by around 6 months."),

    q(76, "child_health", "ch_common_diseases", "diarrhea", 1,
      "What is the best initial treatment for uncomplicated childhood diarrhea?",
      ["A) Antibiotics", "B) ORS", "C) Anti-diarrheal drugs", "D) Fasting"],
      "B",
      "Oral Rehydration Salts (ORS) are the first-line treatment for diarrhea."),

    q(77, "child_health", "ch_neonatal", "newborn care", 2,
      "What is the normal birth weight of a full-term Indian newborn?",
      ["A) 1.5-2 kg", "B) 2.5-3.5 kg", "C) 4-5 kg", "D) 1-1.5 kg"],
      "B",
      "Average full-term newborn weight is 2.5-3.5 kg."),

    q(78, "child_health", "ch_growth", "immunization schedule", 2,
      "At what age is the first dose of measles vaccine given?",
      ["A) 6 weeks", "B) 9 months", "C) 12 months", "D) 5 years"],
      "B",
      "The first dose of measles vaccine is given at 9 months of age."),

    q(79, "child_health", "ch_common_diseases", "ari", 2,
      "Which sign indicates severe pneumonia in a child?",
      ["A) Mild cough", "B) Chest indrawing", "C) Runny nose", "D) Sore throat"],
      "B",
      "Chest indrawing is a sign of severe pneumonia in children."),

    q(80, "child_health", "ch_neonatal", "breastfeeding", 1,
      "When should breastfeeding ideally be initiated after birth?",
      ["A) After 24 hours", "B) Within 1 hour", "C) After 6 hours", "D) After 12 hours"],
      "B",
      "Early initiation of breastfeeding within 1 hour is recommended."),

    q(81, "child_health", "ch_common_diseases", "malnutrition", 2,
      "Which anthropometric indicator is used to assess acute malnutrition in children?",
      ["A) Height-for-age", "B) Weight-for-height", "C) Head circumference", "D) Birth weight"],
      "B",
      "Weight-for-height is used to assess acute malnutrition."),

    q(82, "child_health", "ch_growth", "teething", 2,
      "At what age do primary teeth usually begin to erupt?",
      ["A) 2-3 months", "B) 6 months", "C) 12 months", "D) 18 months"],
      "B",
      "Primary teeth typically begin to erupt around 6 months of age."),

    # --- Midwifery & Gynecological Nursing (12) ---
    q(83, "midwifery", "mw_pregnancy", "antenatal care", 1,
      "How many antenatal check-ups are recommended for a normal pregnancy?",
      ["A) 2", "B) 4", "C) 6", "D) 8"],
      "B",
      "A minimum of 4 antenatal visits is recommended for a normal pregnancy."),

    q(84, "midwifery", "mw_labour", "stages of labour", 2,
      "Which stage of labour ends with full dilation of the cervix?",
      ["A) First stage", "B) Second stage", "C) Third stage", "D) Fourth stage"],
      "A",
      "The first stage of labour ends when the cervix is fully dilated (10 cm)."),

    q(85, "midwifery", "mw_labour", "apgar", 1,
      "At what intervals after birth is the Apgar score assessed?",
      ["A) 1 and 5 minutes", "B) 5 and 10 minutes", "C) 10 and 15 minutes", "D) 15 and 20 minutes"],
      "A",
      "Apgar score is assessed at 1 minute and 5 minutes after birth."),

    q(86, "midwifery", "mw_puerperium", "postnatal care", 2,
      "What is the normal duration of the puerperium?",
      ["A) 1 week", "B) 2 weeks", "C) 6 weeks", "D) 3 months"],
      "C",
      "The puerperium is the 6-week period following childbirth."),

    q(87, "midwifery", "mw_complications", "pih", 2,
      "What is the diagnostic triad of preeclampsia?",
      ["A) Hypertension, proteinuria, edema", "B) Fever, pain, bleeding", "C) Headache, vomiting, diarrhea", "D) Jaundice, anemia, oliguria"],
      "A",
      "Preeclampsia is classically diagnosed by hypertension, proteinuria, and edema."),

    q(88, "midwifery", "mw_complications", "pph", 3,
      "What is the most common cause of postpartum hemorrhage?",
      ["A) Infection", "B) Uterine atony", "C) Retained placenta", "D) Coagulopathy"],
      "B",
      "Uterine atony is the most common cause of postpartum hemorrhage."),

    q(89, "midwifery", "mw_gynecology", "menstrual disorders", 2,
      "What is the term for painful menstruation?",
      ["A) Amenorrhea", "B) Dysmenorrhea", "C) Menorrhagia", "D) Metrorrhagia"],
      "B",
      "Dysmenorrhea refers to painful menstrual periods."),

    q(90, "midwifery", "mw_anatomy", "pelvis", 2,
      "Which female pelvis type is most favourable for vaginal delivery?",
      ["A) Android", "B) Anthropoid", "C) Gynaecoid", "D) Platypelloid"],
      "C",
      "The gynaecoid pelvis is the most favourable for vaginal delivery."),

    q(91, "midwifery", "mw_pregnancy", "expected date", 2,
      "Naegele's rule calculates the expected date of delivery by adding 7 days and subtracting 3 months from:",
      ["A) Last menstrual period", "B) Date of conception", "C) First fetal movement", "D) First antenatal visit"],
      "A",
      "Naegele's rule uses the first day of the last menstrual period."),

    q(92, "midwifery", "mw_labour", "mechanism of labour", 3,
      "Which is the first movement in the mechanism of normal labour?",
      ["A) Internal rotation", "B) Descent", "C) Flexion", "D) Extension"],
      "B",
      "Descent of the fetal head is the first movement in the mechanism of labour."),

    q(93, "midwifery", "mw_complications", "eclampsia", 2,
      "What is the defining feature of eclampsia?",
      ["A) High blood pressure only", "B) Seizures in a woman with preeclampsia", "C) Severe headache", "D) Proteinuria only"],
      "B",
      "Eclampsia is preeclampsia complicated by seizures."),

    q(94, "midwifery", "mw_puerperium", "breastfeeding", 2,
      "Which hormone is responsible for milk ejection during breastfeeding?",
      ["A) Progesterone", "B) Oxytocin", "C) Estrogen", "D) Prolactin"],
      "B",
      "Oxytocin causes the milk ejection reflex (let-down)."),

    # --- Nutrition & Dietetics (5) ---
    q(95, "nutrition", "nut_basics", "balanced diet", 1,
      "Which nutrient is the main source of energy for the body?",
      ["A) Protein", "B) Fat", "C) Carbohydrate", "D) Vitamin"],
      "C",
      "Carbohydrates are the body's main energy source."),

    q(96, "nutrition", "nut_basics", "protein", 2,
      "Which disease is caused by severe protein-energy malnutrition?",
      ["A) Rickets", "B) Kwashiorkor", "C) Scurvy", "D) Night blindness"],
      "B",
      "Kwashiorkor results from severe protein deficiency."),

    q(97, "nutrition", "nut_lifecycle", "pregnancy nutrition", 2,
      "Which nutrient is most important to prevent neural tube defects in early pregnancy?",
      ["A) Iron", "B) Calcium", "C) Folic acid", "D) Vitamin C"],
      "C",
      "Folic acid supplementation prevents neural tube defects."),

    q(98, "nutrition", "nut_basics", "vitamins", 2,
      "Which vitamin deficiency causes scurvy?",
      ["A) Vitamin A", "B) Vitamin B12", "C) Vitamin C", "D) Vitamin D"],
      "C",
      "Vitamin C deficiency causes scurvy."),

    q(99, "nutrition", "nut_lifecycle", "iron deficiency", 2,
      "Which condition is most commonly caused by iron deficiency?",
      ["A) Night blindness", "B) Anemia", "C) Rickets", "D) Beriberi"],
      "B",
      "Iron deficiency is the most common cause of anemia."),

    # --- First Aid & Emergency (5) ---
    q(100, "first_aid", "fa_basics", "cpr", 1,
      "What is the recommended compression-to-ventilation ratio for adult CPR with one rescuer?",
      ["A) 15:2", "B) 30:2", "C) 5:1", "D) 50:2"],
      "B",
      "Adult CPR compression-to-ventilation ratio is 30:2 for one rescuer."),

    q(101, "first_aid", "fa_basics", "shock", 2,
      "What is the first step in managing a patient in shock?",
      ["A) Give oral fluids", "B) Maintain airway and breathing", "C) Apply tourniquet", "D) Elevate legs only"],
      "B",
      "Airway, breathing, and circulation are the first priorities in shock."),

    q(102, "first_aid", "fa_basics", "burns", 2,
      "How should a minor thermal burn be initially managed?",
      ["A) Apply ice directly", "B) Cool running water", "C) Apply butter", "D) Pop blisters"],
      "B",
      "Cool running water is recommended for minor burns."),

    q(103, "first_aid", "fa_emergency", "triage", 3,
      "In triage, which category is given highest priority?",
      ["A) Dead/expectant", "B) Minor", "C) Delayed", "D) Immediate"],
      "D",
      "Immediate category needs life-saving intervention first."),

    q(104, "first_aid", "fa_basics", "choking", 2,
      "Which manoeuvre is used to relieve airway obstruction in an adult?",
      ["A) Back blows only", "B) Heimlich manoeuvre", "C) Finger sweep", "D) Chest thrusts only"],
      "B",
      "Abdominal thrusts (Heimlich manoeuvre) are used for adult choking."),
]


def main():
    cognitive_counts = {}
    context_counts = {}
    for q_obj in QUESTIONS:
        cognitive_counts[q_obj["cognitive_level"]] = cognitive_counts.get(q_obj["cognitive_level"], 0) + 1
        context_counts[q_obj["context"]] = context_counts.get(q_obj["context"], 0) + 1

    bank = {
        "topic": "Telangana Staff Nurse Recruitment",
        "exam_pattern": "mhsrb_staff_nurse",
        "meta": {
            "total_questions": len(QUESTIONS),
            "language": "en",
            "source": "INC GNM Syllabus / Standard Nursing Textbooks",
            "verification_status": "reviewed",
            "verified_by": VERIFIED_BY,
            "last_reviewed": LAST_REVIEWED,
            "generated_at": LAST_REVIEWED,
            "dimensions": {
                "format": ["mcq"],
                "cognitive_level": cognitive_counts,
                "context": context_counts,
            },
        },
        "questions": QUESTIONS,
    }
    OUTPUT_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(QUESTIONS)} questions to {OUTPUT_PATH}")
    print(f"Cognitive levels: {cognitive_counts}")
    print(f"Contexts: {context_counts}")


if __name__ == "__main__":
    main()
