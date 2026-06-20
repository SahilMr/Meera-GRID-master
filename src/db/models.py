from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.db.database import Base

class StatusLookup(Base):
    __tablename__ = "status_lookup"

    status_id = Column(Integer, primary_key=True)
    status_label = Column(String(50), unique=True, nullable=False)


class RtiQuery(Base):
    __tablename__ = "rti_query"

    rti_query_id = Column(String(36), primary_key=True)
    inward_id = Column(String(100), nullable=False)
    query_text = Column(Text, nullable=False)
    department_id = Column(Integer, nullable=False)
    status_id = Column(Integer, ForeignKey("status_lookup.status_id"), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    assigned_at = Column(String(50), nullable=True)

    status = relationship("StatusLookup")
    supporting_documents = relationship(
        "SupportingDocument",
        back_populates="rti_query",
        cascade="all, delete-orphan"
    )
    office_notes = relationship(
        "OfficeNote",
        back_populates="rti_query",
        cascade="all, delete-orphan"
    )


class SupportingDocument(Base):
    __tablename__ = "supporting_document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rti_query_id = Column(String(36), ForeignKey("rti_query.rti_query_id"), nullable=False)
    document_url = Column(String(500), nullable=False)

    rti_query = relationship("RtiQuery", back_populates="supporting_documents")


class OfficeNote(Base):
    __tablename__ = "office_note"

    office_note_id = Column(String(36), primary_key=True)
    rti_query_id = Column(String(36), ForeignKey("rti_query.rti_query_id"), nullable=False)
    office_note = Column(Text, nullable=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(String(50), nullable=False)

    rti_query = relationship("RtiQuery", back_populates="office_notes")


class UserQuery(Base):
    __tablename__ = "user_query"

    query_id = Column(String(36), primary_key=True)
    rti_query_id = Column(String(36), ForeignKey("rti_query.rti_query_id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    user_query = Column(Text, nullable=False)
    asst_response = Column(Text, nullable=False)
    created_at = Column(String(50), nullable=False)

    sources = relationship(
        "UserQuerySource",
        back_populates="user_query",
        cascade="all, delete-orphan"
    )


class UserQuerySource(Base):
    __tablename__ = "user_query_source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String(36), ForeignKey("user_query.query_id"), nullable=False)
    source_name = Column(String(200), nullable=False)

    user_query = relationship("UserQuery", back_populates="sources")


class AssistantSuggestion(Base):
    __tablename__ = "assistant_suggestion"

    suggestion_id = Column(String(36), primary_key=True)
    rti_query_id = Column(String(36), ForeignKey("rti_query.rti_query_id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    asst_suggestion = Column(Text, nullable=False)
    created_at = Column(String(50), nullable=False)

    sources = relationship(
        "SuggestionSource",
        back_populates="suggestion",
        cascade="all, delete-orphan"
    )


class SuggestionSource(Base):
    __tablename__ = "suggestion_source"

    id = Column(Integer, primary_key=True, autoincrement=True)
    suggestion_id = Column(String(36), ForeignKey("assistant_suggestion.suggestion_id"), nullable=False)
    source_name = Column(String(200), nullable=False)

    suggestion = relationship("AssistantSuggestion", back_populates="sources")


class DepartmentMappingMaster(Base):
    __tablename__ = "department_mapping_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    office = Column(String(200), nullable=False)
    division_section = Column(String(200), nullable=False)
    sub_section = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    user = Column(String(100), nullable=False)
    uploaded_at = Column(String(50), nullable=False)
