from flask import Blueprint, render_template, session, redirect, url_for, request
from app import db
from app.models import Organisation, User, Opportunity, YoungArtist

organisations_bp = Blueprint('organisations', __name__)

def get_current_organisation():
    if 'user_id' not in session:
        return None
    return Organisation.query.filter_by(user_id=session['user_id']).first()

@organisations_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role', '').lower() != 'organisation':
        return redirect(url_for('artists.dashboard'))
    
    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    opportunities = Opportunity.query.filter_by(
        organisation_id=org.id
    ).order_by(Opportunity.deadline.asc()).all()

    return render_template('org_dashboard.html',
                    org=org,
                    opportunities=opportunities,
                    total_opportunities=len(opportunities)                     
    )

@organisations_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))
    opportunities = Opportunity.query.filter_by(organisation_id=org.id).all()
    open_opportunities_count = sum(
        1 for opportunity in opportunities if opportunity.status and opportunity.status.lower() == 'open'
    )
    return render_template(
        'org_profile.html',
        org=org,
        opportunities=opportunities,
        open_opportunities_count=open_opportunities_count
    )

@organisations_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    org = get_current_organisation()
    if org is None:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        org.org_name = request.form.get('org_name')
        org.org_type = request.form.get('org_type')
        org.location = request.form.get('location')
        org.contact_email = request.form.get('contact_email') or None
        org.website = request.form.get('website') or None
        org.phone = request.form.get('phone') or None
        org.logo_url = request.form.get('logo_url') or None
        org.about_us = request.form.get('about_us') or None
        db.session.commit()
        return redirect(url_for('organisations.profile'))
    
    opportunities = Opportunity.query.filter_by(organisation_id=org.id).all()
    open_opportunities_count = sum(
        1 for opportunity in opportunities if opportunity.status and opportunity.status.lower() == 'open'
    )
    return render_template(
        'org_profile.html',
        org=org,
        opportunities=opportunities,
        open_opportunities_count=open_opportunities_count,
        edit=True
    )

@organisations_bp.route('/search-artists')
def search_artists():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    art_form = request.args.get('art_form', '' )
    location = request.args.get('location', '')
    age = request.args.get('age', '')

    query = YoungArtist.query

    if art_form:
        query = query.filter(YoungArtist.art_form.ilike(f'%{art_form}%'))
    if location:
        query = query.filter(YoungArtist.location.ilike(f'%{location}%'))
    if age:
        query = query.filter(YoungArtist.age == int(age))

    artists = query.all()
    return render_template('search_artists.html', artists=artists, art_form=art_form, location=location, age=age)