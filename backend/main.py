import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib, json, asyncio, base64

from database import init_db, get_db, Client, User, Lead, CallLog, Campaign
from ai_agent import get_ai_response, analyze_sentiment, generate_opening
from lead_scorer import score_lead_from_keywords, get_lead_recommendation
try:
    from voice_caller import make_call, generate_answer_twiml, text_to_speech_elevenlabs, speech_to_text_deepgram, active_voice_calls, end_voice_call, get_call_status
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False
    active_voice_calls = {}
from config import HOST, PORT


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(title="AI Caller - SaaS Platform", version="2.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ===== HELPERS =====

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_client(client_id: str = Header(None, alias="x-client-id"), db: Session = Depends(get_db)):
    if not client_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    client = db.query(Client).filter(Client.id == int(client_id)).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid client")
    return client


# ===== SCHEMAS =====

class ClientRegister(BaseModel):
    company_name: str
    industry: str
    contact_name: str
    email: str
    phone: str
    password: str
    product_info: str
    ai_name: Optional[str] = "Alex"

class ClientLogin(BaseModel):
    email: str
    password: str

class ClientUpdate(BaseModel):
    product_info: Optional[str] = None
    ai_script: Optional[str] = None
    ai_name: Optional[str] = None
    ai_tone: Optional[str] = None

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    company: Optional[str] = None

class CallRequest(BaseModel):
    lead_id: int

class ChatMessage(BaseModel):
    message: str

class CampaignCreate(BaseModel):
    name: str
    script: str
    product_info: str


# ===== AUTH ENDPOINTS =====

@app.get("/")
def home():
    return {"message": "AI Caller SaaS Platform", "version": "2.0", "status": "running"}

@app.post("/auth/register")
def register(data: ClientRegister, db: Session = Depends(get_db)):
    existing = db.query(Client).filter(Client.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    client = Client(
        company_name=data.company_name,
        industry=data.industry,
        contact_name=data.contact_name,
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password),
        product_info=data.product_info,
        ai_name=data.ai_name or "Alex"
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"message": "Registration successful", "client_id": client.id, "company": client.company_name}

@app.post("/auth/login")
def login(data: ClientLogin, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.email == data.email, Client.password == hash_password(data.password)).first()
    if not client:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"client_id": client.id, "company_name": client.company_name, "contact_name": client.contact_name, "industry": client.industry, "product_info": client.product_info, "ai_name": client.ai_name}

@app.post("/auth/team-login")
def team_login(data: ClientLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.password == hash_password(data.password)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    client = db.query(Client).filter(Client.id == user.client_id).first()
    return {"client_id": user.client_id, "company_name": client.company_name if client else "", "contact_name": user.name, "role": user.role, "permissions": user.permissions, "industry": client.industry if client else "", "product_info": client.product_info if client else ""}

@app.get("/auth/profile")
def get_profile(client: Client = Depends(get_current_client)):
    return {"id": client.id, "company_name": client.company_name, "industry": client.industry, "contact_name": client.contact_name, "email": client.email, "product_info": client.product_info, "ai_name": client.ai_name, "ai_tone": client.ai_tone, "plan": client.plan, "total_calls": client.total_calls}

@app.put("/auth/profile")
def update_profile(data: ClientUpdate, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    if data.product_info: client.product_info = data.product_info
    if data.ai_script: client.ai_script = data.ai_script
    if data.ai_name: client.ai_name = data.ai_name
    if data.ai_tone: client.ai_tone = data.ai_tone
    db.commit()
    return {"message": "Profile updated"}


# ===== LEADS (Client-Isolated) =====

@app.post("/leads")
def add_lead(lead: LeadCreate, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    new_lead = Lead(client_id=client.id, name=lead.name, phone=lead.phone, email=lead.email, company=lead.company)
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return {"message": f"Lead '{lead.name}' added", "id": new_lead.id}

@app.get("/leads")
def get_leads(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.client_id == client.id).all()
    return {"total": len(leads), "leads": leads}

@app.get("/leads/{lead_id}")
def get_lead(lead_id: int, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.client_id == client.id).first()
    if not lead: raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.get("/leads/category/{category}")
def get_leads_by_category(category: str, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    leads = db.query(Lead).filter(Lead.client_id == client.id, Lead.category == category).all()
    return {"category": category, "total": len(leads), "leads": leads}

@app.post("/leads/upload-csv")
async def upload_csv(file: UploadFile = File(...), client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    import csv, io
    content = await file.read()
    text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    count = 0
    for row in reader:
        lead = Lead(client_id=client.id, name=row.get('name', '').strip(), phone=row.get('phone', '').strip(), email=row.get('email', '').strip() or None, company=row.get('company', '').strip() or None)
        if lead.name and lead.phone:
            db.add(lead)
            count += 1
    db.commit()
    return {"message": f"{count} leads uploaded", "count": count}


# ===== CALL SIMULATOR (Client-Isolated) =====

active_conversations = {}

@app.post("/call/start")
def start_call(request: CallRequest, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == request.lead_id, Lead.client_id == client.id).first()
    if not lead: raise HTTPException(status_code=404, detail="Lead not found")

    product_info = client.product_info or "General product"
    opening = generate_opening(lead.name, product_info)

    conversation_id = f"call_{client.id}_{lead.id}_{int(datetime.now().timestamp())}"
    active_conversations[conversation_id] = {
        "client_id": client.id,
        "lead_id": lead.id,
        "lead_name": lead.name,
        "product_info": product_info,
        "history": [{"role": "assistant", "content": opening}],
        "started_at": datetime.now().isoformat()
    }

    lead.status = "called"
    db.commit()
    return {"conversation_id": conversation_id, "ai_message": opening, "lead_name": lead.name}

@app.post("/call/respond")
def respond_to_call(conversation_id: str, msg: ChatMessage, client: Client = Depends(get_current_client)):
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv = active_conversations[conversation_id]
    conv["history"].append({"role": "user", "content": msg.message})
    ai_response = get_ai_response(conv["history"], conv["product_info"])
    conv["history"].append({"role": "assistant", "content": ai_response})
    return {"ai_message": ai_response, "turn": len(conv["history"]) // 2}

@app.post("/call/end")
def end_call(conversation_id: str, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    if conversation_id not in active_conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv = active_conversations[conversation_id]
    analysis = analyze_sentiment(conv["history"])

    call_log = CallLog(client_id=client.id, lead_id=conv["lead_id"], lead_name=conv["lead_name"], phone="simulated", duration_seconds=len(conv["history"]) * 15, transcript=json.dumps(conv["history"]), sentiment=analysis.get("sentiment", "neutral"), lead_score=analysis.get("score", 5), category=analysis.get("category", "warm"), summary=analysis.get("summary", ""), call_status="completed")
    db.add(call_log)

    lead = db.query(Lead).filter(Lead.id == conv["lead_id"]).first()
    if lead:
        lead.score = analysis.get("score", 5)
        lead.category = analysis.get("category", "warm")
        lead.status = "qualified"
        lead.notes = analysis.get("summary", "")

    client.total_calls += 1
    db.commit()
    del active_conversations[conversation_id]
    return {"status": "call_ended", "analysis": analysis, "recommendation": get_lead_recommendation(analysis.get("category", "cold"))}


# ===== CALL LOGS =====

@app.get("/calls")
def get_calls(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    calls = db.query(CallLog).filter(CallLog.client_id == client.id).all()
    return {"total": len(calls), "calls": calls}


# ===== CAMPAIGNS =====

@app.post("/campaigns")
def create_campaign(campaign: CampaignCreate, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    new_campaign = Campaign(client_id=client.id, name=campaign.name, script=campaign.script, product_info=campaign.product_info)
    db.add(new_campaign)
    db.commit()
    return {"message": f"Campaign '{campaign.name}' created", "id": new_campaign.id}

@app.get("/campaigns")
def get_campaigns(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter(Campaign.client_id == client.id).all()
    return {"total": len(campaigns), "campaigns": campaigns}


# ===== DASHBOARD =====

@app.get("/dashboard/stats")
def get_stats(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    total_leads = db.query(Lead).filter(Lead.client_id == client.id).count()
    hot = db.query(Lead).filter(Lead.client_id == client.id, Lead.category == "hot").count()
    warm = db.query(Lead).filter(Lead.client_id == client.id, Lead.category == "warm").count()
    cold = db.query(Lead).filter(Lead.client_id == client.id, Lead.category == "cold").count()
    total_calls = db.query(CallLog).filter(CallLog.client_id == client.id).count()
    return {"total_leads": total_leads, "hot_leads": hot, "warm_leads": warm, "cold_leads": cold, "total_calls": total_calls, "conversion_rate": f"{(hot / max(total_leads, 1)) * 100:.1f}%"}


# ===== EXPORT =====

@app.get("/export/leads")
def export_leads(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    import csv, io
    leads = db.query(Lead).filter(Lead.client_id == client.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Phone', 'Email', 'Company', 'Score', 'Category', 'Status'])
    for l in leads:
        writer.writerow([l.name, l.phone, l.email or '', l.company or '', l.score, l.category, l.status])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=leads_export.csv"})

@app.get("/export/calls")
def export_calls(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    import csv, io
    calls = db.query(CallLog).filter(CallLog.client_id == client.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Lead Name', 'Duration(s)', 'Sentiment', 'Score', 'Category', 'Summary'])
    for c in calls:
        writer.writerow([c.lead_name, c.duration_seconds, c.sentiment, c.lead_score, c.category, c.summary or ''])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=calls_export.csv"})


# ===== TEAM MANAGEMENT (Client Admin) =====

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "agent"  # admin, manager, agent
    permissions: str = "dashboard,leads,calls"  # comma-separated pages

@app.post("/team/add")
def add_team_member(user: UserCreate, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Client admin adds team member"""
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    if user.role not in ['admin', 'manager', 'agent']:
        raise HTTPException(status_code=400, detail="Role must be admin, manager, or agent")
    new_user = User(client_id=client.id, name=user.name, email=user.email, password=hash_password(user.password), role=user.role, permissions=user.permissions)
    db.add(new_user)
    db.commit()
    return {"message": f"{user.name} added as {user.role}", "id": new_user.id}

@app.get("/team")
def get_team(client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Get all team members"""
    users = db.query(User).filter(User.client_id == client.id).all()
    return {"total": len(users), "team": [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "permissions": u.permissions, "is_active": u.is_active} for u in users]}

@app.put("/team/{user_id}/role")
def change_role(user_id: int, role: str, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Change team member role"""
    user = db.query(User).filter(User.id == user_id, User.client_id == client.id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if role not in ['admin', 'manager', 'agent']: raise HTTPException(status_code=400, detail="Invalid role")
    user.role = role
    db.commit()
    return {"message": f"{user.name} role changed to {role}"}

@app.put("/team/{user_id}/permissions")
def update_permissions(user_id: int, permissions: str, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Update which pages a user can access"""
    user = db.query(User).filter(User.id == user_id, User.client_id == client.id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.permissions = permissions
    db.commit()
    return {"message": f"{user.name} permissions updated"}

@app.put("/team/{user_id}/toggle")
def toggle_user(user_id: int, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Activate/Deactivate team member"""
    user = db.query(User).filter(User.id == user_id, User.client_id == client.id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"{user.name} {'activated' if user.is_active else 'deactivated'}"}

@app.delete("/team/{user_id}")
def remove_user(user_id: int, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Remove team member"""
    user = db.query(User).filter(User.id == user_id, User.client_id == client.id).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"{user.name} removed"}


# ===== SUPER ADMIN =====

@app.get("/admin/clients")
def get_all_clients(admin_key: str = Header(None, alias="x-admin-key"), db: Session = Depends(get_db)):
    if admin_key != "superadmin123":
        raise HTTPException(status_code=403, detail="Admin access only")
    clients = db.query(Client).all()
    return {"total": len(clients), "clients": [{"id": c.id, "company": c.company_name, "industry": c.industry, "email": c.email, "plan": c.plan, "total_calls": c.total_calls, "is_active": c.is_active, "created": str(c.created_at)} for c in clients]}

@app.put("/admin/clients/{client_id}/plan")
def change_plan(client_id: int, plan: str, admin_key: str = Header(None, alias="x-admin-key"), db: Session = Depends(get_db)):
    if admin_key != "superadmin123": raise HTTPException(status_code=403, detail="Admin access only")
    if plan not in ['free', 'basic', 'pro']: raise HTTPException(status_code=400, detail="Plan must be free, basic, or pro")
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    client.plan = plan
    db.commit()
    return {"message": f"{client.company_name} plan changed to {plan}"}

@app.put("/admin/clients/{client_id}/toggle")
def toggle_client(client_id: int, admin_key: str = Header(None, alias="x-admin-key"), db: Session = Depends(get_db)):
    if admin_key != "superadmin123": raise HTTPException(status_code=403, detail="Admin access only")
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    client.is_active = not client.is_active
    db.commit()
    return {"message": f"{client.company_name} {'activated' if client.is_active else 'deactivated'}"}

@app.put("/admin/clients/{client_id}/reset-password")
def admin_reset_password(client_id: int, new_password: str, admin_key: str = Header(None, alias="x-admin-key"), db: Session = Depends(get_db)):
    if admin_key != "superadmin123": raise HTTPException(status_code=403, detail="Admin access only")
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    client.password = hash_password(new_password)
    db.commit()
    return {"message": f"Password reset for {client.company_name}"}


# ===== VOICE CALLING (Real Phone Calls) =====

class VoiceCallRequest(BaseModel):
    lead_id: int

@app.post("/voice/call")
def initiate_voice_call(req: VoiceCallRequest, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Start a real AI phone call to a lead"""
    if not VOICE_ENABLED:
        raise HTTPException(status_code=501, detail="Voice calling not configured. Install twilio, deepgram-sdk, elevenlabs packages.")
    lead = db.query(Lead).filter(Lead.id == req.lead_id, Lead.client_id == client.id).first()
    if not lead: raise HTTPException(status_code=404, detail="Lead not found")
    if not lead.phone: raise HTTPException(status_code=400, detail="Lead has no phone number")

    opening = generate_opening(lead.name, client.product_info or "our product")
    result = make_call(lead.phone, lead.id, client.id, opening)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    lead.status = "calling"
    db.commit()
    return result

@app.post("/voice/webhook/answer")
async def voice_answer_webhook(request: Request, call_id: str = ""):
    """Twilio calls this when person picks up"""
    twiml = generate_answer_twiml(call_id)
    return Response(content=twiml, media_type="application/xml")

@app.post("/voice/webhook/status")
async def voice_status_webhook(request: Request, call_id: str = ""):
    """Twilio sends call status updates here"""
    form = await request.form()
    status = form.get("CallStatus", "")
    if call_id in active_voice_calls:
        active_voice_calls[call_id]["status"] = status
    return {"ok": True}

@app.websocket("/voice/ws/{call_id}")
async def voice_websocket(websocket: WebSocket, call_id: str):
    """Real-time audio streaming: Twilio <-> AI Agent"""
    await websocket.accept()

    if call_id not in active_voice_calls:
        await websocket.close()
        return

    call_data = active_voice_calls[call_id]
    call_data["status"] = "connected"
    audio_buffer = b""
    stream_sid = None

    # Send opening message as speech
    opening_audio = await text_to_speech_elevenlabs(call_data["opening_message"])
    if opening_audio:
        payload = base64.b64encode(opening_audio).decode("utf-8")
        # Wait for stream SID before sending

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                call_data["stream_sid"] = stream_sid
                # Send opening TTS
                if opening_audio:
                    audio_payload = base64.b64encode(opening_audio).decode("utf-8")
                    await websocket.send_json({"event": "media", "streamSid": stream_sid, "media": {"payload": audio_payload}})
                    call_data["transcript"].append({"role": "assistant", "content": call_data["opening_message"]})

            elif event == "media":
                # Incoming audio from caller
                chunk = base64.b64decode(data["media"]["payload"])
                audio_buffer += chunk

                # Process every ~2 seconds of audio (16000 bytes ≈ 2s at 8kHz mulaw)
                if len(audio_buffer) >= 16000:
                    transcript = await speech_to_text_deepgram(audio_buffer)
                    audio_buffer = b""

                    if transcript.strip():
                        call_data["transcript"].append({"role": "user", "content": transcript})

                        # Get AI response
                        ai_reply = get_ai_response(call_data["transcript"], call_data.get("product_info", ""))
                        call_data["transcript"].append({"role": "assistant", "content": ai_reply})

                        # Convert to speech and send back
                        reply_audio = await text_to_speech_elevenlabs(ai_reply)
                        if reply_audio and stream_sid:
                            audio_payload = base64.b64encode(reply_audio).decode("utf-8")
                            await websocket.send_json({"event": "media", "streamSid": stream_sid, "media": {"payload": audio_payload}})

            elif event == "stop":
                break

    except WebSocketDisconnect:
        pass
    finally:
        call_data["status"] = "completed"

@app.post("/voice/end")
def end_active_call(call_id: str, client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """End an active voice call and get analysis"""
    result = end_voice_call(call_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    call_data = active_voice_calls.get(call_id, {})
    transcript = call_data.get("transcript", [])

    if transcript:
        analysis = analyze_sentiment(transcript)
        call_log = CallLog(client_id=client.id, lead_id=call_data["lead_id"], lead_name="Voice Call", phone="real", duration_seconds=len(transcript) * 15, transcript=json.dumps(transcript), sentiment=analysis.get("sentiment", "neutral"), lead_score=analysis.get("score", 5), category=analysis.get("category", "warm"), summary=analysis.get("summary", ""), call_status="completed")
        db.add(call_log)
        client.total_calls += 1
        db.commit()
        return {"status": "ended", "analysis": analysis}

    return {"status": "ended", "analysis": None}

@app.get("/voice/status/{call_id}")
def voice_call_status(call_id: str, client: Client = Depends(get_current_client)):
    """Check status of an active voice call"""
    return get_call_status(call_id)


# ===== RUN =====

if __name__ == "__main__":
    import uvicorn
    print("\nStarting AI Caller SaaS Platform v2.0...")
    print(f"API Docs: http://localhost:{PORT}/docs")
    print(f"Server: http://localhost:{PORT}")
    print(f"Voice Calls: Enabled (Twilio + Deepgram + ElevenLabs)\n")
    uvicorn.run(app, host=HOST, port=PORT)
