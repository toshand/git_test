"""
アサインロジック

このモジュールには、要員と案件のマッチングロジックが含まれています。
専門性、スキル、プロフェッションを考慮したアサイン機能を提供します。
"""

from datetime import date, datetime
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    SkillType, ProfessionType, DomainType, ProficiencyLevel,
    AssignmentType, AssignmentStatus
)


class AssignmentMatcher:
    """アサインマッチングクラス"""
    
    def __init__(self, session: Session):
        """
        アサインマッチングクラスを初期化
        
        Args:
            session: データベースセッション
        """
        self.session = session
    
    def find_matching_staff(self, project_id: int, assignment_type: AssignmentType = AssignmentType.PARTIAL) -> List[Dict]:
        """
        案件にマッチする要員を検索
        
        Args:
            project_id: 案件ID
            assignment_type: アサインタイプ
            
        Returns:
            List[Dict]: マッチした要員のリスト（スコア付き）
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
        
        requirements = self.session.query(ProjectRequirement).filter(
            ProjectRequirement.project_id == project_id
        ).all()
        
        if not requirements:
            return []
        
        # 全要員を取得
        all_staff = self.session.query(Staff).all()
        matches = []
        
        for staff in all_staff:
            score = self._calculate_match_score(staff, requirements, project, assignment_type)
            if score > 0:
                matches.append({
                    'staff': staff,
                    'score': score,
                    'match_details': self._get_match_details(staff, requirements)
                })
        
        # スコア順でソート
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches
    
    def _calculate_match_score(self, staff: Staff, requirements: List[ProjectRequirement], 
                             project: Project, assignment_type: AssignmentType) -> float:
        """
        要員と案件要件のマッチスコアを計算
        
        Args:
            staff: 要員
            requirements: 案件要件
            project: 案件
            assignment_type: アサインタイプ
            
        Returns:
            float: マッチスコア（0.0-1.0）
        """
        total_score = 0.0
        total_weight = 0.0
        
        # 現在のアサイン状況を確認
        current_assignments = self._get_current_assignments(staff.id, project.start_date, project.end_date)
        if assignment_type == AssignmentType.FULL and current_assignments:
            return 0.0  # フルアサインの場合は既存アサインがあるとマッチしない
        
        for req in requirements:
            weight = req.priority / 5.0  # 優先度を重みとして使用
            total_weight += weight
            
            # 専門領域マッチング
            if req.domain_type:
                domain_score = self._check_domain_match(staff, req.domain_type)
                total_score += domain_score * weight * 0.4
            
            # スキルマッチング
            if req.skill_type:
                skill_score = self._check_skill_match(staff, req.skill_type)
                total_score += skill_score * weight * 0.3
            
            # プロフェッションマッチング
            if req.profession_type:
                profession_score = self._check_profession_match(staff, req.profession_type)
                total_score += profession_score * weight * 0.3
        
        if total_weight == 0:
            return 0.0
        
        # パーシャルアサインの場合は空き時間を考慮
        if assignment_type == AssignmentType.PARTIAL:
            availability = self._calculate_availability(staff, project.start_date, project.end_date)
            total_score *= availability
        
        return min(total_score / total_weight, 1.0)
    
    def _check_domain_match(self, staff: Staff, required_domain: DomainType) -> float:
        """専門領域マッチングをチェック"""
        staff_domains = self.session.query(StaffDomain).filter(
            StaffDomain.staff_id == staff.id,
            StaffDomain.domain_type == required_domain
        ).all()
        
        if not staff_domains:
            return 0.0
        
        # 最高の専門性レベルを取得
        max_level = max(staff_domains, key=lambda x: self._get_proficiency_score(x.expertise_level))
        return self._get_proficiency_score(max_level.expertise_level)
    
    def _check_skill_match(self, staff: Staff, required_skill: SkillType) -> float:
        """スキルマッチングをチェック"""
        staff_skills = self.session.query(StaffSkill).filter(
            StaffSkill.staff_id == staff.id,
            StaffSkill.skill_type == required_skill
        ).all()
        
        if not staff_skills:
            return 0.0
        
        # 最高の習熟度レベルを取得
        max_level = max(staff_skills, key=lambda x: self._get_proficiency_score(x.proficiency_level))
        return self._get_proficiency_score(max_level.proficiency_level)
    
    def _check_profession_match(self, staff: Staff, required_profession: ProfessionType) -> float:
        """プロフェッションマッチングをチェック"""
        staff_professions = self.session.query(StaffProfession).filter(
            StaffProfession.staff_id == staff.id,
            StaffProfession.profession_type == required_profession
        ).all()
        
        if not staff_professions:
            return 0.0
        
        # 経験年数を考慮したスコア
        max_experience = max(staff_professions, key=lambda x: x.experience_years)
        experience_score = min(max_experience.experience_years / 10.0, 1.0)  # 10年で最大スコア
        return experience_score
    
    def _get_proficiency_score(self, level: ProficiencyLevel) -> float:
        """習熟度レベルをスコアに変換"""
        level_scores = {
            ProficiencyLevel.BEGINNER: 0.2,
            ProficiencyLevel.INTERMEDIATE: 0.5,
            ProficiencyLevel.ADVANCED: 0.8,
            ProficiencyLevel.EXPERT: 1.0
        }
        return level_scores.get(level, 0.0)
    
    def _get_current_assignments(self, staff_id: int, start_date: date, end_date: date) -> List[Assignment]:
        """指定期間の現在のアサインを取得"""
        return self.session.query(Assignment).filter(
            Assignment.staff_id == staff_id,
            Assignment.status == AssignmentStatus.ACTIVE,
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        ).all()
    
    def _calculate_availability(self, staff: Staff, start_date: date, end_date: date) -> float:
        """要員の空き時間を計算"""
        current_assignments = self._get_current_assignments(staff.id, start_date, end_date)
        
        if not current_assignments:
            return 1.0  # 完全に空いている
        
        # 既存アサインの割合を計算
        total_allocation = sum(assignment.allocation_percentage for assignment in current_assignments)
        return max(0.0, 1.0 - total_allocation)
    
    def _get_match_details(self, staff: Staff, requirements: List[ProjectRequirement]) -> Dict:
        """マッチ詳細を取得"""
        details = {
            'domains': [],
            'skills': [],
            'professions': []
        }
        
        for req in requirements:
            if req.domain_type:
                domain_match = self._check_domain_match(staff, req.domain_type)
                if domain_match > 0:
                    details['domains'].append({
                        'domain': req.domain_type.value,
                        'score': domain_match
                    })
            
            if req.skill_type:
                skill_match = self._check_skill_match(staff, req.skill_type)
                if skill_match > 0:
                    details['skills'].append({
                        'skill': req.skill_type.value,
                        'score': skill_match
                    })
            
            if req.profession_type:
                profession_match = self._check_profession_match(staff, req.profession_type)
                if profession_match > 0:
                    details['professions'].append({
                        'profession': req.profession_type.value,
                        'score': profession_match
                    })
        
        return details
    
    def create_assignment(self, staff_id: int, project_id: int, assignment_type: AssignmentType,
                         allocation_percentage: float, start_date: date, end_date: date,
                         assigned_hours: int = 0) -> Assignment:
        """
        アサインを作成
        
        Args:
            staff_id: 要員ID
            project_id: 案件ID
            assignment_type: アサインタイプ
            allocation_percentage: 割合
            start_date: 開始日
            end_date: 終了日
            assigned_hours: アサイン工数
            
        Returns:
            Assignment: 作成されたアサイン
        """
        assignment = Assignment(
            staff_id=staff_id,
            project_id=project_id,
            assignment_type=assignment_type,
            allocation_percentage=allocation_percentage,
            start_date=start_date,
            end_date=end_date,
            assigned_hours=assigned_hours,
            status=AssignmentStatus.ACTIVE
        )
        
        self.session.add(assignment)
        self.session.commit()
        return assignment
    
    def get_staff_workload(self, staff_id: int, start_date: date, end_date: date) -> Dict:
        """
        要員の稼働状況を取得
        
        Args:
            staff_id: 要員ID
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            Dict: 稼働状況情報
        """
        assignments = self.session.query(Assignment).filter(
            Assignment.staff_id == staff_id,
            Assignment.status == AssignmentStatus.ACTIVE,
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        ).all()
        
        total_allocation = sum(assignment.allocation_percentage for assignment in assignments)
        available_capacity = max(0.0, 1.0 - total_allocation)
        
        return {
            'total_allocation': total_allocation,
            'available_capacity': available_capacity,
            'assignments': assignments,
            'is_fully_allocated': total_allocation >= 1.0
        }
