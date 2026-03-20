from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Brain Stroke Risk Prediction System...")
    print("API available at: http://localhost:5000")
    print("Endpoints:")
    print("  GET  / - API Info")
    print("  GET  /api/users - Get all users")
    print("  POST /api/users - Create user")
    print("  GET  /api/patients - Get all patients")
    print("  POST /api/patients - Create patient")
    print("  GET  /api/predictions - Get all predictions")
    print("  POST /api/predictions - Create prediction")
    
    app.run(debug=True, host='0.0.0.0', port=5000)