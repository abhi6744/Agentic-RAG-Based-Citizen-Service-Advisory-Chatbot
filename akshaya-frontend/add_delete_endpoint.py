import sys

endpoint_code = """

@app.delete(
    "/conversations/{conversation_id}",
    tags=["Conversations"],
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    \"\"\"Delete a conversation and its messages.\"\"\"
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete associated messages first
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.delete(conv)
    db.commit()
    return {"status": "success"}
"""

with open('../akshaya-backend/app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

if "def delete_conversation" not in content:
    content = content.replace("app.include_router(chat.router)", endpoint_code + "\napp.include_router(chat.router)")
    with open('../akshaya-backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added DELETE endpoint.")
else:
    print("DELETE endpoint already exists.")
