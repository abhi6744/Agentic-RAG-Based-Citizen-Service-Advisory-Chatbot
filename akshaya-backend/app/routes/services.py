from fastapi import APIRouter
from app.schemas.common import ServiceInfo, ServicesResponse

router = APIRouter()

SUPPORTED_SERVICES = [
    ServiceInfo(
        id="aadhaar",
        name="Aadhaar Services",
        description="Guidance on Aadhaar enrolment, demographic updates (name, address, DOB), biometric updates, and required documents (Proof of Identity, Address, Relationship, Date of Birth).",
        sample_question="My name in Aadhaar doesn't match my certificate  -  how do I update it?",
    ),
    ServiceInfo(
        id="ration_card",
        name="Ration Card Services",
        description="Guidance on new ration card eligibility in Kerala, required documents, AAY/BPL/APL category information, and the application process through Akshaya Centres or Civil Supplies.",
        sample_question="What documents do I need for a new ration card in Kerala?",
    ),
    ServiceInfo(
        id="scholarship",
        name="Scholarship Services",
        description="Guidance on National Scholarship Portal (NSP) eligibility criteria, income limits, category-based schemes, required documents based on scholarship amount, and application stages.",
        sample_question="Am I eligible for a National Scholarship, and what documents are needed?",
    ),
]

@router.get("/services", response_model=ServicesResponse)
def get_services():
    return ServicesResponse(services=SUPPORTED_SERVICES)
