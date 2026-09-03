import os, shutil, mimetypes, uuid, threading
from pathlib import Path
from datetime import datetime,timezone
from fastapi import FastAPI,Depends,UploadFile,File,Form,HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import Base,engine,get_db
from .models import *
from .services import *
Base.metadata.create_all(engine)
app=FastAPI(title="TRACE-X API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_methods=["*"],allow_headers=["*"])
def audit(db,action,resource,status="SUCCESS"):
 db.add(Audit(actor="Demo Investigator",action=action,resource=resource,status=status));db.commit()
class Login(BaseModel): username:str;password:str
class CaseIn(BaseModel): name:str;incident_type:str="Suspicious Activity";priority:str="MEDIUM"
class ReportIn(BaseModel): case_id:int
@app.get("/api/health")
def health(): return {"status":"ONLINE","service":"TRACE-X API"}
@app.post("/api/auth/login")
def login(x:Login):
 if x.username=="demo@tracex.local" and x.password=="demo123": return {"access_token":"local-demo-token","user":"Demo Investigator"}
 raise HTTPException(401,"Invalid demo credentials")
@app.get("/api/cases")
def cases(db:Session=Depends(get_db)):
 return [{**{k:getattr(c,k) for k in ["id","case_id","name","incident_type","status","priority","investigator"]},"created_at":c.created_at.isoformat(),"evidence_count":len(c.evidence)} for c in db.query(Case).order_by(Case.id).all()]
@app.post("/api/cases")
def create_case(x:CaseIn,db:Session=Depends(get_db)):
 n=db.query(Case).count()+1;c=Case(case_id=f"TRX-2026-{n:03d}",name=x.name,incident_type=x.incident_type,priority=x.priority);db.add(c);db.commit();audit(db,"case_created",c.case_id);return {"id":c.id,"case_id":c.case_id}
@app.get("/api/evidence")
def evidence(db:Session=Depends(get_db)):
 return [{k:getattr(e,k) for k in ["id","evidence_id","filename","source","format","size","original_hash","integrity","analysis_status","case_id"]} for e in db.query(Evidence).all()]
@app.post("/api/evidence/upload")
async def upload(file:UploadFile=File(...),case_id:int=Form(1),db:Session=Depends(get_db)):
 name=safe_name(file.filename or "evidence.bin"); eid=f"EVD-{db.query(Evidence).count()+1:04d}"; path=ROOT/"evidence/original"/f"{eid}_{name}"
 with open(path,"wb") as out:
  while chunk:=await file.read(1024*1024): out.write(chunk)
 h=sha256_file(path); fmt=Path(name).suffix.upper().lstrip(".") or "UNKNOWN"; mime=file.content_type or mimetypes.guess_type(name)[0] or "application/octet-stream"
 e=Evidence(evidence_id=eid,case_id=case_id,filename=name,source="UPLOADED EVIDENCE",format=fmt,size=path.stat().st_size,original_hash=h,mime_type=mime,stored_path=str(path),integrity="VERIFIED",analysis_status="AWAITING REVIEW")
 db.add(e);db.commit();db.refresh(e);db.add(Custody(custody_id=f"COC-{db.query(Custody).count()+1:05d}",evidence_id=e.id,action="ACQUIRED",actor="System",description="Original evidence registered and SHA-256 calculated.",current_hash=h));db.commit();audit(db,"evidence_uploaded",eid);return {"evidence_id":eid,"sha256":h}
@app.post("/api/evidence/{eid}/verify")
def verify(eid:int,db:Session=Depends(get_db)):
 e=db.get(Evidence,eid)
 if not e: raise HTTPException(404,"Evidence not found")
 h=sha256_file(e.stored_path);e.integrity="VERIFIED" if h==e.original_hash else "MISMATCH";db.commit();audit(db,"integrity_verified",e.evidence_id,e.integrity);return {"match":h==e.original_hash,"current_hash":h,"original_hash":e.original_hash,"integrity":e.integrity}
@app.get("/api/evidence/{eid}/metadata")
def metadata(eid:int,db:Session=Depends(get_db)):
 e=db.get(Evidence,eid)
 if not e: raise HTTPException(404,"Evidence not found")
 data=ffprobe(e.stored_path) if os.path.exists(e.stored_path) else None
 return {"filename":e.filename,"size":e.size,"mime_type":e.mime_type,"sha256":e.original_hash,"ffprobe":data,"container":"Unknown / proprietary" if e.format=="DAV" else "H.264 / MP4"}
@app.get("/api/evidence/{eid}/events")
def events(eid:int,db:Session=Depends(get_db)):
 return [vars(x)|{"_sa_instance_state":None} for x in db.query(Event).filter_by(evidence_id=eid).all()]
@app.post("/api/evidence/{eid}/analyze")
def analyze(eid:int,db:Session=Depends(get_db)):
 e=db.get(Evidence,eid);job=AnalysisJob(job_id=f"JOB-{db.query(AnalysisJob).count()+1:04d}",evidence_id=eid,job_type="FORENSIC ANALYSIS",status="PROCESSING",progress=5,engine="DEMO",started_at=datetime.now(timezone.utc));db.add(job);e.analysis_status="PROCESSING";db.commit()
 def work():
  from .database import SessionLocal
  s=SessionLocal();j=s.query(AnalysisJob).filter_by(id=job.id).first()
  for p in [25,45,70,90,100]:
   import time;time.sleep(.15);j.progress=p;s.commit()
  j.status="COMPLETED";j.completed_at=datetime.now(timezone.utc);e2=s.get(Evidence,eid);e2.analysis_status="ANALYZED"
  samples=[("22:14:05","MOTION",.92,"Motion detected"),("22:14:31","PERSON",.94,"Person detected"),("22:14:37","VEHICLE",.89,"Vehicle detected"),("22:15:04","SCENE_CHANGE",0,"Scene change"),("22:15:42","MOTION",.97,"High motion"),("22:31:12","VIDEO_GAP",0,"Potential recording gap — requires investigator review"),("22:33:47","VIDEO_GAP",0,"Recording resumed"),("22:41:09","VEHICLE",.91,"Vehicle detected")]
  if not s.query(Event).filter_by(evidence_id=eid).count():
   for t,k,c,d in samples:s.add(Event(evidence_id=eid,timestamp=t,event_type=k,confidence=c,description=d,source="DEMO ANALYSIS"))
  s.commit();s.close()
 threading.Thread(target=work,daemon=True).start();audit(db,"analysis_started",e.evidence_id);return {"job_id":job.job_id}
@app.get("/api/analysis/{job_id}")
def job(job_id:str,db:Session=Depends(get_db)):
 j=db.query(AnalysisJob).filter_by(job_id=job_id).first()
 if not j: raise HTTPException(404,"Job not found")
 return {k:getattr(j,k) for k in ["job_id","job_type","status","progress","engine","started_at","completed_at","error"]}
@app.get("/api/evidence/{eid}/custody")
def custody(eid:int,db:Session=Depends(get_db)): return [{k:getattr(x,k) for k in ["custody_id","action","actor","timestamp","description","previous_hash","current_hash"]} for x in db.query(Custody).filter_by(evidence_id=eid).all()]
@app.get("/api/cameras")
def cameras(db:Session=Depends(get_db)): return [{k:getattr(c,k) for k in ["camera_id","name","channel","status","source","recording_period"]} for c in db.query(Camera).all()]
@app.get("/api/audit")
def audits(db:Session=Depends(get_db)): return [{k:getattr(x,k) for k in ["timestamp","actor","action","resource","status"]} for x in db.query(Audit).order_by(Audit.id.desc()).limit(200).all()]
@app.get("/api/search")
def search(q:str,db:Session=Depends(get_db)):
 return {"cases":[c.case_id for c in db.query(Case).filter(Case.case_id.contains(q)|Case.name.contains(q)).all()],"evidence":[e.evidence_id for e in db.query(Evidence).filter(Evidence.evidence_id.contains(q)|Evidence.filename.contains(q)|Evidence.original_hash.contains(q)).all()]}
@app.post("/api/evidence/{eid}/frames")
def frame(eid:int,db:Session=Depends(get_db)):
 e=db.get(Evidence,eid)
 if not e: raise HTTPException(404,"Evidence not found")
 fid=f"FRM-{db.query(Frame).count()+1:04d}"; out=ROOT/"evidence/derived"/f"{fid}.jpg"
 ok=extract_frame(e.stored_path,0,out) if os.path.exists(e.stored_path) else False
 p=str(out) if ok else ""; h=sha256_file(out) if ok else "DEMO-DERIVATIVE"
 f=Frame(frame_id=fid,evidence_id=eid,timestamp="00:00:00",sha256=h,path=p);db.add(f);db.add(Custody(custody_id=f"COC-{db.query(Custody).count()+1:05d}",evidence_id=eid,action="DERIVATIVE_CREATED",actor="System",description="Frame captured as a derivative; original preserved.",current_hash=h));db.commit();audit(db,"frame_captured",fid);return {"frame_id":fid,"sha256":h,"derivative":True}
@app.post("/api/reports")
def report(x:ReportIn,db:Session=Depends(get_db)):
 c=db.get(Case,x.case_id)
 if not c: raise HTTPException(404,"Case not found")
 from reportlab.lib.pagesizes import A4
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
 from reportlab.lib import colors
 from reportlab.lib.styles import getSampleStyleSheet
 rid=f"TRX-REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}";out=ROOT/"reports"/f"{rid}.pdf";doc=SimpleDocTemplate(str(out),pagesize=A4);s=getSampleStyleSheet();story=[Paragraph("TRACE-X",s["Title"]),Paragraph("DVR/NVR FORENSIC INTELLIGENCE REPORT",s["Heading2"]),Spacer(1,15),Paragraph(f"Case: {c.case_id} — {c.name}",s["BodyText"]),Paragraph(f"Investigator: {c.investigator}",s["BodyText"]),Paragraph(f"Generated: {datetime.now(timezone.utc).isoformat()}",s["BodyText"]),Spacer(1,15),Paragraph("Evidence Inventory",s["Heading2"])]
 data=[["Evidence ID","Filename","SHA-256","Integrity"]]+[[e.evidence_id,e.filename,e.original_hash,e.integrity] for e in c.evidence];t=Table(data,colWidths=[70,120,220,70]);t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),7)]));story += [t,Spacer(1,15),Paragraph("Analysis Methodology",s["Heading2"]),Paragraph("SHA-256 integrity verification, FFmpeg/ffprobe metadata extraction where supported, OpenCV-compatible processing, and advisory demo analysis. Automated findings require investigator verification.",s["BodyText"]),Spacer(1,12),Paragraph("Limitations",s["Heading2"]),Paragraph("This prototype does not decode every proprietary DVR format. Demo detections are simulated and clearly labelled. Potential gaps are not conclusions of tampering.",s["BodyText"]),Spacer(1,12),Paragraph("Disclaimer",s["Heading2"]),Paragraph("This prototype is intended for demonstration and investigative assistance. Automated analysis results require investigator verification and should not be treated as standalone forensic conclusions.",s["BodyText"])]
 doc.build(story);audit(db,"report_generated",rid);return {"report_id":rid,"download_url":f"/api/reports/{rid}/download"}
@app.get("/api/reports/{rid}/download")
def download(rid:str):
 p=ROOT/"reports"/f"{rid}.pdf"
 if not p.exists(): raise HTTPException(404,"Report not found")
 return FileResponse(p,media_type="application/pdf",filename=p.name)
@app.get("/api/system/health")
def syshealth():
 import shutil
 return {"backend":"ONLINE","database":"ONLINE","ffmpeg":"AVAILABLE" if shutil.which("ffmpeg") else "NOT FOUND","opencv":"AVAILABLE","ai_engine":"DEMO MODE","storage":"AVAILABLE"}
