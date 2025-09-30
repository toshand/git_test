"""
要員アサイン管理アプリケーション - データベースモデル

このモジュールには、要員、案件、アサイン管理のためのSQLAlchemyモデルが定義されています。
"""

from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import enum

Base = declarative_base()


class CompanyType(enum.Enum):
    """会社タイプ"""
    KOBELCO = "KOBELCO"
    PARTNER = "PARTNER"


class SkillType(enum.Enum):
    """スキルタイプ"""
    OPEN = "OPEN"
    HOST = "HOST"


class ProficiencyLevel(enum.Enum):
    """習熟度レベル"""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class ProfessionType(enum.Enum):
    """プロフェッションタイプ"""
    EXPERT = "EXPERT"
    PM = "PM"
    DESIGNER = "DESIGNER"
    DEVELOPER = "DEVELOPER"


class DomainType(enum.Enum):
    """専門領域タイプ"""
    PRODUCTION = "PRODUCTION"
    SALES = "SALES"
    PROCUREMENT = "PROCUREMENT"


class ProjectStatus(enum.Enum):
    """案件ステータス"""
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"


class AssignmentType(enum.Enum):
    """アサインタイプ"""
    FULL = "FULL"
    PARTIAL = "PARTIAL"


class AssignmentStatus(enum.Enum):
    """アサインステータス"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    COMPLETED = "COMPLETED"


class Staff(Base):
    """要員モデル"""
    __tablename__ = 'staff'
    
    id = Column(Integer, primary_key=True)
    employee_id = Column(String(50), unique=True, nullable=False, comment='社員ID')
    name = Column(String(100), nullable=False, comment='氏名')
    company_type = Column(Enum(CompanyType), nullable=False, comment='会社タイプ')
    department = Column(String(100), comment='部署')
    email = Column(String(255), comment='メールアドレス')
    phone = Column(String(20), comment='電話番号')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')
    
    # リレーションシップ
    skills = relationship("StaffSkill", back_populates="staff", cascade="all, delete-orphan")
    professions = relationship("StaffProfession", back_populates="staff", cascade="all, delete-orphan")
    domains = relationship("StaffDomain", back_populates="staff", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="staff", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Staff(id={self.id}, name='{self.name}', company_type='{self.company_type.value}')>"


class StaffSkill(Base):
    """要員スキルモデル"""
    __tablename__ = 'staff_skill'
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    skill_type = Column(Enum(SkillType), nullable=False, comment='スキルタイプ')
    proficiency_level = Column(Enum(ProficiencyLevel), nullable=False, comment='習熟度レベル')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="skills")
    
    def __repr__(self) -> str:
        return f"<StaffSkill(staff_id={self.staff_id}, skill_type='{self.skill_type.value}', level='{self.proficiency_level.value}')>"


class StaffProfession(Base):
    """要員プロフェッションモデル"""
    __tablename__ = 'staff_profession'
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    profession_type = Column(Enum(ProfessionType), nullable=False, comment='プロフェッションタイプ')
    experience_years = Column(Integer, default=0, comment='経験年数')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="professions")
    
    def __repr__(self) -> str:
        return f"<StaffProfession(staff_id={self.staff_id}, profession='{self.profession_type.value}', years={self.experience_years})>"


class StaffDomain(Base):
    """要員専門領域モデル"""
    __tablename__ = 'staff_domain'
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    domain_type = Column(Enum(DomainType), nullable=False, comment='専門領域タイプ')
    expertise_level = Column(Enum(ProficiencyLevel), nullable=False, comment='専門性レベル')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="domains")
    
    def __repr__(self) -> str:
        return f"<StaffDomain(staff_id={self.staff_id}, domain='{self.domain_type.value}', level='{self.expertise_level.value}')>"


class Project(Base):
    """案件モデル"""
    __tablename__ = 'project'
    
    id = Column(Integer, primary_key=True)
    project_code = Column(String(50), unique=True, nullable=False, comment='案件コード')
    project_name = Column(String(200), nullable=False, comment='案件名')
    description = Column(Text, comment='案件説明')
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, comment='ステータス')
    start_date = Column(Date, comment='開始日')
    end_date = Column(Date, comment='終了日')
    total_hours = Column(Integer, default=0, comment='総工数（時間）')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')
    
    # リレーションシップ
    requirements = relationship("ProjectRequirement", back_populates="project", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, code='{self.project_code}', name='{self.project_name}')>"


class ProjectRequirement(Base):
    """案件要件モデル"""
    __tablename__ = 'project_requirement'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    domain_type = Column(Enum(DomainType), comment='必要な専門領域')
    skill_type = Column(Enum(SkillType), comment='必要なスキル')
    profession_type = Column(Enum(ProfessionType), comment='必要なプロフェッション')
    required_hours = Column(Integer, default=0, comment='必要工数（時間）')
    priority = Column(Integer, default=1, comment='優先度（1-5）')
    
    # リレーションシップ
    project = relationship("Project", back_populates="requirements")
    
    def __repr__(self) -> str:
        return f"<ProjectRequirement(project_id={self.project_id}, domain='{self.domain_type.value if self.domain_type else None}', hours={self.required_hours})>"


class Assignment(Base):
    """アサインモデル"""
    __tablename__ = 'assignment'
    
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    assignment_type = Column(Enum(AssignmentType), nullable=False, comment='アサインタイプ')
    allocation_percentage = Column(Float, nullable=False, comment='割合（0.0-1.0）')
    start_date = Column(Date, nullable=False, comment='アサイン開始日')
    end_date = Column(Date, nullable=False, comment='アサイン終了日')
    assigned_hours = Column(Integer, default=0, comment='アサイン工数（時間）')
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ACTIVE, comment='ステータス')
    created_at = Column(DateTime, default=datetime.utcnow, comment='作成日時')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新日時')
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="assignments")
    project = relationship("Project", back_populates="assignments")
    
    def __repr__(self) -> str:
        return f"<Assignment(staff_id={self.staff_id}, project_id={self.project_id}, type='{self.assignment_type.value}', allocation={self.allocation_percentage})>"
