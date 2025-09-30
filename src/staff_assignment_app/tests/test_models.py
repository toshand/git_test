"""
モデルテスト

データベースモデルのテストを実行します。
"""

import unittest
import sys
import os
from datetime import datetime, date

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    CompanyType, SkillType, ProfessionType, DomainType,
    ProficiencyLevel, ProjectStatus, AssignmentType, AssignmentStatus
)


class TestModels(unittest.TestCase):
    """モデルテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        # テスト用データベースを作成
        self.db_manager = DatabaseManager("sqlite:///:memory:")
        self.db_manager.create_tables()
        self.session = self.db_manager.get_session_sync()
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.session.close()
    
    def test_staff_creation(self):
        """要員作成テスト"""
        staff = Staff(
            employee_id="TEST001",
            name="テスト要員",
            company_type=CompanyType.KOBELCO,
            department="テスト部",
            email="test@example.com",
            phone="03-1234-5678"
        )
        
        self.session.add(staff)
        self.session.commit()
        
        # データベースから取得して確認
        retrieved_staff = self.session.query(Staff).filter(Staff.employee_id == "TEST001").first()
        self.assertIsNotNone(retrieved_staff)
        self.assertEqual(retrieved_staff.name, "テスト要員")
        self.assertEqual(retrieved_staff.company_type, CompanyType.KOBELCO)
    
    def test_project_creation(self):
        """案件作成テスト"""
        project = Project(
            project_code="PROJ001",
            project_name="テスト案件",
            description="テスト用案件",
            status=ProjectStatus.ACTIVE,
            start_date=date.today(),
            end_date=date.today() + date.resolution,
            total_hours=1000
        )
        
        self.session.add(project)
        self.session.commit()
        
        # データベースから取得して確認
        retrieved_project = self.session.query(Project).filter(Project.project_code == "PROJ001").first()
        self.assertIsNotNone(retrieved_project)
        self.assertEqual(retrieved_project.project_name, "テスト案件")
        self.assertEqual(retrieved_project.status, ProjectStatus.ACTIVE)
    
    def test_assignment_creation(self):
        """アサイン作成テスト"""
        # 要員と案件を作成
        staff = Staff(
            employee_id="TEST001",
            name="テスト要員",
            company_type=CompanyType.KOBELCO
        )
        self.session.add(staff)
        
        project = Project(
            project_code="PROJ001",
            project_name="テスト案件",
            status=ProjectStatus.ACTIVE
        )
        self.session.add(project)
        self.session.commit()
        
        # アサインを作成
        assignment = Assignment(
            staff_id=staff.id,
            project_id=project.id,
            assignment_type=AssignmentType.FULL,
            allocation_percentage=1.0,
            start_date=date.today(),
            end_date=date.today() + date.resolution,
            assigned_hours=1000,
            status=AssignmentStatus.ACTIVE
        )
        
        self.session.add(assignment)
        self.session.commit()
        
        # データベースから取得して確認
        retrieved_assignment = self.session.query(Assignment).filter(
            Assignment.staff_id == staff.id,
            Assignment.project_id == project.id
        ).first()
        self.assertIsNotNone(retrieved_assignment)
        self.assertEqual(retrieved_assignment.assignment_type, AssignmentType.FULL)
        self.assertEqual(retrieved_assignment.allocation_percentage, 1.0)
    
    def test_staff_skills(self):
        """要員スキルテスト"""
        staff = Staff(
            employee_id="TEST001",
            name="テスト要員",
            company_type=CompanyType.KOBELCO
        )
        self.session.add(staff)
        self.session.commit()
        
        # スキルを追加
        skill = StaffSkill(
            staff_id=staff.id,
            skill_type=SkillType.OPEN,
            proficiency_level=ProficiencyLevel.ADVANCED
        )
        self.session.add(skill)
        self.session.commit()
        
        # リレーションシップを確認
        self.assertEqual(len(staff.skills), 1)
        self.assertEqual(staff.skills[0].skill_type, SkillType.OPEN)
        self.assertEqual(staff.skills[0].proficiency_level, ProficiencyLevel.ADVANCED)
    
    def test_project_requirements(self):
        """案件要件テスト"""
        project = Project(
            project_code="PROJ001",
            project_name="テスト案件",
            status=ProjectStatus.ACTIVE
        )
        self.session.add(project)
        self.session.commit()
        
        # 要件を追加
        requirement = ProjectRequirement(
            project_id=project.id,
            domain_type=DomainType.PRODUCTION,
            skill_type=SkillType.HOST,
            profession_type=ProfessionType.DEVELOPER,
            required_hours=1000,
            priority=3
        )
        self.session.add(requirement)
        self.session.commit()
        
        # リレーションシップを確認
        self.assertEqual(len(project.requirements), 1)
        self.assertEqual(project.requirements[0].domain_type, DomainType.PRODUCTION)
        self.assertEqual(project.requirements[0].required_hours, 1000)


if __name__ == '__main__':
    unittest.main()
