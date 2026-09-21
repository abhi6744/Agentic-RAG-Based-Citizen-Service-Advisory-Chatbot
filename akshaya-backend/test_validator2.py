from app.services.citation_validator import validate_response

chunks = [{"text": "You need an ID proof and address proof for Aadhaar update. Accepted documents include PAN card and Voter ID."}]

res1 = validate_response("To update your Aadhaar, you must provide an ID proof and address proof, such as a Voter ID or PAN card.", chunks)
print("Valid claim:", res1.is_valid)

res2 = validate_response("To update your Aadhaar, you must pay 500 rupees and provide a DNA sample.", chunks)
print("Invalid claim:", res2.is_valid, res2.unsupported_claims)
