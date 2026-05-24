"""
E-Sports Team Manager - Flask Application
Manages teams, players, equipment, and tournaments
Database: SQLite
Author: CS104 Mini Project
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import os

# Initialize Flask application
app = Flask(__name__)

# Database path - supports both local and PythonAnywhere deployment
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'esports_manager.db')

# ===== HELPER FUNCTIONS =====
def get_db_connection():
    """
    Create and return a database connection with Row factory for dict-like access
    Returns: sqlite3.Connection object configured for dict-style row access
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop existing tables if they exist (to ensure clean schema)
    tables_to_drop = [
        'TournamentResults', 'EquipmentAssignment', 'GamePositions',
        'Tournaments', 'Equipment', 'Players', 'Teams', 'Games'
    ]
    for table in tables_to_drop:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        except:
            pass
    
    # Games Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Games (
        GameID INTEGER PRIMARY KEY AUTOINCREMENT,
        GameName TEXT NOT NULL UNIQUE,
        GameType TEXT NOT NULL
    )''')
    
    # Game Positions Table (Maps positions to games)
    cursor.execute('''CREATE TABLE IF NOT EXISTS GamePositions (
        PositionID INTEGER PRIMARY KEY AUTOINCREMENT,
        GameID INTEGER NOT NULL,
        PositionName TEXT NOT NULL,
        FOREIGN KEY (GameID) REFERENCES Games(GameID),
        UNIQUE(GameID, PositionName)
    )''')
    
    # Teams Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Teams (
        TeamID INTEGER PRIMARY KEY AUTOINCREMENT,
        TeamName TEXT NOT NULL UNIQUE,
        Founded DATE NOT NULL,
        Coach TEXT NOT NULL,
        Country TEXT NOT NULL,
        GameID INTEGER,
        FOREIGN KEY (GameID) REFERENCES Games(GameID)
    )''')
    
    # Players Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Players (
        PlayerID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerName TEXT NOT NULL,
        TeamID INTEGER NOT NULL,
        Position TEXT NOT NULL,
        JoinDate DATE NOT NULL,
        FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
    )''')
    
    # Equipment Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Equipment (
        EquipmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        EquipmentName TEXT NOT NULL,
        Type TEXT NOT NULL,
        Brand TEXT NOT NULL,
        Price REAL NOT NULL,
        PurchaseDate DATE NOT NULL
    )''')
    
    # Equipment Assignment Table (Many-to-Many)
    cursor.execute('''CREATE TABLE IF NOT EXISTS EquipmentAssignment (
        AssignmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        PlayerID INTEGER NOT NULL,
        EquipmentID INTEGER NOT NULL,
        AssignedDate DATE NOT NULL,
        FOREIGN KEY (PlayerID) REFERENCES Players(PlayerID),
        FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID)
    )''')
    
    # Tournaments Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tournaments (
        TournamentID INTEGER PRIMARY KEY AUTOINCREMENT,
        TournamentName TEXT NOT NULL,
        Game TEXT NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL,
        Location TEXT NOT NULL,
        PrizePool REAL NOT NULL
    )''')
    
    # Tournament Results Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS TournamentResults (
        ResultID INTEGER PRIMARY KEY AUTOINCREMENT,
        TournamentID INTEGER NOT NULL,
        TeamID INTEGER NOT NULL,
        Placement INTEGER NOT NULL,
        PrizeMoney REAL NOT NULL,
        FOREIGN KEY (TournamentID) REFERENCES Tournaments(TournamentID),
        FOREIGN KEY (TeamID) REFERENCES Teams(TeamID)
    )''')
    
    conn.commit()
    conn.close()

def insert_sample_data():
    """Insert sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Games
        games = [
            ('League of Legends', 'MOBA'),
            ('Dota 2', 'MOBA'),
            ('Valorant', 'FPS'),
            ('CS:GO', 'FPS'),
            ('Overwatch', 'FPS'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO Games (GameName, GameType) VALUES (?, ?)', games)
        
        # Game Positions
        moba_positions = [
            (1, 'Top'),
            (1, 'Jungle'),
            (1, 'Mid'),
            (1, 'ADC'),
            (1, 'Support'),
            (2, 'Carry'),
            (2, 'Midlaner'),
            (2, 'Offlaner'),
            (2, 'Roamer'),
            (2, 'Support'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO GamePositions (GameID, PositionName) VALUES (?, ?)', moba_positions)
        
        fps_positions = [
            (3, 'Entry Fragger'),
            (3, 'AWP'),
            (3, 'Initiator'),
            (3, 'Controller'),
            (3, 'IGL'),
            (4, 'Entry Fragger'),
            (4, 'AWP'),
            (4, 'Lurker'),
            (4, 'IGL'),
            (4, 'Coach'),
            (5, 'Tank'),
            (5, 'Damage'),
            (5, 'Healer'),
            (5, 'Coach'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO GamePositions (GameID, PositionName) VALUES (?, ?)', fps_positions)
        
        # Teams (Updated with GameID - 1=LoL, 3=Valorant)
        teams = [
            ('Dragon Slayers', '2020-03-15', 'Coach Alex', 'Thailand', 1),
            ('Phoenix Force', '2019-06-20', 'Coach Mike', 'USA', 1),
            ('Titan Squad', '2021-01-10', 'Coach Lee', 'South Korea', 3),
            ('Shadow Guild', '2020-11-05', 'Coach Maria', 'Brazil', 1),
            ('Pixel Masters', '2022-04-12', 'Coach Yuki', 'Japan', 3)
        ]
        cursor.executemany('INSERT OR IGNORE INTO Teams (TeamName, Founded, Coach, Country, GameID) VALUES (?, ?, ?, ?, ?)', teams)
        
        # Players
        players = [
            ('Apex Pro', 1, 'Mid', '2021-05-10'),
            ('Lightning Storm', 1, 'ADC', '2021-06-15'),
            ('Frost Knight', 1, 'Top', '2020-04-01'),
            ('Shadow Echo', 1, 'Support', '2021-07-20'),
            ('Mystic Blade', 1, 'Jungle', '2021-08-10'),
            ('Phoenix Rise', 2, 'Top', '2021-03-15'),
            ('Inferno Burst', 2, 'Mid', '2021-04-20'),
            ('Cyber Ninja', 2, 'ADC', '2021-05-25'),
            ('Steel Guard', 2, 'Support', '2021-06-30'),
            ('Void Walker', 2, 'Jungle', '2021-07-15'),
            ('Dragon Fist', 3, 'Entry Fragger', '2020-12-01'),
            ('Ice Storm', 3, 'Initiator', '2021-01-10'),
            ('Thunder Claw', 3, 'AWP', '2021-02-15'),
            ('Royal Crown', 3, 'Controller', '2021-03-20'),
            ('Crimson Flash', 3, 'IGL', '2021-04-10'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO Players (PlayerName, TeamID, Position, JoinDate) VALUES (?, ?, ?, ?)', players)
        
        # Equipment
        equipment = [
            ('Mechanical Keyboard RGB', 'Keyboard', 'Corsair', 150.00, '2023-01-15'),
            ('Gaming Mouse', 'Mouse', 'Logitech', 80.00, '2023-02-10'),
            ('Headphones Pro', 'Headphones', 'SteelSeries', 200.00, '2023-01-20'),
            ('Gaming Chair', 'Chair', 'Herman Miller', 1500.00, '2022-12-01'),
            ('Monitor 27inch 240Hz', 'Monitor', 'ASUS', 400.00, '2023-03-05'),
            ('SSD 1TB NVMe', 'Storage', 'Samsung', 120.00, '2023-02-15'),
            ('Mousepad XL', 'Mousepad', 'SteelSeries', 40.00, '2023-01-25'),
            ('Webcam 4K', 'Webcam', 'Logitech', 150.00, '2023-03-10'),
            ('Gaming PC RTX4080', 'PC', 'ASUS ROG', 3500.00, '2023-01-01'),
            ('USB Microphone', 'Microphone', 'Blue Yeti', 100.00, '2023-02-20'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO Equipment (EquipmentName, Type, Brand, Price, PurchaseDate) VALUES (?, ?, ?, ?, ?)', equipment)
        
        # Equipment Assignment
        assignments = [
            (1, 1, '2023-02-01'),
            (2, 2, '2023-02-05'),
            (3, 3, '2023-02-10'),
            (1, 4, '2023-02-15'),
            (2, 5, '2023-02-20'),
            (6, 1, '2023-03-01'),
            (7, 2, '2023-03-05'),
            (8, 3, '2023-03-10'),
            (9, 4, '2023-03-15'),
            (10, 5, '2023-03-20'),
        ]
        cursor.executemany('INSERT OR IGNORE INTO EquipmentAssignment (PlayerID, EquipmentID, AssignedDate) VALUES (?, ?, ?)', assignments)
        
        # Tournaments
        tournaments = [
            ('Spring Championship 2023', 'League of Legends', '2023-03-01', '2023-04-30', 'Bangkok', 100000.00),
            ('Summer Masters', 'Dota 2', '2023-06-01', '2023-07-31', 'Seoul', 150000.00),
            ('International Cup', 'CS:GO', '2023-09-01', '2023-10-31', 'Las Vegas', 200000.00),
            ('Winter Finals', 'Valorant', '2023-12-01', '2024-01-31', 'Los Angeles', 120000.00),
            ('Asia Pacific League', 'League of Legends', '2023-05-15', '2023-08-15', 'Singapore', 250000.00),
        ]
        cursor.executemany('INSERT OR IGNORE INTO Tournaments (TournamentName, Game, StartDate, EndDate, Location, PrizePool) VALUES (?, ?, ?, ?, ?, ?)', tournaments)
        
        # Tournament Results
        results = [
            (1, 1, 1, 30000.00),
            (1, 2, 2, 20000.00),
            (1, 3, 3, 15000.00),
            (2, 2, 1, 50000.00),
            (2, 1, 2, 35000.00),
            (3, 3, 1, 60000.00),
            (3, 2, 2, 40000.00),
            (4, 1, 1, 45000.00),
            (4, 3, 2, 30000.00),
            (5, 1, 1, 80000.00),
        ]
        cursor.executemany('INSERT OR IGNORE INTO TournamentResults (TournamentID, TeamID, Placement, PrizeMoney) VALUES (?, ?, ?, ?)', results)
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

# ========== TEAMS ROUTES ==========
@app.route('/')
def index():
    conn = get_db_connection()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('index.html', teams=teams)

@app.route('/teams', methods=['GET', 'POST'])
def teams():
    if request.method == 'POST':
        team_name = request.form['team_name']
        founded = request.form['founded']
        coach = request.form['coach']
        country = request.form['country']
        game_id = request.form.get('game_id')
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Teams (TeamName, Founded, Coach, Country, GameID) VALUES (?, ?, ?, ?, ?)',
                        (team_name, founded, coach, country, game_id))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Team name already exists!", 'error')
        conn.close()
        return redirect(url_for('teams'))
    
    conn = get_db_connection()
    teams = conn.execute('''
        SELECT t.*, g.GameName 
        FROM Teams t 
        LEFT JOIN Games g ON t.GameID = g.GameID
    ''').fetchall()
    games = conn.execute('SELECT * FROM Games').fetchall()
    conn.close()
    return render_template('teams.html', teams=teams, games=games)

@app.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
def edit_team(team_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        team_name = request.form['team_name']
        founded = request.form['founded']
        coach = request.form['coach']
        country = request.form['country']
        game_id = request.form.get('game_id')
        
        conn.execute('UPDATE Teams SET TeamName = ?, Founded = ?, Coach = ?, Country = ?, GameID = ? WHERE TeamID = ?',
                    (team_name, founded, coach, country, game_id, team_id))
        conn.commit()
        conn.close()
        return redirect(url_for('teams'))
    
    team = conn.execute('SELECT * FROM Teams WHERE TeamID = ?', (team_id,)).fetchone()
    games = conn.execute('SELECT * FROM Games').fetchall()
    conn.close()
    return render_template('edit_team.html', team=team, games=games)

@app.route('/team/<int:team_id>/delete', methods=['POST'])
def delete_team(team_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Teams WHERE TeamID = ?', (team_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('teams'))

# ========== PLAYERS ROUTES ==========
@app.route('/players')
def players():
    conn = get_db_connection()
    players_data = conn.execute('''
        SELECT p.PlayerID, p.PlayerName, p.Position, p.JoinDate, t.TeamName, t.TeamID, g.GameName
        FROM Players p
        JOIN Teams t ON p.TeamID = t.TeamID
        LEFT JOIN Games g ON t.GameID = g.GameID
    ''').fetchall()
    teams = conn.execute('''
        SELECT t.*, g.GameName, g.GameID
        FROM Teams t
        LEFT JOIN Games g ON t.GameID = g.GameID
    ''').fetchall()
    conn.close()
    return render_template('players.html', players=players_data, teams=teams)

@app.route('/player/add', methods=['POST'])
def add_player():
    player_name = request.form['player_name']
    team_id = request.form['team_id']
    position = request.form['position']
    join_date = request.form['join_date']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO Players (PlayerName, TeamID, Position, JoinDate) VALUES (?, ?, ?, ?)',
                (player_name, team_id, position, join_date))
    conn.commit()
    conn.close()
    return redirect(url_for('players'))

@app.route('/api/game-positions/<int:game_id>')
def get_game_positions(game_id):
    """API endpoint to get positions for a specific game"""
    conn = get_db_connection()
    positions = conn.execute('''
        SELECT PositionID, PositionName 
        FROM GamePositions 
        WHERE GameID = ?
        ORDER BY PositionName
    ''', (game_id,)).fetchall()
    conn.close()
    return jsonify([dict(pos) for pos in positions])

@app.route('/player/<int:player_id>/edit', methods=['GET', 'POST'])
def edit_player(player_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        player_name = request.form['player_name']
        team_id = request.form['team_id']
        position = request.form['position']
        join_date = request.form['join_date']
        
        conn.execute('UPDATE Players SET PlayerName = ?, TeamID = ?, Position = ?, JoinDate = ? WHERE PlayerID = ?',
                    (player_name, team_id, position, join_date, player_id))
        conn.commit()
        conn.close()
        return redirect(url_for('players'))
    
    player = conn.execute('SELECT * FROM Players WHERE PlayerID = ?', (player_id,)).fetchone()
    teams = conn.execute('''
        SELECT t.*, g.GameName, g.GameID
        FROM Teams t
        LEFT JOIN Games g ON t.GameID = g.GameID
    ''').fetchall()
    conn.close()
    return render_template('edit_player.html', player=player, teams=teams)

@app.route('/player/<int:player_id>/delete', methods=['POST'])
def delete_player(player_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Players WHERE PlayerID = ?', (player_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('players'))

# ========== EQUIPMENT ROUTES ==========
@app.route('/equipment')
def equipment():
    conn = get_db_connection()
    equip = conn.execute('SELECT * FROM Equipment').fetchall()
    assignments = conn.execute('''
        SELECT ea.AssignmentID, e.EquipmentName, p.PlayerName, p.PlayerID, e.EquipmentID, ea.AssignedDate
        FROM EquipmentAssignment ea
        JOIN Equipment e ON ea.EquipmentID = e.EquipmentID
        JOIN Players p ON ea.PlayerID = p.PlayerID
    ''').fetchall()
    players = conn.execute('SELECT * FROM Players').fetchall()
    conn.close()
    return render_template('equipment.html', equipment=equip, assignments=assignments, players=players)

@app.route('/equipment/add', methods=['POST'])
def add_equipment():
    equipment_name = request.form['equipment_name']
    eq_type = request.form['type']
    brand = request.form['brand']
    price = request.form['price']
    purchase_date = request.form['purchase_date']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO Equipment (EquipmentName, Type, Brand, Price, PurchaseDate) VALUES (?, ?, ?, ?, ?)',
                (equipment_name, eq_type, brand, float(price), purchase_date))
    conn.commit()
    conn.close()
    return redirect(url_for('equipment'))

@app.route('/assignment/add', methods=['POST'])
def add_assignment():
    player_id = request.form['player_id']
    equipment_id = request.form['equipment_id']
    assigned_date = request.form['assigned_date']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO EquipmentAssignment (PlayerID, EquipmentID, AssignedDate) VALUES (?, ?, ?)',
                (player_id, equipment_id, assigned_date))
    conn.commit()
    conn.close()
    return redirect(url_for('equipment'))

@app.route('/assignment/<int:assignment_id>/edit', methods=['GET', 'POST'])
def edit_assignment(assignment_id):
    conn = get_db_connection()
    if request.method == 'POST':
        player_id = request.form['player_id']
        equipment_id = request.form['equipment_id']
        assigned_date = request.form['assigned_date']
        
        conn.execute('UPDATE EquipmentAssignment SET PlayerID = ?, EquipmentID = ?, AssignedDate = ? WHERE AssignmentID = ?',
                    (player_id, equipment_id, assigned_date, assignment_id))
        conn.commit()
        conn.close()
        return redirect(url_for('equipment'))
    
    assignment = conn.execute('''
        SELECT ea.*, e.EquipmentName, p.PlayerName
        FROM EquipmentAssignment ea
        JOIN Equipment e ON ea.EquipmentID = e.EquipmentID
        JOIN Players p ON ea.PlayerID = p.PlayerID
        WHERE ea.AssignmentID = ?
    ''', (assignment_id,)).fetchone()
    players = conn.execute('SELECT * FROM Players').fetchall()
    equipment = conn.execute('SELECT * FROM Equipment').fetchall()
    conn.close()
    return render_template('edit_assignment.html', assignment=assignment, players=players, equipment=equipment)

@app.route('/assignment/<int:assignment_id>/delete', methods=['POST'])
def delete_assignment(assignment_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM EquipmentAssignment WHERE AssignmentID = ?', (assignment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('equipment'))

# ========== EQUIPMENT EDIT & DELETE ROUTES ==========
@app.route('/equipment/<int:equipment_id>/edit', methods=['GET', 'POST'])
def edit_equipment(equipment_id):
    conn = get_db_connection()
    if request.method == 'POST':
        equipment_name = request.form['equipment_name']
        eq_type = request.form['type']
        brand = request.form['brand']
        price = request.form['price']
        purchase_date = request.form['purchase_date']
        
        conn.execute('UPDATE Equipment SET EquipmentName = ?, Type = ?, Brand = ?, Price = ?, PurchaseDate = ? WHERE EquipmentID = ?',
                    (equipment_name, eq_type, brand, float(price), purchase_date, equipment_id))
        conn.commit()
        conn.close()
        return redirect(url_for('equipment'))
    
    equip = conn.execute('SELECT * FROM Equipment WHERE EquipmentID = ?', (equipment_id,)).fetchone()
    conn.close()
    return render_template('edit_equipment.html', equipment=equip)

@app.route('/equipment/<int:equipment_id>/delete', methods=['POST'])
def delete_equipment(equipment_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM EquipmentAssignment WHERE EquipmentID = ?', (equipment_id,))
    conn.execute('DELETE FROM Equipment WHERE EquipmentID = ?', (equipment_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('equipment'))

# ========== TOURNAMENTS ROUTES ==========
@app.route('/tournaments')
def tournaments():
    conn = get_db_connection()
    tournaments_data = conn.execute('SELECT * FROM Tournaments').fetchall()
    results = conn.execute('''
        SELECT tr.ResultID, tr.Placement, tr.PrizeMoney, t.TournamentName, tm.TeamName, tr.TournamentID, tr.TeamID
        FROM TournamentResults tr
        JOIN Tournaments t ON tr.TournamentID = t.TournamentID
        JOIN Teams tm ON tr.TeamID = tm.TeamID
    ''').fetchall()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('tournaments.html', tournaments=tournaments_data, results=results, teams=teams)

@app.route('/tournament/add', methods=['POST'])
def add_tournament():
    tournament_name = request.form['tournament_name']
    game = request.form['game']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    location = request.form['location']
    prize_pool = request.form['prize_pool']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO Tournaments (TournamentName, Game, StartDate, EndDate, Location, PrizePool) VALUES (?, ?, ?, ?, ?, ?)',
                (tournament_name, game, start_date, end_date, location, float(prize_pool)))
    conn.commit()
    conn.close()
    return redirect(url_for('tournaments'))

@app.route('/result/add', methods=['POST'])
def add_result():
    tournament_id = request.form['tournament_id']
    team_id = request.form['team_id']
    placement = request.form['placement']
    prize_money = request.form['prize_money']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO TournamentResults (TournamentID, TeamID, Placement, PrizeMoney) VALUES (?, ?, ?, ?)',
                (tournament_id, team_id, int(placement), float(prize_money)))
    conn.commit()
    conn.close()
    return redirect(url_for('tournaments'))

# ========== TOURNAMENT RESULT EDIT & DELETE ROUTES ==========
@app.route('/result/<int:result_id>/edit', methods=['GET', 'POST'])
def edit_result(result_id):
    conn = get_db_connection()
    if request.method == 'POST':
        tournament_id = request.form['tournament_id']
        team_id = request.form['team_id']
        placement = request.form['placement']
        prize_money = request.form['prize_money']
        
        conn.execute('UPDATE TournamentResults SET TournamentID = ?, TeamID = ?, Placement = ?, PrizeMoney = ? WHERE ResultID = ?',
                    (tournament_id, team_id, int(placement), float(prize_money), result_id))
        conn.commit()
        conn.close()
        return redirect(url_for('tournaments'))
    
    result = conn.execute('SELECT * FROM TournamentResults WHERE ResultID = ?', (result_id,)).fetchone()
    tournaments = conn.execute('SELECT * FROM Tournaments').fetchall()
    teams = conn.execute('SELECT * FROM Teams').fetchall()
    conn.close()
    return render_template('edit_result.html', result=result, tournaments=tournaments, teams=teams)

@app.route('/result/<int:result_id>/delete', methods=['POST'])
def delete_result(result_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM TournamentResults WHERE ResultID = ?', (result_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('tournaments'))

# ========== TOURNAMENT EDIT & DELETE ROUTES ==========
@app.route('/tournament/<int:tournament_id>/edit', methods=['GET', 'POST'])
def edit_tournament(tournament_id):
    conn = get_db_connection()
    if request.method == 'POST':
        tournament_name = request.form['tournament_name']
        game = request.form['game']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        location = request.form['location']
        prize_pool = request.form['prize_pool']
        
        conn.execute('UPDATE Tournaments SET TournamentName = ?, Game = ?, StartDate = ?, EndDate = ?, Location = ?, PrizePool = ? WHERE TournamentID = ?',
                    (tournament_name, game, start_date, end_date, location, float(prize_pool), tournament_id))
        conn.commit()
        conn.close()
        return redirect(url_for('tournaments'))
    
    tournament = conn.execute('SELECT * FROM Tournaments WHERE TournamentID = ?', (tournament_id,)).fetchone()
    conn.close()
    return render_template('edit_tournament.html', tournament=tournament)

@app.route('/tournament/<int:tournament_id>/delete', methods=['POST'])
def delete_tournament(tournament_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM TournamentResults WHERE TournamentID = ?', (tournament_id,))
    conn.execute('DELETE FROM Tournaments WHERE TournamentID = ?', (tournament_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('tournaments'))

# ========== DASHBOARD & REPORTS ==========
@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    
    total_teams = conn.execute('SELECT COUNT(*) as count FROM Teams').fetchone()['count']
    total_players = conn.execute('SELECT COUNT(*) as count FROM Players').fetchone()['count']
    total_equipment = conn.execute('SELECT COUNT(*) as count FROM Equipment').fetchone()['count']
    total_tournaments = conn.execute('SELECT COUNT(*) as count FROM Tournaments').fetchone()['count']
    
    # Top teams by prize money
    top_teams = conn.execute('''
        SELECT t.TeamName, SUM(tr.PrizeMoney) as total_prize
        FROM Teams t
        LEFT JOIN TournamentResults tr ON t.TeamID = tr.TeamID
        GROUP BY t.TeamID
        ORDER BY total_prize DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    return render_template('dashboard.html', 
                         total_teams=total_teams,
                         total_players=total_players,
                         total_equipment=total_equipment,
                         total_tournaments=total_tournaments,
                         top_teams=top_teams)

if __name__ == '__main__':
    # Local development - initialize database
    init_db()
    insert_sample_data()
    app.run(debug=True, port=5000)
