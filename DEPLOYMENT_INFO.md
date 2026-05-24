# PythonAnywhere Deployment Guide

## ข้อมูลการ Deploy E-Sports Team Manager

### 📦 ไฟล์ที่จำเป็น

```
esports-team-manager/
├── app.py                              # Flask application
├── requirements.txt                    # Python dependencies
├── pythonanywhere_wsgi.py              # WSGI file for PythonAnywhere
├── test_deployment.py                  # Deployment test script
├── esports_manager.db                  # SQLite database (auto-created)
├── templates/                          # HTML templates (13 files)
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── teams.html
│   ├── edit_team.html
│   ├── add_team.html
│   ├── players.html
│   ├── edit_player.html
│   ├── add_player.html
│   ├── equipment.html
│   ├── edit_equipment.html
│   ├── add_equipment.html
│   ├── tournaments.html
│   ├── edit_tournament.html
│   ├── add_tournament.html
│   ├── edit_assignment.html
│   └── edit_result.html
├── DEPLOY_QUICK_START.txt              # Quick deployment guide (Thai)
├── PYTHONANYWHERE_DEPLOYMENT.txt       # Detailed guide (Thai)
└── README.md                           # Project documentation
```

### 🚀 Quick Deployment Steps

#### 1. Test Locally First

```bash
python3 test_deployment.py
```

#### 2. Create PythonAnywhere Account

- Go to: https://www.pythonanywhere.com/
- Sign up (Free account available)
- Remember your username

#### 3. Upload Code

**Option A: GitHub (Recommended)**

```bash
# In PythonAnywhere Bash console
git clone https://github.com/YOUR_USERNAME/esports-team-manager.git
```

**Option B: Web Upload**

- Use PythonAnywhere Files to upload

#### 4. Create Web App

- PythonAnywhere → Web → "Add a new web app"
- Manual configuration
- Python 3.11
- Get your URL: `https://yourusername.pythonanywhere.com`

#### 5. Setup Virtual Environment

```bash
# In Bash console
mkvirtualenv --python=/usr/bin/python3.11 flask
pip install -r ~/esports-team-manager/requirements.txt
```

#### 6. Configure WSGI File

- Web → WSGI configuration file
- Replace content with:

```python
import os
import sys

project_home = '/home/yourusername/esports-team-manager'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

activate_this = os.path.expanduser('~/.virtualenvs/flask/bin/activate_this.py')
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

from app import app as application

if not os.path.exists(os.path.join(project_home, 'esports_manager.db')):
    from app import init_db, insert_sample_data
    init_db()
    insert_sample_data()
```

**⚠️ Replace `yourusername` with your PythonAnywhere username**

#### 7. Reload Web App

- Click "Reload" button in Web tab
- Wait 10-30 seconds
- Visit: `https://yourusername.pythonanywhere.com`

### 🔍 Testing

Once deployed, test these features:

```
✅ Homepage loads (/ route)
✅ Dashboard shows stats (/dashboard)
✅ Teams page displays (/teams)
✅ Players page with game-specific positions (/players)
✅ Equipment management (/equipment)
✅ Tournaments and results (/tournaments)
✅ Add new team/player/equipment
✅ Edit existing records
✅ Delete records (cascading works)
✅ Database persistence (add item, reload, still there)
```

### 📝 Available Documentation

| File                            | Purpose                                    |
| ------------------------------- | ------------------------------------------ |
| `DEPLOY_QUICK_START.txt`        | Quick 7-step guide (Thai)                  |
| `PYTHONANYWHERE_DEPLOYMENT.txt` | Detailed guide with troubleshooting (Thai) |
| `test_deployment.py`            | Pre-deployment validation script           |
| `pythonanywhere_wsgi.py`        | WSGI template file                         |
| `README.md`                     | Full project documentation                 |

### 🐛 Common Issues

**502 Bad Gateway**

- Check Error log in Web tab
- Verify WSGI file syntax
- Check virtualenv path

**Database is empty**

```bash
# In Bash console
cd ~/esports-team-manager
python3
from app import init_db, insert_sample_data
init_db()
insert_sample_data()
exit()
```

**CSS/Images not loading**

- Setup Static files (Web → Static files section)
- URL: `/static`, Directory: `/home/yourusername/esports-team-manager/static`

### 💾 Important Notes

- **Database**: SQLite - stored in project directory
- **Backup**: Download `esports_manager.db` regularly from Files
- **Code updates**: Use Git pull or re-upload files
- **Free tier**: Limited CPU, web app may unload if inactive

### 🌐 Final URL Format

```
https://yourusername.pythonanywhere.com/
```

Example: `https://john123.pythonanywhere.com/`

### 📞 Support

- PythonAnywhere Docs: https://help.pythonanywhere.com/
- Flask Docs: https://flask.palletsprojects.com/
- GitHub: https://github.com/your-repo-url

---

**Ready to deploy?** Start with `DEPLOY_QUICK_START.txt` for step-by-step instructions!
