"""
要員アサイン管理アプリケーション - メインアプリケーション

Flaskを使用したWebアプリケーションのメインファイルです。
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Dict
import json

from .database import get_db, init_database
from .models import (
    Staff, Project, Assignment, ProjectRequirement,
    StaffSkill, StaffProfession, StaffDomain,
    CompanyType, SkillType, ProfessionType, DomainType, 
    ProficiencyLevel, ProjectStatus, AssignmentType, AssignmentStatus
)
from .assignment_logic import AssignmentMatcher


def create_app():
    """Flaskアプリケーションを作成"""
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.secret_key = 'your-secret-key-here'
    
    # データベース初期化
    init_database()
    
    @app.route('/')
    def index():
        """ホームページ"""
        return render_template('index.html')
    
    @app.route('/staff')
    def staff_list():
        """要員一覧"""
        db = next(get_db())
        staff_list = db.query(Staff).all()
        return render_template('staff/list.html', staff_list=staff_list)
    
    @app.route('/staff/new', methods=['GET', 'POST'])
    def staff_new():
        """要員新規作成"""
        if request.method == 'POST':
            db = next(get_db())
            try:
                staff = Staff(
                    employee_id=request.form['employee_id'],
                    name=request.form['name'],
                    company_type=CompanyType(request.form['company_type']),
                    department=request.form.get('department', ''),
                    email=request.form.get('email', ''),
                    phone=request.form.get('phone', '')
                )
                db.add(staff)
                db.commit()
                flash('要員を登録しました', 'success')
                return redirect(url_for('staff_list'))
            except Exception as e:
                db.rollback()
                flash(f'エラーが発生しました: {str(e)}', 'error')
        
        return render_template('staff/new.html')
    
    @app.route('/staff/<int:staff_id>')
    def staff_detail(staff_id):
        """要員詳細"""
        db = next(get_db())
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            flash('要員が見つかりません', 'error')
            return redirect(url_for('staff_list'))
        
        return render_template('staff/detail.html', staff=staff)
    
    @app.route('/staff/<int:staff_id>/edit', methods=['GET', 'POST'])
    def staff_edit(staff_id):
        """要員編集"""
        db = next(get_db())
        staff = db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            flash('要員が見つかりません', 'error')
            return redirect(url_for('staff_list'))
        
        if request.method == 'POST':
            try:
                staff.name = request.form['name']
                staff.company_type = CompanyType(request.form['company_type'])
                staff.department = request.form.get('department', '')
                staff.email = request.form.get('email', '')
                staff.phone = request.form.get('phone', '')
                staff.updated_at = datetime.utcnow()
                db.commit()
                flash('要員情報を更新しました', 'success')
                return redirect(url_for('staff_detail', staff_id=staff_id))
            except Exception as e:
                db.rollback()
                flash(f'エラーが発生しました: {str(e)}', 'error')
        
        return render_template('staff/edit.html', staff=staff)
    
    @app.route('/projects')
    def project_list():
        """案件一覧"""
        db = next(get_db())
        projects = db.query(Project).all()
        return render_template('project/list.html', projects=projects)
    
    @app.route('/projects/new', methods=['GET', 'POST'])
    def project_new():
        """案件新規作成"""
        if request.method == 'POST':
            db = next(get_db())
            try:
                project = Project(
                    project_code=request.form['project_code'],
                    project_name=request.form['project_name'],
                    description=request.form.get('description', ''),
                    status=ProjectStatus(request.form['status']),
                    start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form['start_date'] else None,
                    end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None,
                    total_hours=int(request.form.get('total_hours', 0))
                )
                db.add(project)
                db.commit()
                flash('案件を登録しました', 'success')
                return redirect(url_for('project_list'))
            except Exception as e:
                db.rollback()
                flash(f'エラーが発生しました: {str(e)}', 'error')
        
        return render_template('project/new.html')
    
    @app.route('/projects/<int:project_id>')
    def project_detail(project_id):
        """案件詳細"""
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash('案件が見つかりません', 'error')
            return redirect(url_for('project_list'))
        
        return render_template('project/detail.html', project=project)
    
    @app.route('/assignments')
    def assignment_list():
        """アサイン一覧"""
        db = next(get_db())
        assignments = db.query(Assignment).all()
        return render_template('assignment/list.html', assignments=assignments)
    
    @app.route('/assignments/new', methods=['GET', 'POST'])
    def assignment_new():
        """アサイン新規作成"""
        db = next(get_db())
        
        if request.method == 'POST':
            try:
                assignment = Assignment(
                    staff_id=int(request.form['staff_id']),
                    project_id=int(request.form['project_id']),
                    assignment_type=AssignmentType(request.form['assignment_type']),
                    allocation_percentage=float(request.form['allocation_percentage']),
                    start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
                    end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date(),
                    assigned_hours=int(request.form.get('assigned_hours', 0))
                )
                db.add(assignment)
                db.commit()
                flash('アサインを作成しました', 'success')
                return redirect(url_for('assignment_list'))
            except Exception as e:
                db.rollback()
                flash(f'エラーが発生しました: {str(e)}', 'error')
        
        # フォーム用のデータを取得
        staff_list = db.query(Staff).all()
        project_list = db.query(Project).all()
        
        return render_template('assignment/new.html', 
                             staff_list=staff_list, 
                             project_list=project_list)
    
    @app.route('/assignments/match/<int:project_id>')
    def assignment_match(project_id):
        """案件にマッチする要員を検索"""
        db = next(get_db())
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            flash('案件が見つかりません', 'error')
            return redirect(url_for('project_list'))
        
        matcher = AssignmentMatcher(db)
        matches = matcher.find_matching_staff(project_id)
        
        return render_template('assignment/match.html', 
                             project=project, 
                             matches=matches)
    
    @app.route('/api/staff/<int:staff_id>/workload')
    def api_staff_workload(staff_id):
        """要員の稼働状況API"""
        db = next(get_db())
        matcher = AssignmentMatcher(db)
        
        start_date = request.args.get('start_date', date.today().isoformat())
        end_date = request.args.get('end_date', date.today().isoformat())
        
        workload = matcher.get_staff_workload(
            staff_id, 
            datetime.strptime(start_date, '%Y-%m-%d').date(),
            datetime.strptime(end_date, '%Y-%m-%d').date()
        )
        
        # アサイン情報を詳細化
        assignments_data = []
        for assignment in workload['assignments']:
            assignment_data = {
                'id': assignment.id,
                'assignment_type': assignment.assignment_type.value,
                'allocation_percentage': assignment.allocation_percentage,
                'start_date': assignment.start_date.isoformat(),
                'end_date': assignment.end_date.isoformat(),
                'assigned_hours': assignment.assigned_hours,
                'status': assignment.status.value,
                'project': {
                    'id': assignment.project.id,
                    'project_name': assignment.project.project_name,
                    'project_code': assignment.project.project_code
                }
            }
            assignments_data.append(assignment_data)
        
        return jsonify({
            'total_allocation': workload['total_allocation'],
            'available_capacity': workload['available_capacity'],
            'is_fully_allocated': workload['is_fully_allocated'],
            'assignments': assignments_data
        })
    
    @app.route('/reports/workload')
    def report_workload():
        """稼働状況レポート"""
        db = next(get_db())
        staff_list = db.query(Staff).all()
        return render_template('reports/workload.html', staff_list=staff_list)
    
    @app.route('/reports/project_status')
    def report_project_status():
        """案件進捗レポート"""
        db = next(get_db())
        projects = db.query(Project).all()
        return render_template('reports/project_status.html', projects=projects)
    
    # スキル管理エンドポイント
    @app.route('/staff/<int:staff_id>/skill/add', methods=['POST'])
    def add_staff_skill(staff_id):
        """要員スキル追加"""
        db = next(get_db())
        try:
            skill = StaffSkill(
                staff_id=staff_id,
                skill_type=SkillType(request.form['skill_type']),
                proficiency_level=ProficiencyLevel(request.form['proficiency_level'])
            )
            db.add(skill)
            db.commit()
            return jsonify({'success': True, 'message': 'スキルを追加しました'})
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    @app.route('/staff/<int:staff_id>/skill/delete', methods=['POST'])
    def delete_staff_skill(staff_id):
        """要員スキル削除"""
        db = next(get_db())
        try:
            skill_id = request.form.get('skill_id')
            skill = db.query(StaffSkill).filter(
                StaffSkill.id == skill_id,
                StaffSkill.staff_id == staff_id
            ).first()
            if skill:
                db.delete(skill)
                db.commit()
                return jsonify({'success': True, 'message': 'スキルを削除しました'})
            else:
                return jsonify({'success': False, 'message': 'スキルが見つかりません'}), 404
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # プロフェッション管理エンドポイント
    @app.route('/staff/<int:staff_id>/profession/add', methods=['POST'])
    def add_staff_profession(staff_id):
        """要員プロフェッション追加"""
        db = next(get_db())
        try:
            profession = StaffProfession(
                staff_id=staff_id,
                profession_type=ProfessionType(request.form['profession_type']),
                experience_years=int(request.form['experience_years'])
            )
            db.add(profession)
            db.commit()
            return jsonify({'success': True, 'message': 'プロフェッションを追加しました'})
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    @app.route('/staff/<int:staff_id>/profession/delete', methods=['POST'])
    def delete_staff_profession(staff_id):
        """要員プロフェッション削除"""
        db = next(get_db())
        try:
            profession_id = request.form.get('profession_id')
            profession = db.query(StaffProfession).filter(
                StaffProfession.id == profession_id,
                StaffProfession.staff_id == staff_id
            ).first()
            if profession:
                db.delete(profession)
                db.commit()
                return jsonify({'success': True, 'message': 'プロフェッションを削除しました'})
            else:
                return jsonify({'success': False, 'message': 'プロフェッションが見つかりません'}), 404
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    # 専門領域管理エンドポイント
    @app.route('/staff/<int:staff_id>/domain/add', methods=['POST'])
    def add_staff_domain(staff_id):
        """要員専門領域追加"""
        db = next(get_db())
        try:
            domain = StaffDomain(
                staff_id=staff_id,
                domain_type=DomainType(request.form['domain_type']),
                expertise_level=ProficiencyLevel(request.form['expertise_level'])
            )
            db.add(domain)
            db.commit()
            return jsonify({'success': True, 'message': '専門領域を追加しました'})
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    @app.route('/staff/<int:staff_id>/domain/delete', methods=['POST'])
    def delete_staff_domain(staff_id):
        """要員専門領域削除"""
        db = next(get_db())
        try:
            domain_id = request.form.get('domain_id')
            domain = db.query(StaffDomain).filter(
                StaffDomain.id == domain_id,
                StaffDomain.staff_id == staff_id
            ).first()
            if domain:
                db.delete(domain)
                db.commit()
                return jsonify({'success': True, 'message': '専門領域を削除しました'})
            else:
                return jsonify({'success': False, 'message': '専門領域が見つかりません'}), 404
        except Exception as e:
            db.rollback()
            return jsonify({'success': False, 'message': str(e)}), 400
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
