# Akshaya Advisory MVP

Akshaya Advisory is a Citizen Service Advisory Chatbot designed to assist citizens with navigating government services in Kerala. This MVP utilizes an Agentic Retrieval-Augmented Generation (RAG) architecture to provide accurate, strictly sourced, and context-aware guidance for citizens.

## Supported Services
This MVP is strictly scoped to the following services in **English**:
1. **Aadhaar Services:** Enrollment, updates, document requirements, and general guidance.
2. **Kerala Ration Card Services:** Applying for new cards, adding/removing members, and eligibility criteria.
3. **Scholarship Services:** Advisory on National Scholarship Portal (NSP) schemes, eligibility, and required documentation.

## Core Features
* **Multimodal Chat (Text & Images):** Users can ask text questions or upload/capture images of documents. The backend uses a vision-capable LLM to analyze the document, classify the service, and provide relevant official guidance.
* **Agentic RAG Pipeline:** Combines intent classification, dynamic FAISS semantic search, and structured LLM generation to produce highly accurate, formatted responses (Summary, Documents, Eligibility, Next Steps).
* **Contextual Follow-ups:** Maintains conversation context, allowing users to ask follow-up questions like "Where should I go?" without restating the service name.
* **Strict Source Grounding:** Answers are generated *strictly* using the retrieved official documents. The system provides active citations and degrades gracefully if a question is out of scope (Anti-Hallucination).
* **Feedback & History:** Users can upvote/downvote answers with comments and view their past categorized conversations.

## Architecture & Technology Stack

### Frontend (React Native / Expo)
* **Framework:** Expo (React Native Web + Mobile), TypeScript.
* **Features:** Responsive Blue/White UI, cross-platform file uploads (Blob/File on Web, URI on Native), robust message rendering, offline-safe history state.
* **Networking:** Auto-detects environment to map API requests (`127.0.0.1` for Web, `10.0.2.2` for Android Emulators, or custom network IPs).

### Backend (Python / FastAPI)
* **Framework:** FastAPI, Uvicorn ASGI server, SQLAlchemy ORM.
* **AI / LLM:** **Grok API (`grok-2-latest`)** for both text and vision evaluation.
* **Embeddings & Vector Store:** `sentence-transformers/all-MiniLM-L6-v2` embeddings indexed in **FAISS** for ultra-fast local retrieval.
* **Database:** SQLite for structured data (Conversations, Messages, Feedback, Citations).

## Security & Privacy Safeguards
* **Temporary Image Processing:** Uploaded document images are saved to a temporary directory, evaluated by the vision model, and **immediately deleted** in a `try/finally` block. They are never permanently stored or embedded into the vector database.
* **PII Scrubbing:** Built-in privacy filters prevent sensitive numerical data from being unnecessarily processed or echoed.
* **Secrets Management:** Environment variables (`.env`) are strictly untracked.

---

## Local Setup & Installation

### 1. Backend Setup
Navigate to the backend directory and set up the Python environment:
```cmd
cd akshaya-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in `akshaya-backend/` based on `.env.example`:
```env
GROK_API_KEY=your_api_key_here
```

**Start the Backend Server:**
```cmd
uvicorn app.main:app --port 8001
# Note: Use --reload for development
```
The API will be available at `http://127.0.0.1:8001`.

### 2. Frontend Setup
Navigate to the frontend directory:
```cmd
cd akshaya-frontend
npm install
```

**Start the Frontend Web App:**
```cmd
npx expo start --web
```
You can also run it on an Android Emulator by pressing `a` in the Expo terminal. The app will automatically route requests to `10.0.2.2:8001` to bridge the emulator network gap.

### 3. Knowledge Base Ingestion (Optional)
The pre-built FAISS index is already included in `akshaya-backend/data/vector_store/`. 
If you add new official PDFs to the `akshaya-knowledge-base` directory, re-run the ingestion pipeline:
```cmd
cd akshaya-backend/ingestion
python extract_text.py
python chunk_documents.py
python generate_embeddings.py
python build_faiss_index.py
```

## API Reference
* `POST /chat`: Main endpoint for sending text/image queries. Returns a structured JSON response.
* `POST /feedback`: Accepts user ratings (`helpful`/`not_helpful`) and comments.
* `GET /conversations`: Returns a paginated list of the user's conversation history based on `device_id`.
* `GET /conversations/{id}`: Returns full message history and context for a specific conversation.
* `GET /health`: System availability check.

## Disclaimer
This MVP chatbot is an advisory tool and does not replace an Akshaya operator or official government department. Requirements and fees should be independently verified.
