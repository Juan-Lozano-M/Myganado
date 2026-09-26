# My Ganado — Product truth

## 1) Product summary

My Ganado is an academic prototype for intelligent livestock monitoring aimed at small and medium cattle producers. It combines animal registration, virtual sensor simulation, a real-data-backed ML model, risk classification, alerts, and a dashboard that helps owners and veterinarians track the health status of cattle over time.

## 2) User and audience

Primary users:

- Cattle owners or farm managers.
- Small and medium producers with limited technical resources.
- Academic evaluators and instructors.

Secondary users:

- Veterinarians receiving escalated cases.
- Developers and researchers validating the ML workflow.

## 3) Core value proposition

The product helps users monitor cattle conditions through a simple decision-support flow:

1. Record animals and measurements.
2. Simulate physiological and environmental data.
3. Use a real-data-based ML model to estimate risk.
4. Visualize the current state and historical trends.
5. Trigger alerts and escalate persistent risk cases.

This is not a veterinary diagnosis system. It is a monitoring and follow-up support tool.

## 4) Primary goals

- Register and track bovine individuals.
- Store physiological, behavioral, and environmental measurements.
- Produce plausible simulated sensor readings for testing and demos.
- Build an ML pipeline using a real dataset seed, cleaned and documented.
- Classify risk as LOW, MEDIUM, or HIGH.
- Generate notifications for owners and escalations for veterinarians.
- Show results in a dashboard with historical evolution.

## 5) Non-goals

- Real-time physical hardware monitoring in the MVP.
- Computer vision or image-based detection.
- Purchase of actual IoT devices or sensors.
- Veterinary treatment automation.
- Diagnosis or prescription decisions.
- Mandatory integration with real hardware during this first version.

## 6) Operating context

The application is expected to run in a local academic environment using:

- React + TypeScript for the frontend.
- FastAPI + Python for the backend.
- PostgreSQL for persistence.
- Scikit-learn + Python for the ML pipeline.
- Docker Compose for local execution.

The architecture should be modular enough to replace the simulator with real IoT sensors later without major UI or domain disruption.

## 7) Key user flows

A. Animal registration and tracking

- Create animal profile.
- Save physical and contextual details.
- Review individual records and history.

B. Measurement and simulation

- Configure environmental conditions.
- Run simulation for animal + environment.
- Store virtual sensor readings.

C. ML inference and risk assessment

- Send measurement data to the model.
- Receive classified risk.
- Record probability and timestamp.

D. Alerting and escalation

- LOW: record only.
- MEDIUM: notify owner, track persistence.
- HIGH: notify owner and veterinarian immediately.

E. Historical review

- Compare risk evolution over time.
- Visualize variables such as temperature, activity, water consumption, and environmental conditions.

## 8) Functional constraints

- The model must use a real and documented dataset seed, not only synthetic data.
- Synthetic data must be clearly separated from real data and never presented as authentic veterinary measurements.
- The target variable risk must be documented as real or derived, with methodology when derived.
- The UI should prioritize clarity over visual complexity.
- The system must be understandable for demonstration and academic validation.

## 9) Design direction

The interface should feel trustworthy, readable, and operational, with emphasis on:

- Clear reading of risk states.
- Strong hierarchy on key KPIs and alerts.
- Easy understanding of historical patterns.
- Calm, professional visual design with practical supervision dashboards.
- Good contrast and readable typography for data-heavy views.

## 10) Tone and voice

- Professional.
- Clear and practical.
- Supportive, not clinical.
- Focused on monitoring and follow-up.

## 11) Evidence and validation

The product should be considered successful when the following are demonstrable:

- Real dataset and documentation exist.
- Cleaning and preparation are reproducible.
- ML models are trained and evaluated.
- A risk model is integrated into the backend.
- Simulated readings reach the API and generate a prediction.
- Alerts and persistence are correctly recorded.
- Dashboard shows the lifecycle end-to-end.

## 12) Status

Current status: product context initialized for project execution.

Next recommended actions:

- Select and document the real dataset.
- Define the target variable and methodology.
- Create the ML cleaning pipeline.
- Implement the backend and simulator contracts.
- Build the first dashboard views.
