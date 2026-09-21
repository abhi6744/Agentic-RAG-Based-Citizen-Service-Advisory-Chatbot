# Akshaya Advisory

## Project overview
Akshaya Advisory is a Citizen Service Advisory Chatbot designed to assist citizens with navigating government services in Kerala, specifically for Aadhaar, Kerala Ration Cards, and Scholarships. This MVP is an English-only application.

## Problem statement
Citizens often find it difficult to navigate complex bureaucratic requirements, identifying the correct documents, fees, and office locations for government services.

## Proposed solution
An intelligent, context-aware chatbot (Agentic RAG) that provides accurate, sourced answers based on official government documents and rules.

## Current MVP scope
The current MVP is limited to English-language interactions and focuses exclusively on three predefined service categories. It does not process actual applications but provides advisory guidance.

## Supported services

### Aadhaar Services
Guidance on enrollment, updates, document requirements, and finding enrollment centers.

### Kerala Ration Card Services
Information on applying for new cards, adding/removing members, and eligibility criteria based on the Kerala Ration Card rules.

### Scholarship Services
Advisory on National Scholarship Portal (NSP) schemes, eligibility, and required documentation.

## Main features

### Natural-language chat
Conversational interface to ask questions about supported services.

### Contextual follow-up questions
The system remembers the context (e.g., if you ask about Ration Cards, a follow-up like "Where should I go?" will remain in the Ration Card context).

### Next-step guidance
Provides actionable next steps after resolving the immediate query.

### Image upload
Users can attach images (mocked UI support for document analysis in the future).

### Source citations
Answers include references to the official documents they were derived from.

### Confidence and verification warnings
The system issues warnings if a query is out of scope or if the information must be independently verified.

### Feedback collection
Users can rate answers as helpful or unhelpful and provide comments.

### Conversation history
Maintains a log of past user interactions.

### Privacy safeguards
Filters out personal or sensitive information before processing queries.

## Frontend architecture
- React Native / Expo application
- Written in TypeScript
- Uses Expo Router for navigation
- Custom theming (light blue/white layout)

## Backend architecture
- FastAPI application (Python)
- Uvicorn ASGI server
- Agentic architecture for routing and RAG

## Agentic RAG pipeline
Retrieval-Augmented Generation using a combination of intent classification, semantic search, and an LLM for natural language response generation.

## Document ingestion pipeline
Scripts to parse PDFs from the local knowledge base, chunk text, and embed it using an embedding model.

## Embedding and vector search
Leverages embedding models to convert text chunks into vector representations for semantic search.

## FAISS vector store
Local vector database using FAISS to index and rapidly retrieve relevant document chunks.

## SQLite database
Stores structured data such as chat history, feedback, and user sessions.

## API endpoints
- `/api/v1/chat`: Main conversational endpoint.
- `/api/v1/feedback`: Endpoint to submit user feedback.
- `/api/v1/history`: Endpoint to fetch conversation history.

## Project folder structure
- `akshaya-frontend/`: Contains the Expo React Native application.
- `akshaya-backend/`: Contains the FastAPI backend, ingestion scripts, and database models.
- `docs/`: General project documentation.

## Technology stack
- **Frontend:** React Native, Expo, TypeScript
- **Backend:** Python, FastAPI, Uvicorn, SQLAlchemy
- **AI/Vector Store:** FAISS, Grok API (LLM)
- **Database:** SQLite

## Environment variables
The backend requires a `.env` file containing API keys and other configuration parameters. See `.env.example` for required keys.

## Local setup
1. Clone the repository.
2. Setup the backend virtual environment and install requirements.
3. Setup the frontend dependencies.

## Running the backend
``cmd
cd akshaya-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8001
``

## Running the frontend
Navigate to `akshaya-frontend/` and run:
```bash
npx expo start --web
```

## Building the knowledge base
Navigate to `akshaya-backend/ingestion/` and run the appropriate scripts to parse documents and build the FAISS index. (Note: Raw documents are stored locally in `akshaya-knowledge-base` and are deliberately ignored in Git).

## Testing
Test the API endpoints directly or use the Expo web interface.

## Grounding and anti-hallucination design
The LLM is strictly prompted to use only the provided context. If an answer cannot be found in the context, it gracefully degrades rather than hallucinating details.

## Security and privacy
No PII is permanently logged in plain text where avoidable, and privacy filters scrub sensitive data from user queries before LLM processing.

## Current limitations
- English only.
- Limited to three service domains.
- Does not integrate with live government portals.

## Future enhancements
- Multi-lingual support (Malayalam, Hindi).
- More government services.
- Real-time location integration for nearby Akshaya centers.

## Important source and verification disclaimer
This chatbot does not replace an Akshaya operator or government department. Current requirements, fees, and procedures must be confirmed through official sources.
