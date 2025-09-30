"""
サンプルデータ作成スクリプト

データベースにサンプルデータを作成します。
"""

import sys
import os
from datetime import datetime, date, timedelta
from random import choice, randint, uniform, sample

# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import init_database, db_manager
from models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    CompanyType, SkillType, ProficiencyLevel, ProfessionType, DomainType,
    ProjectStatus, AssignmentType, AssignmentStatus
)


def create_sample_data():
    """サンプルデータを作成"""
    print("サンプルデータを作成中...")
    
    # データベースを初期化
    init_database()
    
    session = db_manager.get_session_sync()
    try:
        # 既存データをクリア
        session.query(Assignment).delete()
        session.query(ProjectRequirement).delete()
        session.query(StaffSkill).delete()
        session.query(StaffProfession).delete()
        session.query(StaffDomain).delete()
        session.query(Project).delete()
        session.query(Staff).delete()
        session.commit()
        
        # 要員データを作成
        staff_list = create_staff_data(session)
        session.commit()
        print(f"要員データを作成しました: {len(staff_list)}名")
        
        # 案件データを作成
        project_list = create_project_data(session)
        session.commit()
        print(f"案件データを作成しました: {len(project_list)}件")
        
        # 要員スキル・プロフェッション・専門領域を作成
        create_staff_skills(session, staff_list)
        create_staff_professions(session, staff_list)
        create_staff_domains(session, staff_list)
        session.commit()
        print("要員のスキル・プロフェッション・専門領域を作成しました")
        
        # 案件要件を作成
        create_project_requirements(session, project_list)
        session.commit()
        print("案件要件を作成しました")
        
        # アサインデータを作成
        create_assignments(session, staff_list, project_list)
        session.commit()
        print("アサインデータを作成しました")
        print("サンプルデータの作成が完了しました！")
    finally:
        session.close()


def create_staff_data(session):
    """要員データを作成"""
    staff_list = []
    
    # コベルコシステム社員
    kobelco_names = [
        "田中太郎", "佐藤花子", "鈴木一郎", "高橋美咲", "山田健太",
        "渡辺真理", "伊藤正雄", "中村由美", "小林和也", "加藤恵子",
        "吉田大輔", "斎藤香織", "松本直樹", "井上麻衣", "木村拓也",
        "林美穂", "森田健一", "清水智子", "石川雄一", "阿部恵美"
    ]
    
    for i, name in enumerate(kobelco_names):
        staff = Staff(
            employee_id=f"KSC{i+1:03d}",
            name=name,
            company_type=CompanyType.KOBELCO,
            department=f"開発部{i%3+1}",
            email=f"{name.lower().replace(' ', '.')}@kobelco.co.jp",
            phone=f"03-1234-{i+1000:04d}"
        )
        session.add(staff)
        staff_list.append(staff)
    
    # パートナー企業要員
    partner_names = [
        "山本健二", "田村由香", "佐々木正", "原田智子", "村上雄一",
        "岡田美香", "西村健太", "福田真理", "藤田正樹", "石田恵子",
        "小川直樹", "森本香織", "大野健一", "松井美穂", "野口正雄",
        "中島恵美", "上田健太", "前田真理", "長谷川正樹", "小松恵子"
    ]
    
    for i, name in enumerate(partner_names):
        staff = Staff(
            employee_id=f"PT{i+1:03d}",
            name=name,
            company_type=CompanyType.PARTNER,
            department=f"パートナー企業{i%2+1}",
            email=f"{name.lower().replace(' ', '.')}@partner.co.jp",
            phone=f"03-5678-{i+2000:04d}"
        )
        session.add(staff)
        staff_list.append(staff)
    
    return staff_list


def create_project_data(session):
    """案件データを作成"""
    project_list = []
    
    projects = [
        {
            "project_code": "PRJ001",
            "project_name": "生産管理システム改修",
            "description": "既存の生産管理システムの機能拡張とパフォーマンス改善",
            "status": ProjectStatus.ACTIVE,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "total_hours": 2000
        },
        {
            "project_code": "PRJ002", 
            "project_name": "販売管理システム新規開発",
            "description": "新しい販売管理システムの設計・開発・テスト",
            "status": ProjectStatus.ACTIVE,
            "start_date": date(2024, 2, 1),
            "end_date": date(2024, 11, 30),
            "total_hours": 3000
        },
        {
            "project_code": "PRJ003",
            "project_name": "調達管理システム統合",
            "description": "複数の調達システムを統合し、一元管理を実現",
            "status": ProjectStatus.PLANNING,
            "start_date": date(2024, 4, 1),
            "end_date": date(2025, 3, 31),
            "total_hours": 2500
        },
        {
            "project_code": "PRJ004",
            "project_name": "基幹システム保守",
            "description": "既存基幹システムの日常保守・障害対応",
            "status": ProjectStatus.ACTIVE,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "total_hours": 1500
        },
        {
            "project_code": "PRJ005",
            "project_name": "データ分析基盤構築",
            "description": "ビッグデータ分析のための基盤システム構築",
            "status": ProjectStatus.ACTIVE,
            "start_date": date(2024, 3, 1),
            "end_date": date(2024, 10, 31),
            "total_hours": 1800
        }
    ]
    
    for project_data in projects:
        project = Project(**project_data)
        session.add(project)
        project_list.append(project)
    
    return project_list


def create_staff_skills(session, staff_list):
    """要員スキルを作成"""
    for staff in staff_list:
        # ランダムに1-3個のスキルを追加
        num_skills = randint(1, 3)
        selected_skills = sample(list(SkillType), min(num_skills, len(list(SkillType))))
        
        for skill_type in selected_skills:
            # 重複チェック
            existing = session.query(StaffSkill).filter(
                StaffSkill.staff_id == staff.id,
                StaffSkill.skill_type == skill_type
            ).first()
            
            if not existing:
                skill = StaffSkill(
                    staff_id=staff.id,
                    skill_type=skill_type,
                    proficiency_level=choice(list(ProficiencyLevel))
                )
                session.add(skill)


def create_staff_professions(session, staff_list):
    """要員プロフェッションを作成"""
    for staff in staff_list:
        # ランダムに1-2個のプロフェッションを追加
        num_professions = randint(1, 2)
        selected_professions = sample(list(ProfessionType), min(num_professions, len(list(ProfessionType))))
        
        for profession_type in selected_professions:
            # 重複チェック
            existing = session.query(StaffProfession).filter(
                StaffProfession.staff_id == staff.id,
                StaffProfession.profession_type == profession_type
            ).first()
            
            if not existing:
                profession = StaffProfession(
                    staff_id=staff.id,
                    profession_type=profession_type,
                    experience_years=randint(1, 15)
                )
                session.add(profession)


def create_staff_domains(session, staff_list):
    """要員専門領域を作成"""
    for staff in staff_list:
        # ランダムに1-2個の専門領域を追加
        num_domains = randint(1, 2)
        selected_domains = sample(list(DomainType), min(num_domains, len(list(DomainType))))
        
        for domain_type in selected_domains:
            # 重複チェック
            existing = session.query(StaffDomain).filter(
                StaffDomain.staff_id == staff.id,
                StaffDomain.domain_type == domain_type
            ).first()
            
            if not existing:
                domain = StaffDomain(
                    staff_id=staff.id,
                    domain_type=domain_type,
                    expertise_level=choice(list(ProficiencyLevel))
                )
                session.add(domain)


def create_project_requirements(session, project_list):
    """案件要件を作成"""
    for project in project_list:
        # ランダムに1-3個の要件を追加
        num_requirements = randint(1, 3)
        
        for i in range(num_requirements):
            requirement = ProjectRequirement(
                project_id=project.id,
                domain_type=choice(list(DomainType)),
                skill_type=choice(list(SkillType)),
                profession_type=choice(list(ProfessionType)),
                required_hours=randint(100, 500),
                priority=randint(1, 5)
            )
            session.add(requirement)


def create_assignments(session, staff_list, project_list):
    """アサインデータを作成"""
    # 各案件に対してランダムに要員をアサイン
    for project in project_list:
        # 案件に必要な要員数を決定（2-5名）
        num_assignments = randint(2, 5)
        
        # ランダムに要員を選択
        selected_staff = sample(staff_list, min(num_assignments, len(staff_list)))
        
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
