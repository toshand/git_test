"""
AI アサイン候補選定機能

スキル、領域、アサイン状況を考慮した要員アサイン候補の選定を行います。
"""

from typing import List, Dict, Tuple, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    SkillType, ProfessionType, DomainType, ProficiencyLevel,
    AssignmentType, AssignmentStatus
)


class AIAssignmentAdvisor:
    """AI アサイン候補選定クラス"""
    
    def __init__(self, session: Session):
        """
        AI アサイン候補選定クラスを初期化
        
        Args:
            session: データベースセッション
        """
        self.session = session
    
    def get_ai_assignment_candidates(self, project_id: int, target_month: date, 
                                   max_candidates: int = 10) -> List[Dict]:
        """
        AI によるアサイン候補を取得
        
        Args:
            project_id: 案件ID
            target_month: 対象月
            max_candidates: 最大候補数
            
        Returns:
            List[Dict]: AI候補リスト（スコア付き）
        """
        # 案件情報を取得
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
        
        # 案件要件を取得
        requirements = self.session.query(ProjectRequirement).filter(
            ProjectRequirement.project_id == project_id
        ).all()
        
        if not requirements:
            return []
        
        # 全要員を取得
        all_staff = self.session.query(Staff).all()
        candidates = []
        
        for staff in all_staff:
            # AI スコアを計算
            ai_score = self._calculate_ai_score(staff, requirements, project, target_month)
            
            if ai_score > 0:
                # 候補情報を構築
                candidate_info = self._build_candidate_info(staff, ai_score, requirements, target_month)
                candidates.append(candidate_info)
        
        # スコア順でソート
        candidates.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return candidates[:max_candidates]
    
    def _calculate_ai_score(self, staff: Staff, requirements: List[ProjectRequirement], 
                          project: Project, target_month: date) -> float:
        """
        AI スコアを計算
        
        Args:
            staff: 要員
            requirements: 案件要件
            project: 案件
            target_month: 対象月
            
        Returns:
            float: AI スコア（0.0-1.0）
        """
        # 基本マッチングスコア
        base_score = self._calculate_base_matching_score(staff, requirements)
        
        # 稼働状況スコア
        workload_score = self._calculate_workload_score(staff, target_month)
        
        # 経験・スキルレベルスコア
        experience_score = self._calculate_experience_score(staff, requirements)
        
        # 案件適合性スコア
        project_fit_score = self._calculate_project_fit_score(staff, project, requirements)
        
        # 重み付けして総合スコアを計算
        ai_score = (
            base_score * 0.3 +           # 基本マッチング
            workload_score * 0.25 +      # 稼働状況
            experience_score * 0.25 +    # 経験・スキル
            project_fit_score * 0.2      # 案件適合性
        )
        
        return min(ai_score, 1.0)
    
    def _calculate_base_matching_score(self, staff: Staff, requirements: List[ProjectRequirement]) -> float:
        """基本マッチングスコアを計算"""
        total_score = 0.0
        total_weight = 0.0
        
        for req in requirements:
            weight = req.priority / 5.0
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
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_workload_score(self, staff: Staff, target_month: date) -> float:
        """稼働状況スコアを計算"""
        # 対象月の稼働状況を取得
        start_date = date(target_month.year, target_month.month, 1)
        if target_month.month == 12:
            end_date = date(target_month.year + 1, 1, 1) - date.resolution
        else:
            end_date = date(target_month.year, target_month.month + 1, 1) - date.resolution
        
        # 現在のアサインを取得
        current_assignments = self.session.query(Assignment).filter(
            Assignment.staff_id == staff.id,
            Assignment.status == AssignmentStatus.ACTIVE,
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        ).all()
        
        total_allocation = sum(assignment.allocation_percentage for assignment in current_assignments)
        available_capacity = max(0.0, 1.0 - total_allocation)
        
        # 稼働率が低いほど高スコア
        if total_allocation >= 1.0:
            return 0.0  # 完全稼働中
        elif total_allocation >= 0.8:
            return 0.3  # 高稼働
        elif total_allocation >= 0.5:
            return 0.6  # 中稼働
        else:
            return 1.0  # 低稼働
    
    def _calculate_experience_score(self, staff: Staff, requirements: List[ProjectRequirement]) -> float:
        """経験・スキルレベルスコアを計算"""
        total_score = 0.0
        count = 0
        
        for req in requirements:
            if req.domain_type:
                domain_score = self._get_domain_experience_score(staff, req.domain_type)
                total_score += domain_score
                count += 1
            
            if req.skill_type:
                skill_score = self._get_skill_experience_score(staff, req.skill_type)
                total_score += skill_score
                count += 1
            
            if req.profession_type:
                profession_score = self._get_profession_experience_score(staff, req.profession_type)
                total_score += profession_score
                count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def _calculate_project_fit_score(self, staff: Staff, project: Project, requirements: List[ProjectRequirement]) -> float:
        """案件適合性スコアを計算"""
        # 案件の複雑さを考慮
        complexity_score = min(len(requirements) / 5.0, 1.0)
        
        # 要員の多様性スコア
        diversity_score = self._calculate_diversity_score(staff)
        
        # 案件期間との適合性
        duration_score = self._calculate_duration_fit_score(staff, project)
        
        return (complexity_score * 0.4 + diversity_score * 0.3 + duration_score * 0.3)
    
    def _check_domain_match(self, staff: Staff, required_domain: DomainType) -> float:
        """専門領域マッチングをチェック"""
        staff_domains = self.session.query(StaffDomain).filter(
            StaffDomain.staff_id == staff.id,
            StaffDomain.domain_type == required_domain
        ).all()
        
        if not staff_domains:
            return 0.0
        
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
        
        max_experience = max(staff_professions, key=lambda x: x.experience_years)
        return min(max_experience.experience_years / 10.0, 1.0)
    
    def _get_proficiency_score(self, level: ProficiencyLevel) -> float:
        """習熟度レベルをスコアに変換"""
        level_scores = {
            ProficiencyLevel.BEGINNER: 0.2,
            ProficiencyLevel.INTERMEDIATE: 0.5,
            ProficiencyLevel.ADVANCED: 0.8,
            ProficiencyLevel.EXPERT: 1.0
        }
        return level_scores.get(level, 0.0)
    
    def _get_domain_experience_score(self, staff: Staff, domain_type: DomainType) -> float:
        """専門領域の経験スコアを取得"""
        domain = self.session.query(StaffDomain).filter(
            StaffDomain.staff_id == staff.id,
            StaffDomain.domain_type == domain_type
        ).first()
        
        if not domain:
            return 0.0
        
        return self._get_proficiency_score(domain.expertise_level)
    
    def _get_skill_experience_score(self, staff: Staff, skill_type: SkillType) -> float:
        """スキルの経験スコアを取得"""
        skill = self.session.query(StaffSkill).filter(
            StaffSkill.staff_id == staff.id,
            StaffSkill.skill_type == skill_type
        ).first()
        
        if not skill:
            return 0.0
        
        return self._get_proficiency_score(skill.proficiency_level)
    
    def _get_profession_experience_score(self, staff: Staff, profession_type: ProfessionType) -> float:
        """プロフェッションの経験スコアを取得"""
        profession = self.session.query(StaffProfession).filter(
            StaffProfession.staff_id == staff.id,
            StaffProfession.profession_type == profession_type
        ).first()
        
        if not profession:
            return 0.0
        
        return min(profession.experience_years / 10.0, 1.0)
    
    def _calculate_diversity_score(self, staff: Staff) -> float:
        """要員の多様性スコアを計算"""
        # スキル数
        skill_count = len(staff.skills)
        
        # 専門領域数
        domain_count = len(staff.domains)
        
        # プロフェッション数
        profession_count = len(staff.professions)
        
        # 多様性スコア（0.0-1.0）
        diversity = (skill_count + domain_count + profession_count) / 9.0
        return min(diversity, 1.0)
    
    def _calculate_duration_fit_score(self, staff: Staff, project: Project) -> float:
        """案件期間との適合性スコアを計算"""
        # 要員の過去のアサイン期間を考慮
        past_assignments = self.session.query(Assignment).filter(
            Assignment.staff_id == staff.id,
            Assignment.status == AssignmentStatus.COMPLETED
        ).all()
        
        if not past_assignments:
            return 0.5  # 経験なしの場合は中程度
        
        # 平均アサイン期間を計算
        total_duration = 0
        for assignment in past_assignments:
            duration = (assignment.end_date - assignment.start_date).days
            total_duration += duration
        
        avg_duration = total_duration / len(past_assignments)
        
        # 案件期間との適合性
        if project.start_date and project.end_date:
            project_duration = (project.end_date - project.start_date).days
            fit_ratio = min(avg_duration / project_duration, project_duration / avg_duration)
            return fit_ratio
        
        return 0.5
    
    def _build_candidate_info(self, staff: Staff, ai_score: float, 
                            requirements: List[ProjectRequirement], target_month: date) -> Dict:
        """候補情報を構築"""
        # 稼働状況を取得
        start_date = date(target_month.year, target_month.month, 1)
        if target_month.month == 12:
            end_date = date(target_month.year + 1, 1, 1) - date.resolution
        else:
            end_date = date(target_month.year, target_month.month + 1, 1) - date.resolution
        
        # 現在のアサインを取得
        current_assignments = self.session.query(Assignment).filter(
            Assignment.staff_id == staff.id,
            Assignment.status == AssignmentStatus.ACTIVE,
            or_(
                and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
            )
        ).all()
        
        total_allocation = sum(assignment.allocation_percentage for assignment in current_assignments)
        available_capacity = max(0.0, 1.0 - total_allocation)
        
        workload = {
            'total_allocation': total_allocation,
            'available_capacity': available_capacity,
            'assignments': current_assignments
        }
        
        # マッチング詳細を取得
        match_details = self._get_match_details(staff, requirements)
        
        return {
            'staff': staff,
            'ai_score': ai_score,
            'workload': workload,
            'match_details': match_details,
            'recommendation_reason': self._generate_recommendation_reason(staff, ai_score, workload, match_details)
        }
    
    def _get_match_details(self, staff: Staff, requirements: List[ProjectRequirement]) -> Dict:
        """マッチング詳細を取得"""
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
                        'score': domain_match,
                        'required': True
                    })
            
            if req.skill_type:
                skill_match = self._check_skill_match(staff, req.skill_type)
                if skill_match > 0:
                    details['skills'].append({
                        'skill': req.skill_type.value,
                        'score': skill_match,
                        'required': True
                    })
            
            if req.profession_type:
                profession_match = self._check_profession_match(staff, req.profession_type)
                if profession_match > 0:
                    details['professions'].append({
                        'profession': req.profession_type.value,
                        'score': profession_match,
                        'required': True
                    })
        
        return details
    
    def _generate_recommendation_reason(self, staff: Staff, ai_score: float, 
                                      workload: Dict, match_details: Dict) -> str:
        """推奨理由を生成"""
        reasons = []
        
        # スコアに基づく理由
        if ai_score >= 0.8:
            reasons.append("高い適合性")
        elif ai_score >= 0.6:
            reasons.append("良好な適合性")
        else:
            reasons.append("部分的適合性")
        
        # 稼働状況に基づく理由
        if workload['available_capacity'] >= 0.8:
            reasons.append("十分な空き時間")
        elif workload['available_capacity'] >= 0.5:
            reasons.append("適度な空き時間")
        else:
            reasons.append("限定的な空き時間")
        
        # マッチング詳細に基づく理由
        if match_details['domains']:
            domain_names = [d['domain'] for d in match_details['domains']]
            reasons.append(f"専門領域: {', '.join(domain_names)}")
        
        if match_details['skills']:
            skill_names = [s['skill'] for s in match_details['skills']]
            reasons.append(f"スキル: {', '.join(skill_names)}")
        
        return " | ".join(reasons)
