# Notes Web Application - Azure Deployment Journey

A simple Flask web application for storing and displaying notes, deployed on Azure with SQL Database.

## Project Overview
This project demonstrates migrating from a local SQLite-based Flask app to a cloud-hosted solution using Azure App Service and Azure SQL Database.

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: Azure SQL Database (migrated from SQLite)
- **Deployment**: Azure App Service (Linux)
- **Server**: Gunicorn (production WSGI server)

## Local Development Setup

### 1. Virtual Environment Setup
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration
Set the Azure SQL connection string:
```powershell
# Working connection string format
$env:AZURE_SQL_CONNECTIONSTRING = "Driver={ODBC Driver 17 for SQL Server};Server=tcp:laser.database.windows.net,1433;Database=notesdb;UID=danishumer;PWD=password@1;Encrypt=yes;"
```

### 4. Run Application
```powershell
python app.py
```

## Azure Infrastructure Setup

### SQL Database Configuration
- **Server Name**: `laser.database.windows.net`
- **Database Name**: `notesdb`
- **Authentication**: SQL Server Authentication
- **Admin Username**: `danishumer`
- **Password**: `password@1`

### Networking & Security
- **Firewall Rule**: Added client IP `24.38.103.194` for development access
- **Public Network Access**: Enabled for development
- **Encryption**: TLS 1.2 enforced

## Problems Encountered & Solutions

### 1. Virtual Environment Issues
**Problem**: PowerShell execution policy blocking activation
```
.venv\Scripts\activate : The module '.venv' could not be loaded
```
**Solution**: Used proper PowerShell activation syntax:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. ODBC Driver Missing
**Problem**: 
```
pyodbc.InterfaceError: ('IM002', '[IM002] [Microsoft][ODBC Driver Manager] Data source name not found')
```
**Solution**: Confirmed ODBC Driver 17 for SQL Server was available, updated connection string driver version.

### 3. Network Access Denied
**Problem**:
```
Connection was denied because Deny Public Network Access is set to Yes
```
**Solution**: Enabled public network access in Azure SQL Server networking settings.

### 4. Firewall Blocking Connection
**Problem**:
```
Client with IP address '24.38.103.194' is not allowed to access the server
```
**Solution**: Added firewall rule for client IP address in Azure Portal.

### 5. Authentication Failures
**Problem**:
```
pyodbc.InterfaceError: ('28000', "Login failed for user 'danishumer'")
```
**Solutions Tried**:
- Verified server admin username in Azure Portal Properties
- Reset SQL Server admin password
- **Final Solution**: Used correct ODBC parameter names (`UID`/`PWD` instead of `Uid`/`Pwd`)

### 6. **Connection String Format Issues**
**Problem**: Various connection string formats failed
**Working Solution**:
```
Driver={ODBC Driver 17 for SQL Server};Server=tcp:laser.database.windows.net,1433;Database=notesdb;UID=danishumer;PWD=password@1;Encrypt=yes;
```

### 7. **Duplicate Flask Route Definitions**
**Problem**:
```
AssertionError: View function mapping is overwriting an existing endpoint function: health
```
**Solution**: Removed duplicate `/health` route definitions, kept only one.

### 8. **Startup Script Path Issues** 
**Problem**:
```
/opt/startup/startup.sh: 23: startup.sh: not found (Exit Code 127)
```
**Solutions**:
- **Option A**: Set startup command directly in Portal: `gunicorn --bind=0.0.0.0:8000 --workers=1 app:app`
- **Option B**: Keep [`startup.sh`](startup.sh ) file with same command for consistency

## Database Schema
The application automatically creates the following table:
```sql
CREATE TABLE notes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    content NVARCHAR(MAX) NOT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
)
```

## File Structure
```
learningCloud/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── startup.sh         # Azure App Service startup script
├── templates/
│   └── index.html     # HTML template for notes interface
└── README.md          # This documentation
```

## Key Learnings

1. **Environment Variables**: Azure SQL connection strings must be properly formatted and secured
2. **ODBC Drivers**: Version compatibility and parameter naming is crucial
3. **Azure Networking**: Firewall rules and public access settings must be configured correctly
4. **SQL Authentication**: Server admin credentials vs database users can be confusing
5. **Case Sensitivity**: ODBC connection parameters are case-sensitive (`UID` vs `Uid`)
6. **Startup Commands**: Both Portal startup command and [`startup.sh`](startup.sh ) file should contain: `gunicorn --bind=0.0.0.0:8000 --workers=1 app:app`
7. **Deployment Success**: After fixing duplicate Flask routes and startup configuration, app deployed successfully

## Deployment Success ✅
**Final working configuration:**
- **Startup Command**: `gunicorn --bind=0.0.0.0:8000 --workers=1 app:app` (set in Portal)
- **Connection String**: `Driver={ODBC Driver 17 for SQL Server};Server=tcp:laser.database.windows.net,1433;Database=notesdb;UID=danishumer;PWD=password@1;Encrypt=yes;`
- **Live URL**: `https://notes-app-danish.azurewebsites.net`
- **Database**: Azure SQL Database with notes table
- **Environment**: Azure App Service (Linux) with Python 3.12

## Next Steps
- ✅ ~~Deploy to Azure App Service~~ **COMPLETED**
- ✅ ~~Configure production environment variables~~ **COMPLETED**
- Set up CI/CD pipeline
- Add error handling and logging  
- Implement user authentication

## Environment Variables Required
- `AZURE_SQL_CONNECTIONSTRING`: Complete ODBC connection string for Azure SQL Database

## Production Considerations
- Use Azure Key Vault for secrets management
- Implement proper logging
- Add connection pooling
- Set up monitoring and alerts
- Configure custom domain and SSL