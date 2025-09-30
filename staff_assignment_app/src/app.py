"""
要員アサイン管理アプリケーション - メインアプリケーション
生成AI
Flask アプリケーションのメインファイルです。
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, date, timedelta
from typing import List, Dict

from database import get_db, init_database, db_manager
from models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    CompanyType, SkillType, ProficiencyLevel, ProfessionType, DomainType,
    ProjectStatus, AssignmentType, AssignmentStatus
)
from ai_assignment_advisor import AIAssignmentAdvisor


def create_app():
    """Flaskアプリケーションを作成"""
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = 'your-secret-key-here'
    
    # データベースを初期化
    init_database()
    
    @app.route('/')
    def index():
        """ダッシュボード"""
        session = db_manager.get_session_sync()
        try:
            # 統計情報を取得
            total_staff = session.query(Staff).count()
            total_projects = session.query(Project).count()
            active_assignments = session.query(Assignment).filter(
                Assignment.status == AssignmentStatus.ACTIVE
            ).count()
            
            # 最近のアサインを取得
            recent_assignments = session.query(Assignment).join(Staff).join(Project).filter(
                Assignment.status == AssignmentStatus.ACTIVE
            ).order_by(desc(Assignment.created_at)).limit(5).all()
            
            return render_template('index.html',
                                 total_staff=total_staff,
                                 total_projects=total_projects,
                                 active_assignments=active_assignments,
                                 recent_assignments=recent_assignments)
        finally:
            session.close()
    
    @app.route('/staff')
    def staff_list():
        """要員一覧"""
        session = db_manager.get_session_sync()
        try:
            staff_list = session.query(Staff).order_by(Staff.name).all()
            return render_template('staff/list.html', staff_list=staff_list)
        finally:
            session.close()
    
    @app.route('/staff/new', methods=['GET', 'POST'])
    def staff_new():
        """要員新規作成"""
        if request.method == 'POST':
            session = db_manager.get_session_sync()
            try:
                staff = Staff(
                    employee_id=request.form['employee_id'],
                    name=request.form['name'],
                    company_type=CompanyType(request.form['company_type']),
                    department=request.form.get('department', ''),
                    email=request.form.get('email', ''),
                    phone=request.form.get('phone', '')
                )
                session.add(staff)
                session.commit()
                flash('要員を登録しました。', 'success')
                return redirect(url_for('staff_detail', staff_id=staff.id))
            except Exception as e:
                flash(f'エラーが発生しました: {str(e)}', 'error')
            finally:
                session.close()
        
        return render_template('staff/new.html')
    
    @app.route('/staff/<int:staff_id>')
    def staff_detail(staff_id):
        """要員詳細"""
        with db_manager.get_session() as session:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                flash('要員が見つかりません。', 'error')
                return redirect(url_for('staff_list'))
            
            return render_template('staff/detail.html', staff=staff)
    
    @app.route('/staff/<int:staff_id>/edit', methods=['GET', 'POST'])
    def staff_edit(staff_id):
        """要員編集"""
        with db_manager.get_session() as session:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                flash('要員が見つかりません。', 'error')
                return redirect(url_for('staff_list'))
            
            if request.method == 'POST':
                try:
                    staff.name = request.form['name']
                    staff.company_type = CompanyType(request.form['company_type'])
                    staff.department = request.form.get('department', '')
                    staff.email = request.form.get('email', '')
                    staff.phone = request.form.get('phone', '')
                    session.commit()
                    flash('要員情報を更新しました。', 'success')
                    return redirect(url_for('staff_detail', staff_id=staff.id))
                except Exception as e:
                    flash(f'エラーが発生しました: {str(e)}', 'error')
            
            return render_template('staff/edit.html', staff=staff)
    
    @app.route('/api/staff/<int:staff_id>/skills', methods=['POST'])
    def api_add_staff_skill():
        """要員スキル追加API"""
        staff_id = request.json.get('staff_id')
        skill_type = request.json.get('skill_type')
        proficiency_level = request.json.get('proficiency_level')
        
        with db_manager.get_session() as session:
            try:
                # 重複チェック
                existing = session.query(StaffSkill).filter(
                    StaffSkill.staff_id == staff_id,
                    StaffSkill.skill_type == SkillType(skill_type)
                ).first()
                
                if existing:
                    return jsonify({'success': False, 'message': '既に登録されているスキルです。'})
                
                skill = StaffSkill(
                    staff_id=staff_id,
                    skill_type=SkillType(skill_type),
                    proficiency_level=ProficiencyLevel(proficiency_level)
                )
                session.add(skill)
                session.commit()
                
                return jsonify({'success': True, 'message': 'スキルを追加しました。'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'エラー: {str(e)}'})
    
    @app.route('/api/staff/<int:staff_id>/professions', methods=['POST'])
    def api_add_staff_profession():
        """要員プロフェッション追加API"""
        staff_id = request.json.get('staff_id')
        profession_type = request.json.get('profession_type')
        experience_years = request.json.get('experience_years', 0)
        
        with db_manager.get_session() as session:
            try:
                # 重複チェック
                existing = session.query(StaffProfession).filter(
                    StaffProfession.staff_id == staff_id,
                    StaffProfession.profession_type == ProfessionType(profession_type)
                ).first()
                
                if existing:
                    return jsonify({'success': False, 'message': '既に登録されているプロフェッションです。'})
                
                profession = StaffProfession(
                    staff_id=staff_id,
                    profession_type=ProfessionType(profession_type),
                    experience_years=experience_years
                )
                session.add(profession)
                session.commit()
                
                return jsonify({'success': True, 'message': 'プロフェッションを追加しました。'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'エラー: {str(e)}'})
    
    @app.route('/api/staff/<int:staff_id>/domains', methods=['POST'])
    def api_add_staff_domain():
        """要員専門領域追加API"""
        staff_id = request.json.get('staff_id')
        domain_type = request.json.get('domain_type')
        expertise_level = request.json.get('expertise_level')
        
        with db_manager.get_session() as session:
            try:
                # 重複チェック
                existing = session.query(StaffDomain).filter(
                    StaffDomain.staff_id == staff_id,
                    StaffDomain.domain_type == DomainType(domain_type)
                ).first()
                
                if existing:
                    return jsonify({'success': False, 'message': '既に登録されている専門領域です。'})
                
                domain = StaffDomain(
                    staff_id=staff_id,
                    domain_type=DomainType(domain_type),
                    expertise_level=ProficiencyLevel(expertise_level)
                )
                session.add(domain)
                session.commit()
                
                return jsonify({'success': True, 'message': '専門領域を追加しました。'})
            except Exception as e:
                return jsonify({'success': False, 'message': f'エラー: {str(e)}'})
    
    @app.route('/api/staff/<int:staff_id>/workload')
    def api_staff_workload():
        """要員稼働状況API"""
        with db_manager.get_session() as session:
            staff = session.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return jsonify({'error': '要員が見つかりません。'})
            
            # 現在のアサインを取得
            current_assignments = session.query(Assignment).join(Project).filter(
                Assignment.staff_id == staff_id,
                Assignment.status == AssignmentStatus.ACTIVE
            ).all()
            
            total_allocation = sum(assignment.allocation_percentage for assignment in current_assignments)
            available_capacity = max(0.0, 1.0 - total_allocation)
            
            # アサイン詳細を取得
            assignment_details = []
            for assignment in current_assignments:
                assignment_details.append({
                    'project_name': assignment.project.project_name,
                    'allocation_percentage': assignment.allocation_percentage,
                    'assigned_hours': assignment.assigned_hours,
                    'start_date': assignment.start_date.isoformat(),
                    'end_date': assignment.end_date.isoformat()
                })
            
            return jsonify({
                'total_allocation': total_allocation,
                'available_capacity': available_capacity,
                'assignments': assignment_details
            })
    
    @app.route('/projects')
    def project_list():
        """案件一覧"""
        with db_manager.get_session() as session:
            projects = session.query(Project).order_by(desc(Project.created_at)).all()
            return render_template('project/list.html', projects=projects)
    
    @app.route('/projects/new', methods=['GET', 'POST'])
    def project_new():
        """案件新規作成"""
        if request.method == 'POST':
            with db_manager.get_session() as session:
                try:
                    project = Project(
                        project_code=request.form['project_code'],
                        project_name=request.form['project_name'],
                        description=request.form.get('description', ''),
                        status=ProjectStatus(request.form['status']),
                        start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form.get('start_date') else None,
                        end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None,
                        total_hours=int(request.form.get('total_hours', 0))
                    )
                    session.add(project)
                    session.commit()
                    flash('案件を登録しました。', 'success')
                    return redirect(url_for('project_detail', project_id=project.id))
                except Exception as e:
                    flash(f'エラーが発生しました: {str(e)}', 'error')
        
        return render_template('project/new.html')
    
    @app.route('/projects/<int:project_id>')
    def project_detail(project_id):
        """案件詳細"""
        with db_manager.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                flash('案件が見つかりません。', 'error')
                return redirect(url_for('project_list'))
            
            return render_template('project/detail.html', project=project)
    
    @app.route('/assignments')
    def assignment_list():
        """アサイン一覧"""
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        staff_id = request.args.get('staff_id', type=int)
        
        with db_manager.get_session() as session:
            # 年月でフィルタリング
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            query = session.query(Assignment).join(Staff).join(Project).filter(
                or_(
                    and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                    and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                    and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
                )
            )
            
            if staff_id:
                query = query.filter(Assignment.staff_id == staff_id)
            
            assignments = query.order_by(desc(Assignment.created_at)).all()
            
            # 要員リストを取得（フィルター用）
            staff_list = session.query(Staff).order_by(Staff.name).all()
            
            return render_template('assignment/list.html',
                                 assignments=assignments,
                                 staff_list=staff_list,
                                 selected_year=year,
                                 selected_month=month,
                                 selected_staff_id=staff_id)
    
    @app.route('/assignments/calendar')
    def assignment_calendar():
        """アサインカレンダー"""
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        with db_manager.get_session() as session:
            # 年月でフィルタリング
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            assignments = session.query(Assignment).join(Staff).join(Project).filter(
                or_(
                    and_(Assignment.start_date <= start_date, Assignment.end_date >= start_date),
                    and_(Assignment.start_date <= end_date, Assignment.end_date >= end_date),
                    and_(Assignment.start_date >= start_date, Assignment.end_date <= end_date)
                )
            ).all()
            
            return render_template('assignment/calendar.html',
                                 assignments=assignments,
                                 selected_year=year,
                                 selected_month=month)
    
    @app.route('/assignments/new', methods=['GET', 'POST'])
    def assignment_new():
        """アサイン新規作成"""
        if request.method == 'POST':
            with db_manager.get_session() as session:
                try:
                    # 年月から開始日・終了日を計算
                    year = int(request.form['year'])
                    month = int(request.form['month'])
                    start_date = date(year, month, 1)
                    if month == 12:
                        end_date = date(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = date(year, month + 1, 1) - timedelta(days=1)
                    
                    assignment = Assignment(
                        staff_id=int(request.form['staff_id']),
                        project_id=int(request.form['project_id']),
                        assignment_type=AssignmentType(request.form['assignment_type']),
                        allocation_percentage=float(request.form['allocation_percentage']),
                        start_date=start_date,
                        end_date=end_date,
                        assigned_hours=int(request.form.get('assigned_hours', 0)),
                        status=AssignmentStatus.ACTIVE
                    )
                    session.add(assignment)
                    session.commit()
                    flash('アサインを登録しました。', 'success')
                    return redirect(url_for('assignment_list'))
                except Exception as e:
                    flash(f'エラーが発生しました: {str(e)}', 'error')
        
        with db_manager.get_session() as session:
            staff_list = session.query(Staff).order_by(Staff.name).all()
            projects = session.query(Project).order_by(Project.project_name).all()
            return render_template('assignment/new.html', staff_list=staff_list, projects=projects)
    
    @app.route('/assignments/ai-candidates/<int:project_id>')
    def ai_assignment_candidates(project_id):
        """AI アサイン候補表示"""
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        target_month = date(year, month, 1)
        
        with db_manager.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                flash('案件が見つかりません。', 'error')
                return redirect(url_for('project_list'))
            
            # AI 候補を取得
            advisor = AIAssignmentAdvisor(session)
            candidates = advisor.get_ai_assignment_candidates(project_id, target_month)
            
            return render_template('assignment/ai_candidates.html',
                                 project=project,
                                 candidates=candidates,
                                 selected_year=year,
                                 selected_month=month)
    
    @app.route('/reports/workload')
    def workload_report():
        """稼働状況レポート"""
        with db_manager.get_session() as session:
            # 全要員の稼働状況を取得
            staff_list = session.query(Staff).all()
            workload_data = []
            
            for staff in staff_list:
                # 現在のアサインを取得
                current_assignments = session.query(Assignment).join(Project).filter(
                    Assignment.staff_id == staff.id,
                    Assignment.status == AssignmentStatus.ACTIVE
                ).all()
                
                total_allocation = sum(assignment.allocation_percentage for assignment in current_assignments)
                available_capacity = max(0.0, 1.0 - total_allocation)
                
                workload_data.append({
                    'staff': staff,
                    'total_allocation': total_allocation,
                    'available_capacity': available_capacity,
                    'assignments': current_assignments
                })
            
            return render_template('reports/workload.html', workload_data=workload_data)
    
    @app.route('/reports/project-status')
    def project_status_report():
        """案件状況レポート"""
        with db_manager.get_session() as session:
            projects = session.query(Project).order_by(desc(Project.created_at)).all()
            return render_template('reports/project_status.html', projects=projects)
    
    return app
