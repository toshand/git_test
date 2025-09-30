"""
サンプルデータ投入スクリプト

要員アサイン管理システムのテスト用サンプルデータを作成します。
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint, uniform

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_database, db_manager
from src.models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    CompanyType, SkillType, ProfessionType, DomainType,
    ProficiencyLevel, ProjectStatus, AssignmentType, AssignmentStatus
)


def create_sample_data():
    """サンプルデータを作成"""
    print("サンプルデータの作成を開始します...")
    
    # データベース初期化
    init_database()
    
    # セッション取得
    session = db_manager.get_session_sync()
    
    try:
        # 既存データをクリア
        print("既存データをクリアしています...")
        session.query(Assignment).delete()
        session.query(ProjectRequirement).delete()
        session.query(StaffDomain).delete()
        session.query(StaffProfession).delete()
        session.query(StaffSkill).delete()
        session.query(Project).delete()
        session.query(Staff).delete()
        session.commit()
        
        # 要員データを作成
        print("要員データを作成しています...")
        staff_list = create_staff_data(session)
        
        # 案件データを作成
        print("案件データを作成しています...")
        project_list = create_project_data(session)
        
        # アサインデータを作成
        print("アサインデータを作成しています...")
        create_assignment_data(session, staff_list, project_list)
        
        session.commit()
        print("サンプルデータの作成が完了しました！")
        
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
        raise
    finally:
        session.close()


def create_staff_data(session):
    """要員データを作成"""
    staff_list = []
    
    # コベルコシステム社員（300名）
    for i in range(1, 301):
        staff = Staff(
            employee_id=f"KSC{i:04d}",
            name=f"コベルコ社員{i}",
            company_type=CompanyType.KOBELCO,
            department=choice(["システム部", "開発部", "運用部", "保守部"]),
            email=f"kobelco{i}@example.com",
            phone=f"03-1234-{i:04d}"
        )
        session.add(staff)
        staff_list.append(staff)
        
        # スキル設定
        create_staff_skills(session, staff)
        
        # プロフェッション設定
        create_staff_professions(session, staff)
        
        # 専門領域設定
        create_staff_domains(session, staff)
    
    # パートナー企業要員（200名）
    for i in range(1, 201):
        staff = Staff(
            employee_id=f"PTN{i:04d}",
            name=f"パートナー要員{i}",
            company_type=CompanyType.PARTNER,
            department=choice(["パートナーA", "パートナーB", "パートナーC"]),
            email=f"partner{i}@example.com",
            phone=f"03-5678-{i:04d}"
        )
        session.add(staff)
        staff_list.append(staff)
        
        # スキル設定
        create_staff_skills(session, staff)
        
        # プロフェッション設定
        create_staff_professions(session, staff)
        
        # 専門領域設定
        create_staff_domains(session, staff)
    
    return staff_list


def create_staff_skills(session, staff):
    """要員のスキルを設定"""
    # ランダムに1-2個のスキルを設定（重複を避ける）
    num_skills = randint(1, 2)
    skills = [SkillType.OPEN, SkillType.HOST]
    selected_skills = []
    
    for _ in range(num_skills):
        skill_type = choice(skills)
        if skill_type not in selected_skills:
            selected_skills.append(skill_type)
            proficiency = choice(list(ProficiencyLevel))
            
            skill = StaffSkill(
                staff_id=staff.id,
                skill_type=skill_type,
                proficiency_level=proficiency
            )
            session.add(skill)


def create_staff_professions(session, staff):
    """要員のプロフェッションを設定"""
    # ランダムに1-2個のプロフェッションを設定（重複を避ける）
    num_professions = randint(1, 2)
    professions = list(ProfessionType)
    selected_professions = []
    
    for _ in range(num_professions):
        profession_type = choice(professions)
        if profession_type not in selected_professions:
            selected_professions.append(profession_type)
            experience_years = randint(1, 15)
            
            profession = StaffProfession(
                staff_id=staff.id,
                profession_type=profession_type,
                experience_years=experience_years
            )
            session.add(profession)


def create_staff_domains(session, staff):
    """要員の専門領域を設定"""
    # ランダムに1-2個の専門領域を設定（重複を避ける）
    num_domains = randint(1, 2)
    domains = list(DomainType)
    selected_domains = []
    
    for _ in range(num_domains):
        domain_type = choice(domains)
        if domain_type not in selected_domains:
            selected_domains.append(domain_type)
            expertise_level = choice(list(ProficiencyLevel))
            
            domain = StaffDomain(
                staff_id=staff.id,
                domain_type=domain_type,
                expertise_level=expertise_level
            )
            session.add(domain)


def create_project_data(session):
    """案件データを作成"""
    project_list = []
    
    project_templates = [
        {
            "code": "SYS001",
            "name": "基幹システム運用保守",
            "description": "基幹システムの運用・保守業務",
            "total_hours": 2000,
            "requirements": [
                {"domain": DomainType.PRODUCTION, "skill": SkillType.HOST, "profession": ProfessionType.DEVELOPER, "hours": 1000},
                {"domain": DomainType.PRODUCTION, "skill": SkillType.HOST, "profession": ProfessionType.EXPERT, "hours": 1000}
            ]
        },
        {
            "code": "SYS002", 
            "name": "販売管理システム開発",
            "description": "販売管理システムの新規開発",
            "total_hours": 3000,
            "requirements": [
                {"domain": DomainType.SALES, "skill": SkillType.OPEN, "profession": ProfessionType.DESIGNER, "hours": 1500},
                {"domain": DomainType.SALES, "skill": SkillType.OPEN, "profession": ProfessionType.DEVELOPER, "hours": 1500}
            ]
        },
        {
            "code": "SYS003",
            "name": "調達システム保守",
            "description": "調達システムの保守・改修",
            "total_hours": 1500,
            "requirements": [
                {"domain": DomainType.PROCUREMENT, "skill": SkillType.OPEN, "profession": ProfessionType.DEVELOPER, "hours": 1500}
            ]
        }
    ]
    
    for template in project_templates:
        project = Project(
            project_code=template["code"],
            project_name=template["name"],
            description=template["description"],
            status=choice(list(ProjectStatus)),
            start_date=date.today() + timedelta(days=randint(-30, 30)),
            end_date=date.today() + timedelta(days=randint(90, 365)),
            total_hours=template["total_hours"]
        )
        session.add(project)
        project_list.append(project)
        
        # 案件要件を作成
        for req in template["requirements"]:
            requirement = ProjectRequirement(
                project_id=project.id,
                domain_type=req["domain"],
                skill_type=req["skill"],
                profession_type=req["profession"],
                required_hours=req["hours"],
                priority=randint(1, 5)
            )
            session.add(requirement)
    
    return project_list


def create_assignment_data(session, staff_list, project_list):
    """アサインデータを作成"""
    # 各案件に対してランダムに要員をアサイン
    for project in project_list:
        # 案件に必要な要員数を決定（2-5名）
        num_assignments = randint(2, 5)
        
        # ランダムに要員を選択
        selected_staff = choice(staff_list, num_assignments)
        
        for staff in selected_staff:
            assignment_type = choice(list(AssignmentType))
            allocation_percentage = uniform(0.2, 1.0) if assignment_type == AssignmentType.PARTIAL else 1.0
            
            assignment = Assignment(
                staff_id=staff.id,
                project_id=project.id,
                assignment_type=assignment_type,
                allocation_percentage=allocation_percentage,
                start_date=project.start_date,
                end_date=project.end_date,
                assigned_hours=int(project.total_hours * allocation_percentage / num_assignments),
                status=AssignmentStatus.ACTIVE
            )
            session.add(assignment)


if __name__ == "__main__":
    create_sample_data()
