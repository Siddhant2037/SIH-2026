import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"backend"))
from app.database import Base,engine,SessionLocal
from app.models import *
Base.metadata.create_all(engine);db=SessionLocal()
if not db.query(User).count(): db.add(User(username="demo@tracex.local",password_hash="DEMO_ONLY",display_name="Demo Investigator"))
if not db.query(Case).count():
 c=Case(case_id="TRX-2026-001",name="Warehouse Perimeter Incident",incident_type="Unauthorized Access",status="ACTIVE",priority="HIGH");db.add(c);db.flush()
 for i,(cid,name,fmt) in enumerate([("EVD-0001","CAM01_20260901_220000.mp4","MP4"),("EVD-0002","CAM02_20260901_220000.mp4","MP4"),("EVD-0003","CAM03_20260901_220000.mp4","MP4"),("EVD-0004","CAM04_20260901_220000.dav","DAV")]):
  e=Evidence(evidence_id=cid,case_id=c.id,filename=name,source="DVR-UNIT-07",format=fmt,size=2800000000,original_hash=f"DEMO-HASH-{i+1:04d}",mime_type="video/mp4" if fmt=="MP4" else "application/octet-stream",stored_path="",integrity="VERIFIED",analysis_status="ANALYZED");db.add(e);db.flush()
  for j,(t,k,conf,desc) in enumerate([("22:14:05","MOTION",.92,"Motion detected"),("22:14:31","PERSON",.94,"Person detected"),("22:14:37","VEHICLE",.89,"Vehicle detected"),("22:15:04","SCENE_CHANGE",0,"Scene change"),("22:15:42","MOTION",.97,"High motion"),("22:31:12","VIDEO_GAP",0,"Potential recording gap — requires investigator review"),("22:33:47","VIDEO_GAP",0,"Recording resumed"),("22:41:09","VEHICLE",.91,"Vehicle detected")]): db.add(Event(evidence_id=e.id,timestamp=t,event_type=k,confidence=conf,description=desc,source="DEMO ANALYSIS"))
  db.add(Custody(custody_id=f"COC-{i+1:05d}",evidence_id=e.id,action="ACQUIRED",actor="System",description="Demo evidence record; static sample hash.",current_hash=e.original_hash))
 for i,(cid,n,ch,st) in enumerate([("CAM-01","Main Gate","01","Online"),("CAM-02","Warehouse Floor","02","Online"),("CAM-03","Parking","03","Offline"),("CAM-04","Rear Gate","04","Online")]):db.add(Camera(camera_id=cid,name=n,channel=ch,status=st,source="DVR-UNIT-07",recording_period="2026-09-01 22:00–23:00"))
db.commit();print("TRACE-X demo environment seeded.")
