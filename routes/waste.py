from flask import Blueprint, jsonify, request, session
from src.models.user import User, WasteReport, db

waste_bp = Blueprint('waste', __name__)

# Points system configuration
POINTS_PER_KG = {
    'Plastic': 10,
    'Food': 5,
    'Electronic': 15,
    'Hazardous': 20,
    'Other': 8
}

def require_auth():
    """Helper function to check if user is authenticated"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@waste_bp.route('/report', methods=['POST'])
def submit_waste_report():
    """Submit a new waste report"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        waste_type = data.get('waste_type')
        weight = data.get('weight')
        
        # Validation
        if not waste_type or not weight:
            return jsonify({'error': 'Waste type and weight are required'}), 400
        
        if waste_type not in POINTS_PER_KG:
            return jsonify({'error': 'Invalid waste type'}), 400
        
        try:
            weight = float(weight)
            if weight <= 0:
                return jsonify({'error': 'Weight must be positive'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid weight format'}), 400
        
        # Calculate points
        points_earned = int(POINTS_PER_KG[waste_type] * weight)
        
        # Create waste report
        report = WasteReport(
            user_id=user.id,
            waste_type=waste_type,
            weight=weight,
            points_earned=points_earned
        )
        
        # Add points to user
        user.add_points(points_earned)
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Waste report submitted successfully',
            'report': report.to_dict(),
            'points_earned': points_earned,
            'total_points': user.points
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@waste_bp.route('/reports', methods=['GET'])
def get_user_reports():
    """Get all waste reports for the current user"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    reports = WasteReport.query.filter_by(user_id=user.id).order_by(WasteReport.created_at.desc()).all()
    
    return jsonify({
        'reports': [report.to_dict() for report in reports],
        'total_reports': len(reports),
        'total_points': user.points
    }), 200

@waste_bp.route('/points-system', methods=['GET'])
def get_points_system():
    """Get the points system configuration"""
    return jsonify({
        'points_per_kg': POINTS_PER_KG,
        'description': 'Points earned per kilogram of waste reported'
    }), 200

@waste_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Calculate statistics
    reports = WasteReport.query.filter_by(user_id=user.id).all()
    
    stats = {
        'total_reports': len(reports),
        'total_points': user.points,
        'total_weight': sum(report.weight for report in reports),
        'waste_type_breakdown': {}
    }
    
    # Calculate waste type breakdown
    for report in reports:
        waste_type = report.waste_type
        if waste_type not in stats['waste_type_breakdown']:
            stats['waste_type_breakdown'][waste_type] = {
                'count': 0,
                'total_weight': 0,
                'total_points': 0
            }
        
        stats['waste_type_breakdown'][waste_type]['count'] += 1
        stats['waste_type_breakdown'][waste_type]['total_weight'] += report.weight
        stats['waste_type_breakdown'][waste_type]['total_points'] += report.points_earned
    
    return jsonify(stats), 200
