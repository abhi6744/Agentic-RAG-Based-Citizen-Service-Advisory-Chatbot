import os
import subprocess
import sys

def run_cmd(cmd, cwd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, cwd=cwd, check=True)

docs_dir = r"C:\Users\abhin\OneDrive\Desktop\S Project\Chatbot\docs"

# 1. Install Mermaid CLI
try:
    run_cmd("npm install @mermaid-js/mermaid-cli", cwd=docs_dir)
except Exception as e:
    print("Failed to install mermaid-cli:", e)

# 2. Define Mermaid diagrams
diagrams = {
    "arch.mmd": """
graph TD
    User([Citizen / Operator]) --> UI[Web Interface]
    UI --> API[FastAPI Backend]
    
    API --> Retriever[Retrieval Engine]
    API --> Generator[Generation Engine]
    API --> Citation[Citation Module]
    
    Retriever --> VecDB[(Vector DB FAISS/Chroma)]
    Generator --> LLM[Large Language Model]
    
    Admin([Administrator]) --> AdminUI[Admin Dashboard]
    AdminUI --> DocProcessor[Document Ingestion]
    DocProcessor --> Chunking[Text Chunking & Embedding]
    Chunking --> VecDB
""",
    "usecase.mmd": """
graph LR
    User([Citizen / Operator]) --> Ask[Ask Service Query]
    User --> Browse[Browse Services]
    User --> Feed[Submit Feedback]
    
    Admin([Administrator]) --> Manage[Manage Documents]
    Admin --> Logs[Monitor Query Logs]
""",
    "dfd0.mmd": """
graph LR
    User([User]) -- "Natural Language Query" --> System[Agentic RAG Chatbot System]
    System -- "Grounded Answer + Citations" --> User
    
    Admin([Administrator]) -- "Official PDF Documents" --> System
    System -- "System Logs & Metrics" --> Admin
""",
    "dfd1.mmd": """
graph TD
    User([User]) --> QProc[Query Processor]
    QProc --> Embed[Embedding Generator]
    Embed --> VecSearch[Vector Search]
    
    VecSearch -- "Search Query" --> VecDB[(Vector Database)]
    VecDB -- "Top-K Chunks" --> PromptGen[Prompt Constructor]
    
    PromptGen --> LLM[LLM API]
    LLM --> Citation[Citation Mapper]
    Citation --> Output[Response Formatter]
    Output --> User
""",
    "state.mmd": """
stateDiagram-v2
    [*] --> Idle
    Idle --> ProcessingQuery : User Submits Query
    ProcessingQuery --> GeneratingEmbeddings
    GeneratingEmbeddings --> SearchingDatabase
    SearchingDatabase --> ConstructingPrompt : Found Chunks
    SearchingDatabase --> LowConfidence : No Relevant Chunks
    LowConfidence --> Idle : Return Warning
    ConstructingPrompt --> CallingLLM
    CallingLLM --> MappingCitations
    MappingCitations --> Idle : Display Answer
"""
}

# 3. Write Mermaid files and convert to PNG
mmdc_path = os.path.join(docs_dir, "node_modules", ".bin", "mmdc")
for name, content in diagrams.items():
    mmd_path = os.path.join(docs_dir, name)
    png_path = os.path.join(docs_dir, name.replace(".mmd", ".png"))
    with open(mmd_path, "w") as f:
        f.write(content.strip())
    
    try:
        run_cmd(f'"{mmdc_path}" -i {name} -o {name.replace(".mmd", ".png")} -t neutral', cwd=docs_dir)
    except Exception as e:
        print(f"Failed to compile {name}:", e)

# 4. Generate the PDF Report
try:
    import reportlab
except ImportError:
    run_cmd(f"{sys.executable} -m pip install reportlab", cwd=docs_dir)

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_report():
    output_path = os.path.join(docs_dir, "final_report.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=20)
    bold_center = ParagraphStyle('BoldCenter', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=20)
    
    heading1 = ParagraphStyle('Heading1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, spaceAfter=16, spaceBefore=20, alignment=TA_CENTER)
    heading2 = ParagraphStyle('Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, spaceAfter=12, spaceBefore=16)
    heading3 = ParagraphStyle('Heading3', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=10, spaceBefore=10)
    
    normal = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=12)
    bullet = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=12, leading=18, leftIndent=20, spaceAfter=6)

    story = []

    # --- TITLE PAGE ---
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("PROJECT REPORT", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Agentic RAG-Based Citizen Service<br/>Advisory Chatbot", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Submitted in Partial Fulfilment of the Requirements for the<br/>Award of the Degree of", subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("MASTER OF COMPUTER APPLICATIONS", bold_center))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("By", subtitle_style))
    story.append(Paragraph("Abhinav G", bold_center))
    story.append(Paragraph("25225040", bold_center))
    story.append(Spacer(1, 1*inch))
    
    story.append(Paragraph("CHRIST (DEEMED TO BE UNIVERSITY)", ParagraphStyle('BlueBold', parent=bold_center, textColor=colors.blue, fontSize=18)))
    story.append(Paragraph("BANGALORE | DELHI NCR | PUNE", subtitle_style))
    story.append(Spacer(1, 0.5*inch))
    
    story.append(Paragraph("CHRIST (Deemed to be University)", bold_center))
    story.append(Paragraph("Delhi NCR", subtitle_style))
    story.append(Paragraph("School of Sciences", subtitle_style))
    story.append(Paragraph("September 2026", bold_center))
    story.append(PageBreak())

    # --- ABSTRACT ---
    story.append(Paragraph("ABSTRACT", heading1))
    abs_text = "Agentic RAG-Based Citizen Service Advisory Chatbot is an AI-assisted web platform designed to address the inefficiencies in government citizen service delivery through a multilingual conversational interface combined with retrieval-augmented generation and citation grounding.\n\nThe system bridges the gap between complex official documents and citizens through a web application while maintaining a cloud-connected knowledge base of official service rules. The platform provides natural language interaction for querying eligibility, required documents, and fees. The documented interaction model supports multilingual inputs (English and Malayalam), automatic context retrieval, generated answers grounded strictly in official documents, and explicit citation mappings to verify claims.\n\nThe system uses Python, FastAPI, and a Vector Database (FAISS/Chroma) as the backend synchronization layer. The documented virtual endpoints include query processing, embedding generation, document chunk retrieval, and LLM prompt construction. A web platform presents a simple chat interface, service browsing, and administrator dashboard.\n\nThe platform converts complex bureaucratic text into understandable guidance using the principle of strictly grounded Generation. Retrieval relevance and citation mapping prevent hallucinations and ensure high trust.\n\nThis report presents the problem definition, theoretical background, requirements, system architecture, software design, cloud integration, dashboard design, algorithms, implementation, deployment process, testing methodology, results, limitations, responsible use of AI and future scope."
    for p in abs_text.split('\n\n'):
        story.append(Paragraph(p, normal))
    story.append(PageBreak())

    # --- LIST OF TABLES ---
    story.append(Paragraph("LIST OF TABLES", heading1))
    tables_list = [
        ("Table 1", "Project Objectives"),
        ("Table 2", "Functional Requirements"),
        ("Table 3", "Non-Functional Requirements"),
        ("Table 4", "Software Components"),
        ("Table 5", "Functional Test Cases"),
        ("Table 6", "Integration Test Cases"),
        ("Table 7", "Challenge and Resolution Log")
    ]
    t_data = [["Table No.", "Description"]] + tables_list
    t = Table(t_data, colWidths=[1.5*inch, 4.5*inch])
    t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t)
    story.append(PageBreak())

    # --- LIST OF FIGURES ---
    story.append(Paragraph("LIST OF FIGURES", heading1))
    figures_list = [
        ("Figure 1", "Overall System Architecture"),
        ("Figure 2", "Use-Case Diagram"),
        ("Figure 3", "Level 0 Data Flow Diagram"),
        ("Figure 4", "Level 1 Data Flow Diagram"),
        ("Figure 5", "State/Activity Diagram")
    ]
    f_data = [["Figure No.", "Description"]] + figures_list
    f = Table(f_data, colWidths=[1.5*inch, 4.5*inch])
    f.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(f)
    story.append(PageBreak())

    # --- LIST OF ABBREVIATIONS ---
    story.append(Paragraph("LIST OF ABBREVIATIONS", heading1))
    abbr_list = [
        ("AI", "Artificial Intelligence"),
        ("RAG", "Retrieval-Augmented Generation"),
        ("LLM", "Large Language Model"),
        ("NLP", "Natural Language Processing"),
        ("API", "Application Programming Interface"),
        ("UI", "User Interface"),
        ("UX", "User Experience"),
        ("DB", "Database"),
        ("FAQ", "Frequently Asked Questions")
    ]
    a_data = [["Abbreviation", "Meaning"]] + abbr_list
    a = Table(a_data, colWidths=[1.5*inch, 4.5*inch])
    a.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(a)
    story.append(PageBreak())

    # --- TABLE OF CONTENTS ---
    story.append(Paragraph("TABLE OF CONTENTS", heading1))
    toc_data = [
        ["Section / Chapter Name", "Page No."],
        ["Abstract", "ii"],
        ["List of Tables", "iii"],
        ["List of Figures", "iv"],
        ["List of Abbreviations", "v"],
        ["Chapter 1 - Introduction & Project Objectives", "1"],
        ["1.1 Industry and Application Context", "1"],
        ["1.2 Project Background", "1"],
        ["1.3 Problem Statement", "2"],
        ["1.4 Motivation", "2"],
        ["1.5 Objectives", "3"],
        ["1.6 Scope", "3"],
        ["1.7 Contributions", "4"],
        ["Chapter 2 - System Study & Theoretical Background", "5"],
        ["2.1 Existing Approaches", "5"],
        ["2.2 Retrieval-Augmented Generation (RAG)", "6"],
        ["2.3 Large Language Models (LLMs)", "7"],
        ["2.4 Multilingual Natural Language Processing", "8"],
        ["2.5 Trust and Citation Mechanisms", "9"],
        ["2.6 Cloud-Native Design Perspective", "10"],
        ["2.7 Requirement Analysis", "11"],
        ["Chapter 3 - System Design & Implementation", "13"],
        ["3.1 Roles and Responsibilities", "13"],
        ["3.2 Tools and Technologies", "14"],
        ["3.3 Overall System Architecture", "15"],
        ["3.4 Use Case Model", "17"],
        ["3.5 Data Flow Design", "19"],
        ["3.6 Process Flow & State Diagram", "21"],
        ["3.7 Dashboard & UI Design", "23"],
        ["3.8 Algorithms", "25"],
        ["3.9 Implementation Details", "27"],
        ["Chapter 4 - Deployment, Testing, Results & Discussion", "29"],
        ["4.1 Deployment Strategy", "29"],
        ["4.2 Functional Testing", "31"],
        ["4.3 Integration Testing", "33"],
        ["4.4 Testing Workflow", "35"],
        ["4.5 Results: Implemented Functionalities", "37"],
        ["4.6 Feature Analysis", "39"],
        ["4.7 Challenges and Resolutions", "41"],
        ["4.8 Deployment Readiness", "42"],
        ["Chapter 5 - Conclusions & Recommendations", "43"],
        ["5.1 Summary of Work", "43"],
        ["5.2 Learning Outcomes", "44"],
        ["5.3 Limitations", "45"],
        ["5.4 Responsible Usage of AI", "46"],
        ["5.5 Future Scope", "47"],
        ["5.6 Recommendations", "48"],
        ["5.7 Conclusion", "49"],
        ["References", "50"]
    ]
    t_toc = Table(toc_data, colWidths=[5.0*inch, 1.0*inch])
    t_toc.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('GRID', (0,0), (-1,-1), 1, colors.black), ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('PADDING', (0,0), (-1,-1), 6)]))
    for i, row in enumerate(toc_data):
        if "Chapter" in row[0] or row[0] in ["Abstract", "List of Tables", "List of Figures", "List of Abbreviations", "References"]:
            t_toc.setStyle(TableStyle([('FONTNAME', (0,i), (-1,i), 'Helvetica-Bold')]))
    story.append(t_toc)
    story.append(PageBreak())

    def add_section(title, content, level=2, image=None):
        if level == 1:
            story.append(Paragraph(title, heading1))
        elif level == 2:
            story.append(Paragraph(title, heading2))
        else:
            story.append(Paragraph(title, heading3))
        
        if image and os.path.exists(image):
            story.append(Spacer(1, 10))
            # Increase diagram size
            story.append(Image(image, width=6*inch, height=4*inch, kind='proportional'))
            story.append(Spacer(1, 10))

        if isinstance(content, list):
            for item in content:
                story.append(Paragraph(item, bullet))
        else:
            for p in content.split('\n\n'):
                story.append(Paragraph(p, normal))
        story.append(Spacer(1, 20))

    # --- CHAPTER 1 ---
    story.append(Paragraph("CHAPTER 1", heading1))
    story.append(Paragraph("INTRODUCTION & PROJECT OBJECTIVES", heading1))
    
    add_section("1.1 Industry and Application Context", "Government citizen service delivery in India increasingly relies on physical service centers such as Akshaya centers in Kerala, which act as front-end delivery points for a wide range of government-to-citizen (G2C) services including certificates, ration card services, Aadhaar-related support, and welfare scheme applications.\n\nWhile these centers bridge the digital divide effectively, the information layer behind them is still largely manual: operators depend on memory or scattered documents to explain eligibility, required documents, fees, and procedures to citizens. This creates repeated visits, incomplete applications, and inconsistent guidance.\n\nTraditional productivity applications generally address this problem through software-based mechanisms such as static FAQ portals. However, such approaches continue to leave the immediate, accurate interpretation of rules inaccessible to citizens.\n\nThis project approaches the problem from an AI perspective. Instead of attempting to hardcode every rule, the project introduces a dedicated RAG-based physical and digital workflow.")
    add_section("1.2 Project Background", "The project originated from the observation that digital portals alone may not address the availability of accurate advisory services.\n\nThe repository identifies several practical problems:\n• Documents remain scattered across different domains.\n• Digital documents may be bypassed by users preferring human interaction.\n• Operators rely heavily on memory.\n• Productivity and accuracy depend strongly on individual discipline.\n\nThis system introduces an intelligent interaction layer.")
    add_section("1.3 Problem Statement", "The central problem addressed by this project is:\n\nHow can a cloud-based AI intervention be combined with verified document retrieval to support a structured citizen advisory workflow while reducing hallucinations?\n\nThe problem can be divided into five requirements:\n1. Simple query configuration.\n2. Immediate accurate feedback.\n3. Consistent state management.\n4. Historical analytics.\n5. Multilingual capability.\n\nThe system addresses these requirements through RAG.")
    add_section("1.4 Motivation", "The primary motivation is to create a bridge between complex official documents and simple citizen needs.\n\nA normal rule-based chatbot records inputs but does not necessarily understand nuanced queries.\n\nThis project introduces a dedicated verified workflow:\nQuery -> Embed -> Search -> Extract -> Generate -> Cite -> Serve.\n\nThis workflow creates a measurable connection between the citizen's needs and the official government guidelines.")
    add_section("1.5 Objectives", "The project objectives are outlined below:\n\n1. Develop a RAG pipeline over official documents.\n2. Implement natural language handling.\n3. Provide citation-grounded local feedback.\n4. Connect the web platform to the vector database.\n5. Integrate LLM Cloud APIs for synthesis.")
    add_section("1.6 Scope", "The project covers:\n• Web Frontend\n• Python Backend\n• Vector Database (FAISS/Chroma)\n• LLM API connectivity\n• Document chunking\n• Citation mapping\n\nThe project does not claim to process actual service applications or diagnose legal conditions.")
    add_section("1.7 Contributions", "The principal contribution is the integration of modern LLM reasoning with strict verified retrieval.\n\nThe project demonstrates:\n1. Document embedding.\n2. Cloud-connected semantic search.\n3. Web-based visualisation.\n4. Context-grounded synthesis.\n5. End-to-end RAG architecture integration.")
    story.append(PageBreak())

    story.append(Paragraph("CHAPTER 2", heading1))
    story.append(Paragraph("SYSTEM STUDY & THEORETICAL BACKGROUND", heading1))
    add_section("2.1 Existing Approaches", "Existing solutions can generally be grouped into:\n\nStatic Portals\nThese provide basic search over PDFs.\n\nRule Blockers / Decision Trees\nThese restrict the conversation to fixed paths.\n\nGeneral LLMs\nThese offer open-ended conversations but suffer from hallucinations.\n\nThis project uses an additional mechanism: Retrieval-Augmented Generation.")
    add_section("2.2 Retrieval-Augmented Generation (RAG)", "The Internet of Things and AI have evolved. RAG refers to interconnected systems capable of extracting, processing, and synthesizing information with high accuracy.\n\nA typical RAG architecture contains:\n1. Document Ingestion Pipeline\n2. Vector Database\n3. Semantic Search Engine\n4. Prompt Compiler\n5. LLM Synthesis\n\nThis project follows this exact robust structure.")
    add_section("2.3 Large Language Models (LLMs)", "LLMs are used as the primary reasoning engine.\n\nThe LLM provides:\n• Natural Language Understanding\n• Contextual synthesis\n• Multilingual translation\n• Structured output formatting\n\nWithin this project, the LLM is strictly constrained to only answer using the provided context chunks.")
    add_section("2.4 Multilingual Natural Language Processing", "Supporting languages like Malayalam requires powerful cross-lingual embedding models. The system relies on models that map semantically identical phrases in English and Malayalam to the same vector space, enabling unified retrieval.")
    add_section("2.5 Trust and Citation Mechanisms", "Highlighting the exact source document builds trust. The system maps generated claims back to the exact source chunks retrieved from the database.")
    add_section("2.6 Cloud-Native Design Perspective", "The application can be understood as a cloud-native app where responsibilities are separated across layers.\n\nData layer\nVector DB, metadata SQLite.\n\nLogic layer\nFastAPI.\n\nApplication layer\nWeb dashboard.")
    add_section("2.7 Requirement Analysis", "Functional Requirements:\nFR01: User shall be able to submit queries.\nFR02: System shall generate embeddings.\nFR03: System shall perform vector search.\nFR04: System shall construct constrained prompts.\nFR05: System shall provide citations.\n\nNon-Functional Requirements:\nUsability: Interaction should be simple.\nReliability: Citations must be strictly accurate.\nResponsiveness: System should react quickly.\nMaintainability: Layers should remain modular.")
    story.append(PageBreak())

    story.append(Paragraph("CHAPTER 3", heading1))
    story.append(Paragraph("SYSTEM DESIGN & IMPLEMENTATION", heading1))
    add_section("3.1 Roles and Responsibilities", "The major project roles are:\n\nUser: Interacts with the interface.\nBackend Controller: Orchestrates the workflow.\nVector DB: Synchronizes telemetry.\nWeb Platform: Displays information.")
    add_section("3.2 Tools and Technologies", "Category - Technology\nFrontend - React/Next.js\nBackend - Python FastAPI\nDatabase - FAISS/Chroma\nLLM API - OpenAI/Anthropic")
    
    add_section("3.3 Overall System Architecture", "The complete architecture can be represented as follows.", image=os.path.join(docs_dir, "arch.png"))
    
    add_section("3.4 Use Case Model", "The primary actor is the user.\n\nThe user can:\n• Ask Service Query\n• Browse Services\n• View Dashboard\n• View Citations\n\nThe admin can:\n• Manage Documents\n• Monitor Logs", image=os.path.join(docs_dir, "usecase.png"))
    
    add_section("3.5 Data Flow Design", "Level 0 Data Flow Diagram represents the outermost system context.", image=os.path.join(docs_dir, "dfd0.png"))
    add_section("3.6 Process Flow & State Diagram", "The Level 1 DFD and State Diagram illustrate internal workflows.", image=os.path.join(docs_dir, "dfd1.png"))
    add_section("3.7 Activity and State Behaviour", "The state diagram shows the transition from Idle to Processing.", image=os.path.join(docs_dir, "state.png"))
    
    add_section("3.8 Algorithms", "The core algorithm is the Retrieval-Augmented Generation loop.\n\n1. Receive Query Q.\n2. Generate Embedding E(Q).\n3. Search DB for Top-K chunks where CosineSimilarity(E(Q), Chunk_i) is maximized.\n4. Compile Prompt P = Context + Q.\n5. Call LLM(P).\n6. Return Output.")
    add_section("3.9 Implementation Details", "The software architecture is divided into the Frontend Layer (handling inputs and UI updates), the Backend Layer (handling session state, DB queries, and API connections), and the Data Layer (storing vectors and metadata).")
    story.append(PageBreak())

    story.append(Paragraph("CHAPTER 4", heading1))
    story.append(Paragraph("DEPLOYMENT, TESTING, RESULTS & DISCUSSION", heading1))
    add_section("4.1 Deployment Strategy", "The deployment consists of several coordinated layers.\n\nStep 1 - Environment preparation\nConfigure Python, Node, and API keys.\n\nStep 2 - Database configuration\nInitialize the Vector DB.\n\nStep 3 - Cloud configuration\nEstablish endpoints for the frontend to hit.\n\nStep 4 - Web platform\nLaunch the React server.\n\nStep 5 - Integration\nPerform an end-to-end test.")
    add_section("4.2 Functional Testing", "Testing was designed around the features documented in the repository.\n\nFT01: Server starts -> API is accessible.\nFT02: Query submitted -> Vector search triggered.\nFT03: Generation -> Text streaming begins.\nFT04: Citation -> Accurate document metadata returned.")
    add_section("4.3 Integration Testing", "Integration testing verifies the complete system rather than individual components.\n\nIT01: Frontend -> Backend (Query reaches API).\nIT02: Backend -> DB (Chunks returned successfully).\nIT03: Backend -> LLM (Prompt accepted, response generated).\nIT04: Response -> Frontend (UI updates dynamically).")
    add_section("4.4 Results: Implemented Functionalities", "The repository documentation confirms the following principal features:\n• RAG architecture.\n• Configurable document ingestion.\n• React-based Chat UI.\n• Multilingual LLM synthesis.\n• Explicit citation tracking.")
    add_section("4.5 Challenges and Resolutions", "Challenge: LLM Hallucinations. Resolution: Strict prompt instructions and temperature=0.\nChallenge: Large document processing. Resolution: Implemented sliding window chunking.\nChallenge: Multilingual accuracy. Resolution: Utilized advanced cross-lingual embedding models.")
    story.append(PageBreak())

    story.append(Paragraph("CHAPTER 5", heading1))
    story.append(Paragraph("CONCLUSIONS & RECOMMENDATIONS", heading1))
    add_section("5.1 Summary of Work", "This project was developed as an AI-assisted RAG system that combines physical document reality with digital intelligence.\n\nThe system consists of:\n• Python Backend\n• Vector Database\n• LLM API\n• React Web Dashboard")
    add_section("5.2 Learning Outcomes", "The project provided learning in several areas:\n\nArtificial Intelligence: Understanding embeddings and LLMs.\nFull-Stack Development: Connecting React with FastAPI.\nSystem Architecture: Designing scalable, cloud-connected platforms.")
    add_section("5.3 Limitations", "The current implementation is a project-scale prototype.\n\nA production system would require additional:\n• Security controls.\n• Load balancers.\n• Advanced document OCR for scanned PDFs.")
    add_section("5.4 Responsible Usage of AI", "Responsible use of AI is important. The strict grounding mechanism ensures that AI-generated suggestions are not presented as factual unless they have actually been retrieved from an official document.")
    add_section("5.5 Future Scope", "Future versions could explore:\n• Integration with messaging apps (WhatsApp).\n• Automated scraping of government portals.\n• Voice interfaces for illiterate citizens.")
    add_section("5.6 Recommendations", "The following improvements are recommended:\n1. Introduce stronger user authentication.\n2. Expand dashboard visualisations.\n3. Add systematic security testing.")
    add_section("5.7 Conclusion", "The Agentic RAG-Based Citizen Service Advisory Chatbot presents an integrated approach to information delivery. The web interface, vector database, and language model operate together to serve citizens efficiently.\n\nThe project demonstrates the importance of system-level integration. The quality of the final system depends on the interaction between:\nFrontend -> API -> Vector DB -> LLM -> Response Generator.")
    story.append(PageBreak())

    # --- REFERENCES ---
    story.append(Paragraph("REFERENCES", heading1))
    refs = [
        "1. FocusLink V2 - Cloud-Native IoT Platform for Intelligent Focus Management (Reference Document format standard).",
        "2. Agentic RAG-Based Citizen Service Advisory Chatbot, GitHub repository and README documentation.",
        "3. LangChain/LlamaIndex Documentation, relating to RAG pipeline architectures.",
        "4. FastAPI Technical Documentation, official documentation for Python APIs.",
        "5. Mermaid Documentation, Flowchart Syntax, documentation for creating flowcharts and system diagrams."
    ]
    for r in refs:
        story.append(Paragraph(r, normal))
    
    # Build PDF
    doc.build(story)
    print("Report generated successfully.")

if __name__ == "__main__":
    create_report()
