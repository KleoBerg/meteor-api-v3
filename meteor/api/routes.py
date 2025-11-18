from flask import Blueprint, jsonify, current_app
from meteor import dgraph

api = Blueprint('api', __name__)

# JUST A TEST ROUTE TO CHECK API STATUS
@api.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "ok", "message": "API runs"}), 200

# JUST A TEST ROUTE TO CHECK DGRAPH CONNECTION
@api.route('/dgraph-status', methods=['GET'])                                   
def dgraph_status():                                                            
    try:                                                                        
        # We now know this returns a string, so we'll name it accordingly.      
        version_string = current_app.extensions["dgraph"].connection.check_version()     

        return jsonify({                                                        
            "status": "ok",                                                     
            "message": "Successfully connected to Dgraph.",                     
            "dgraph_version": version_string                                    
        }), 200                                                                 
                                                                                
    except Exception as e:                                                      
        current_app.logger.error(f"Dgraph connection check failed: {e}",        exc_info=True)                                                                  
        return jsonify({
            "status": "error", 
            "message": f"Could not connect to Dgraph: {e}"
        }), 500    