from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Event, Session, SessionSpeaker, Speaker, User
from app.schemas import (
    SessionCreate, SessionUpdate, SessionResponse, SpeakerBrief,
    SpeakerCreate, SpeakerResponse,
)

router = APIRouter(prefix="/api", tags=["Sessions & Speakers"])


def _session_to_response(session: Session) -> SessionResponse:
    speakers = [
        SpeakerBrief(id=ss.speaker.id, name=ss.speaker.name, photo_url=ss.speaker.photo_url)
        for ss in session.speakers
    ]
    return SessionResponse(
        id=session.id,
        event_id=session.event_id,
        title=session.title,
        description=session.description,
        track=session.track,
        room=session.room,
        start_time=session.start_time,
        end_time=session.end_time,
        speakers=speakers,
    )


@router.post("/events/{event_id}/sessions", response_model=SessionResponse, status_code=201)
def create_session(
    event_id: int,
    data: SessionCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check for time conflicts in same track
    if data.track:
        conflicts = db.query(Session).filter(
            Session.event_id == event_id,
            Session.track == data.track,
            Session.start_time < data.end_time,
            Session.end_time > data.start_time,
        ).all()
        if conflicts:
            raise HTTPException(status_code=400, detail="Time conflict with existing session in this track")

    session = Session(
        event_id=event_id,
        title=data.title,
        description=data.description,
        track=data.track,
        room=data.room,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(session)
    db.flush()

    for speaker_id in data.speaker_ids:
        speaker = db.query(Speaker).filter(Speaker.id == speaker_id).first()
        if speaker:
            ss = SessionSpeaker(session_id=session.id, speaker_id=speaker_id)
            db.add(ss)

    db.commit()
    db.refresh(session)
    return _session_to_response(session)


@router.get("/events/{event_id}/sessions", response_model=list[SessionResponse])
def list_sessions(event_id: int, db: DBSession = Depends(get_db)):
    sessions = (
        db.query(Session)
        .filter(Session.event_id == event_id)
        .order_by(Session.start_time)
        .all()
    )
    return [_session_to_response(s) for s in sessions]


@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    data: SessionUpdate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    event = db.query(Event).filter(Event.id == session.event_id).first()
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = data.model_dump(exclude_unset=True)
    speaker_ids = update_data.pop("speaker_ids", None)

    for key, value in update_data.items():
        setattr(session, key, value)

    if speaker_ids is not None:
        db.query(SessionSpeaker).filter(SessionSpeaker.session_id == session_id).delete()
        for speaker_id in speaker_ids:
            ss = SessionSpeaker(session_id=session_id, speaker_id=speaker_id)
            db.add(ss)

    db.commit()
    db.refresh(session)
    return _session_to_response(session)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    event = db.query(Event).filter(Event.id == session.event_id).first()
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.query(SessionSpeaker).filter(SessionSpeaker.session_id == session_id).delete()
    db.delete(session)
    db.commit()


# --- Speakers ---
@router.post("/speakers", response_model=SpeakerResponse, status_code=201)
def create_speaker(
    data: SpeakerCreate,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    speaker = Speaker(name=data.name, bio=data.bio, photo_url=data.photo_url, email=data.email)
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return speaker


@router.get("/speakers", response_model=list[SpeakerResponse])
def list_speakers(db: DBSession = Depends(get_db)):
    return db.query(Speaker).all()


@router.get("/speakers/{speaker_id}", response_model=SpeakerResponse)
def get_speaker(speaker_id: int, db: DBSession = Depends(get_db)):
    speaker = db.query(Speaker).filter(Speaker.id == speaker_id).first()
    if not speaker:
        raise HTTPException(status_code=404, detail="Speaker not found")
    return speaker
