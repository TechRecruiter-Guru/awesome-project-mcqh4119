# awesome-project-mcqh4119

A full-stack web application built with modern technologies

## Tech Stack
- Frontend: React
- Backend: Flask
- Database: SQLite


## Features
- Core application functionality
- User interface
- Data processing

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

### Installation
1. Clone the repository
   ```bash
   git clone <your-repo-url>
   cd awesome-project-mcqh4119
   ```

2. Install frontend dependencies
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your configuration
   ```

5. Run the application
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Development Notes
- Frontend runs on http://localhost:3000
- Backend API runs on http://localhost:5000
- The generated code provides a starting template - customize as needed

## License
MIT License