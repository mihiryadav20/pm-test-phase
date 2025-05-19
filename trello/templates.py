"""
Templates for rendering HTML pages
"""

# Template for the index page
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trello OAuth</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
        h1 { color: #0079BF; }
        .login-button { 
            display: inline-block; 
            padding: 10px 20px; 
            background-color: #0079BF; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px;
            font-weight: bold;
        }
        .login-button:hover { background-color: #005b8f; }
        .container { 
            max-width: 600px; 
            margin: 100px auto; 
            text-align: center;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Trello OAuth Demo</h1>
        <p>Connect with your Trello account to view your boards and cards.</p>
        <a href="/login" class="login-button">Login with Trello</a>
    </div>
</body>
</html>
"""

# Template for the dashboard page
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trello Boards</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
        h1 { color: #0079BF; }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; padding: 15px; background-color: #f0f0f0; border-radius: 5px; transition: all 0.2s ease; }
        li:hover { transform: translateY(-2px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        a { text-decoration: none; color: #0079BF; display: block; }
        a:hover { text-decoration: underline; }
        .logout { 
            margin-top: 20px; 
            display: inline-block; 
            padding: 10px 20px; 
            background-color: #EB5A46; 
            color: white; 
            border-radius: 5px;
            text-decoration: none;
        }
        .logout:hover { background-color: #CF513D; }
        .header { display: flex; justify-content: space-between; align-items: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Trello Boards</h1>
            <a href="/logout" class="logout">Logout</a>
        </div>
        <ul>
            {% for board in boards %}
                <li>
                    <a href="/board/{{ board.id }}">{{ board.name }}</a>
                </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# Template for the board view page
BOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ board.name }} - Trello Board</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
        h1 { color: #0079BF; margin: 0; }
        .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 20px;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .board-container { 
            display: flex; 
            overflow-x: auto; 
            padding-bottom: 20px; 
            margin: 0 -10px; /* Offset for list padding */
        }
        .list { 
            min-width: 300px; 
            margin: 0 10px; 
            background-color: #ebecf0; 
            border-radius: 5px; 
            padding: 10px; 
            height: fit-content;
            max-height: 80vh;
            overflow-y: auto;
        }
        .list-header { 
            font-weight: bold; 
            margin-bottom: 10px; 
            padding-bottom: 10px; 
            border-bottom: 1px solid #ddd;
        }
        .card { 
            background-color: white; 
            padding: 10px; 
            margin-bottom: 10px; 
            border-radius: 3px; 
            box-shadow: 0 1px 0 rgba(9,30,66,.25);
            transition: all 0.2s ease;
        }
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 3px 5px rgba(9,30,66,.2);
        }
        .card-title { font-weight: bold; }
        .card-desc { font-size: 14px; margin-top: 5px; color: #5e6c84; }
        .card-due { font-size: 12px; color: #5e6c84; margin-top: 5px; }
        .card-labels { display: flex; flex-wrap: wrap; margin-top: 5px; }
        .card-label { 
            height: 8px; 
            width: 40px; 
            border-radius: 4px; 
            margin-right: 4px; 
            margin-bottom: 4px; 
        }
        .card-members { font-size: 12px; color: #5e6c84; margin-top: 5px; }
        .back-link { 
            display: inline-block; 
            color: #0079BF; 
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 3px;
            transition: background-color 0.2s ease;
        }
        .back-link:hover { 
            background-color: rgba(0, 121, 191, 0.1);
            text-decoration: underline;
        }
        .completed { text-decoration: line-through; opacity: 0.7; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <a href="/dashboard" class="back-link">← Back to Boards</a>
            <h1>{{ board.name }}</h1>
        </div>
        <a href="/logout" class="back-link">Logout</a>
    </div>
    
    <div class="board-container">
        {% for list in lists %}
            <div class="list">
                <div class="list-header">{{ list.name }}</div>
                {% for card in list.cards %}
                    <div class="card{% if card.dueComplete %} completed{% endif %}">
                        <div class="card-title">{{ card.name }}</div>
                        {% if card.desc %}<div class="card-desc">{{ card.desc }}</div>{% endif %}
                        {% if card.due %}<div class="card-due">Due: {{ card.due }}</div>{% endif %}
                        {% if card.labels %}
                            <div class="card-labels">
                                {% for label in card.labels %}
                                    <div class="card-label" style="background-color: {% if label.color %}{{ label.color }}{% else %}#b3b3b3{% endif %};" title="{{ label.name }}"></div>
                                {% endfor %}
                            </div>
                        {% endif %}
                        {% if card.members %}
                            <div class="card-members">
                                Members: {% for member in card.members %}{{ member.fullName }}{% if not loop.last %}, {% endif %}{% endfor %}
                            </div>
                        {% endif %}
                    </div>
                {% endfor %}
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""
