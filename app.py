from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI()

state = {
    "r": 4,
    "c": 4,
    "player": [0, 0],
    "pits": [],
    "visited": [[0, 0]],
    "status": "ACTIVE",
    "safe_count": 1
}

class Init(BaseModel):
    rows: int
    cols: int

class Move(BaseModel):
    x: int
    y: int

@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Grid Simulation</title>
    <style>
        :root {
            --bg-color: #f4f7f6;
            --panel-bg: #ffffff;
            --border-color: #e1e8ed;
            --primary-text: #2c3e50;
            --secondary-text: #7f8c8d;
            --accent-blue: #3498db;
            --accent-green: #2ecc71;
            --accent-red: #e74c3c;
            --cell-size: 100px;
        }

        body {
            background-color: var(--bg-color);
            color: var(--primary-text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 40px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        h1 {
            margin-top: 0;
            font-weight: 300;
            color: var(--primary-text);
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            width: 100%;
            max-width: 800px;
            margin-bottom: 30px;
        }

        .stat-box {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            text-align: center;
        }

        .stat-label {
            font-size: 0.8rem;
            color: var(--secondary-text);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-text);
        }

        #status.status-dead {
            color: var(--accent-red);
        }

        .grid-container {
            background: var(--panel-bg);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        .grid {
            display: grid;
            gap: 10px;
        }

        .cell {
            width: var(--cell-size);
            height: var(--cell-size);
            background-color: #f9fbfd;
            border: 1px solid #dce4ec;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            color: #bdc3c7;
            font-size: 0.85rem;
        }

        .cell:hover:not(.player):not(.pit) {
            background-color: #f0f4f8;
            border-color: var(--accent-blue);
            transform: translateY(-2px);
        }

        .cell.visited {
            background-color: #eafaf1;
            border-color: #abebc6;
            color: #27ae60;
        }

        .cell.player {
            background-color: #ebf5fb;
            border-color: var(--accent-blue);
            box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
            color: var(--accent-blue);
            font-weight: 600;
            transform: scale(1.03);
        }

        .cell.pit {
            background-color: #fdf2f2;
            border-color: #f5b7b1;
            color: var(--accent-red);
            font-weight: bold;
            font-size: 1.5rem;
        }

        button {
            background-color: var(--accent-blue);
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 1rem;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 30px;
            transition: background-color 0.2s;
            font-weight: 600;
        }

        button:hover {
            background-color: #2980b9;
        }
        
        button:active {
            transform: translateY(1px);
        }
    </style>
</head>
<body>

    <h1>Simulation Control Panel</h1>

    <button onclick="init()">Reset Environment</button>

    <div class="dashboard">
        <div class="stat-box">
            <div class="stat-label">Cycles</div>
            <div class="stat-value">N/A</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Safe Cells Logged</div>
            <div id="safe-cells" class="stat-value">0</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">System Status</div>
            <div id="status" class="stat-value">INITIALIZING</div>
        </div>
    </div>

    <div class="grid-container">
        <div id="grid"></div>
    </div>

<script>
let rows=4, cols=4;

async function init(){
    let res = await fetch('/init',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({rows:rows, cols:cols})
    });
    let data = await res.json();
    render(data);
}

async function move(x, y){
    let res = await fetch('/move',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({x,y})
    });
    let data = await res.json();
    render(data);
}

function render(data){
    const grid = document.getElementById("grid");
    const statusVal = document.getElementById("status");
    const safeVal = document.getElementById("safe-cells");

    grid.innerHTML = "";
    grid.className = "grid";
    grid.style.gridTemplateColumns = `repeat(${data.c}, 1fr)`;

    statusVal.innerText = data.status;
    if (data.status === "TERMINATED") {
        statusVal.classList.add("status-dead");
    } else {
        statusVal.classList.remove("status-dead");
    }
    
    safeVal.innerText = data.safe_count;

    for(let i=0; i<data.r; i++){
        for(let j=0; j<data.c; j++){
            const cell = document.createElement("div");
            cell.className = "cell";
            
            const isPlayer = data.player[0] == i && data.player[1] == j;
            const isPit = data.pits.some(p => p[0] == i && p[1] == j);
            const isVisited = data.visited.some(v => v[0] == i && v[1] == j);

            if(isVisited) cell.classList.add("visited");
            
            if(isPlayer) {
                cell.classList.add("player");
                cell.innerText = "AGENT";
            } else if (isPit && (data.status === "TERMINATED" || isVisited)) {
                cell.classList.add("pit");
                cell.innerText = "X";
            } else {
                cell.innerText = `${i},${j}`;
            }

            if(data.status === "ACTIVE") {
                cell.onclick = () => move(i, j);
            } else {
                cell.style.cursor = "default";
            }

            grid.appendChild(cell);
        }
    }
}

window.onload = init;
</script>

</body>
</html>
"""

@app.post("/init")
def init(data: Init):
    global state
    r, c = data.rows, data.cols
    pits = []
    for i in range(r):
        for j in range(c):
            if (i, j) != (0, 0) and random.random() < 0.15:
                pits.append([i, j])

    state = {
        "r": r,
        "c": c,
        "player": [0, 0],
        "pits": pits,
        "visited": [[0, 0]],
        "status": "ACTIVE",
        "safe_count": 1
    }
    return state

@app.post("/move")
def move(data: Move):
    global state
    if state["status"] == "TERMINATED":
        return state

    state["player"] = [data.x, data.y]

    if [data.x, data.y] in state["pits"]:
        state["status"] = "TERMINATED"
    else:
        if [data.x, data.y] not in state["visited"]:
            state["visited"].append([data.x, data.y])
            state["safe_count"] = len(state["visited"])

    return state