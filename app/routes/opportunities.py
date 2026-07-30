from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime
from app import db
from app.models import Opportunity, Organisation, Application, YoungArtist
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

opportunities_bp = Blueprint('opportunities', __name__)

def get_current_organisation():
    if 'user_id' not in session:
        return None
    return Organisation.query.filter_by(user_id=session['user_id']).first()

@opportunities_bp.route('/browse')
def browse():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    opportunities = Opportunity.query.filter_by(status='open').order_by(
        Opportunity.deadline.asc()).all()
    
    return render_template('browse_opportunities.html', opportunities=opportunities)

@opportunities_bp.route('/view/<id>')
def view(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    opportunity = Opportunity.query.get_or_404(id)
    return render_template('view_opportunity.html', opportunity=opportunity)

@opportunities_bp.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if session.get('role').lower() != 'organisation':
        return redirect(url_for('artists.dashboard'))
    
    org = Organisation.query.filter_by(user_id=session['user_id']).first()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        banner_image = request.files.get('banner_image')
        banner_url = None
        if banner_image and banner_image.filename:
            upload_result = cloudinary.uploader.upload(
                banner_image,
                resource_type='image',
                folder='creativelink/opportunity_banners'
            )
            banner_url = upload_result.get('secure_url')

        new_opportunity = Opportunity(
            organisation_id=org.id,
            title=request.form.get('title'),
            type=request.form.get('type'),
            description=request.form.get('description'),
            art_form=request.form.get('art_form'),
            criteria=request.form.get('criteria'),
            location=request.form.get('location'),
            deadline=datetime.strptime(request.form.get('deadline'), '%Y-%m-%d'),
            banner_url=banner_url,
            status='open'
        )
        db.session.add(new_opportunity)
        db.session.commit()
        return redirect(url_for('organisations.dashboard'))

    return render_template('post_opportunity.html', org=org)

@opportunities_bp.route('/delete/<id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    opportunity = Opportunity.query.get_or_404(id)
    db.session.delete(opportunity)
    db.session.commit()
    return redirect(url_for('organisations.dashboard'))

@opportunities_bp.route('/applications/<opportunity_id>')
def view_applications(opportunity_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role', '').lower() != 'organisation':
        return redirect(url_for('artists.dashboard'))

    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    opportunity = Opportunity.query.get_or_404(opportunity_id)
    if opportunity.organisation_id != org.id:
        return redirect(url_for('organisations.dashboard'))

    applications = Application.query.filter_by(
        opportunity_id=opportunity_id
    ).all()

    return render_template('view_applications.html',
                     opportunity=opportunity,
                     applications=applications
    )

@opportunities_bp.route('/applications/<application_id>/review')
def review_application(application_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role', '').lower() != 'organisation':
        return redirect(url_for('artists.dashboard'))

    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)
    opportunity = Opportunity.query.get_or_404(application.opportunity_id)
    if opportunity.organisation_id != org.id:
        return redirect(url_for('organisations.dashboard'))

    return render_template('application_review.html', application=application)


@opportunities_bp.route('/applications/update/<application_id>/<status>')
def update_application(application_id, status):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role', '').lower() != 'organisation':
        return redirect(url_for('artists.dashboard'))

    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    application = Application.query.get_or_404(application_id)
    opportunity = Opportunity.query.get_or_404(application.opportunity_id)
    if opportunity.organisation_id != org.id:
        return redirect(url_for('organisations.dashboard'))

    application.status = status
    db.session.commit()

    return redirect(url_for('opportunities.view_applications',
             opportunity_id=application.opportunity_id))