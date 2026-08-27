# Model Card

## Model: ReviewShield Fusion v0.1.0

**Purpose**: Evidence-based review fraud risk assessment

**Training Data**: DEMO DATA only (synthetic, deterministic seed=42)

**Features**: 5 modality risk scores (text, behavior, temporal, similarity, graph)

**Evaluation**: Classification distribution on demo dataset

**Limitations**:
- Not trained on real-world data
- Risk scores are estimates, not proof of fraud
- Single suspicious signal does not confirm fraud

**Intended Use**: Academic demonstration, portfolio project, investigation support

**Non-Intended Use**: Automated fraud conviction, legal evidence
