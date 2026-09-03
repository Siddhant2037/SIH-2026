from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,Text,Float,BigInteger
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime,timezone
now=lambda:datetime.now(timezone.utc)
class User(Base):
 __tablename__="users"; id=Column(Integer,primary_key=True); username=Column(String,unique=True); password_hash=Column(String); display_name=Column(String)
class Case(Base):
 __tablename__="cases"; id=Column(Integer,primary_key=True); case_id=Column(String,unique=True); name=Column(String); incident_type=Column(String); status=Column(String,default="ACTIVE"); priority=Column(String,default="MEDIUM"); investigator=Column(String,default="Demo Investigator"); created_at=Column(DateTime,default=now)
 evidence=relationship("Evidence",back_populates="case")
class Evidence(Base):
 __tablename__="evidence"; id=Column(Integer,primary_key=True); evidence_id=Column(String,unique=True); case_id=Column(Integer,ForeignKey("cases.id")); filename=Column(String); source=Column(String); format=Column(String); size=Column(BigInteger); original_hash=Column(String); mime_type=Column(String); stored_path=Column(String); acquired_at=Column(DateTime,default=now); integrity=Column(String,default="VERIFIED"); analysis_status=Column(String,default="AWAITING REVIEW")
 case=relationship("Case",back_populates="evidence")
class Event(Base):
 __tablename__="events"; id=Column(Integer,primary_key=True); evidence_id=Column(Integer,ForeignKey("evidence.id")); timestamp=Column(String); event_type=Column(String); confidence=Column(Float); description=Column(String); source=Column(String,default="DEMO ANALYSIS")
class AnalysisJob(Base):
 __tablename__="analysis_jobs"; id=Column(Integer,primary_key=True); job_id=Column(String,unique=True); evidence_id=Column(Integer,ForeignKey("evidence.id")); job_type=Column(String); status=Column(String); progress=Column(Integer); engine=Column(String); started_at=Column(DateTime); completed_at=Column(DateTime); error=Column(Text)
class Custody(Base):
 __tablename__="custody"; id=Column(Integer,primary_key=True); custody_id=Column(String,unique=True); evidence_id=Column(Integer,ForeignKey("evidence.id")); action=Column(String); actor=Column(String); timestamp=Column(DateTime,default=now); description=Column(String); previous_hash=Column(String); current_hash=Column(String)
class Audit(Base):
 __tablename__="audit"; id=Column(Integer,primary_key=True); timestamp=Column(DateTime,default=now); actor=Column(String); action=Column(String); resource=Column(String); status=Column(String)
class Camera(Base):
 __tablename__="cameras"; id=Column(Integer,primary_key=True); camera_id=Column(String,unique=True); name=Column(String); channel=Column(String); status=Column(String); source=Column(String); recording_period=Column(String)
class Frame(Base):
 __tablename__="frames"; id=Column(Integer,primary_key=True); frame_id=Column(String,unique=True); evidence_id=Column(Integer); timestamp=Column(String); sha256=Column(String); path=Column(String); created_at=Column(DateTime,default=now)
