from flask import Flask, render_template, request, jsonify , redirect , url_for
import chess
import chess.svg
import chess.engine
import google.generativeai as genai
app = Flask(__name__)
board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("C:/Users/G karthik/Downloads/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe")
GEMINI_API_KEY = "AIzaSyAAKySqbqHlbiwmlzMfBpobaGylnSLQgDo"  # Replace with your API key
genai.configure(api_key=GEMINI_API_KEY)
difficulty_level = 20

USER_CREDENTIALS={"admin":"password"}
session={}
#engine.configure({'Skill Level': difficulty_level})
"""@app.route('/')
def index():
    return render_template('index.html', board_svg=chess.svg.board(board=board))
"""

# Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session["user"] = username  # Store user in session
            return redirect(url_for("board_select"))  # Redirect to game selection
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/board_select")
def board_select():
    if "user" not in session:
        return redirect(url_for("login"))  # Redirect to login if not authenticated

    return render_template("board_select.html")


# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))




# Chess Game Page (Protected Route)
@app.route("/index", methods=["GET", "POST"])
def index():
    #print("in index")
    if "user" not in session:
        return redirect(url_for("login"))  # Redirect to login if not authenticated

    return render_template('index.html', board_svg=chess.svg.board(board=board), difficulty=difficulty_level)


@app.route('/set_difficulty', methods=['POST'])
def set_difficulty():
    global difficulty_level
    data = request.get_json()
    level = int(data.get("level", 1))
    #print(level)
    if 0 <= level <= 20:
        difficulty_level = level
        print(difficulty_level)
        engine.configure({'Skill Level': difficulty_level})
        return jsonify({"status": "success", "difficulty": difficulty_level})
    else:
        return jsonify({"status": "error", "message": "Invalid difficulty level. Choose a number between 0 and 20."})


@app.route('/move', methods=['POST'])
def move():
    data = request.get_json()
    move_uci = data.get("move")
    if move_uci in [str(m) for m in board.legal_moves]:
        board.push(chess.Move.from_uci(move_uci))

        if not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(depth=difficulty_level))
            print(get_move_explanation(result),difficulty_level)
            board.push(result.move)

        return jsonify({"status": "success", "board": chess.svg.board(board=board)})
    else:
        return jsonify({"status": "invalid move"})


def get_move_explanation(move_uci):
    """Generate a natural language explanation for a given move using Gemini AI."""
    prompt = f"Explain why the move {move_uci} is a good choice in a chess game.{board.fen()} :this is the board state when move is played - give in two lines and best move for opponent"
    print(board.fen())
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Use the correct model
        response = model.generate_content(prompt)
        explanation = response.text if response else "No explanation available."
    except Exception as e:
        explanation = f"Error fetching explanation: {str(e)}"

    print(f"Move: {move_uci}\nExplanation: {explanation}")  # Print explanation to terminal
    return explanation



@app.route('/reset', methods=['POST'])
def reset():
    global board
    board = chess.Board()
    return jsonify({"status": "reset", "board": chess.svg.board(board=board)})


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get("query", "").lower()

    if not user_query:
        return jsonify({"response": "Please enter a question."})

    # Check if the user is asking about the best move
    if "best move" in user_query or "what should I play" in user_query or "suggest a move" in user_query or "make a move" in user_query or "move" in user_query:
        if board.is_game_over():
            return jsonify({"response": "The game is already over!"})

        # Get best move from Stockfish
        result = engine.play(board, chess.engine.Limit(depth=difficulty_level))
        best_move = result.move
        board_fen = board.fen()

        # Generate AI explanation for the move
        prompt = f"Explain why the move {best_move} is the best choice in this chess position: {board_fen}. Provide a brief two-line response along with a recommended counter-move for the opponent."

        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            explanation = response.text if response else "No explanation available."
        except Exception as e:
            explanation = f"Error fetching explanation: {str(e)}"

        return jsonify({"response": f"Best move: {best_move}\n{explanation}"})

    # If the query is not about the best move, use Gemini AI for a general chess response
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(user_query)
        bot_reply = response.text if response else "I couldn't understand that."
    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    return jsonify({"response": bot_reply})


if __name__ == '__main__':
    app.run(debug=True)
    engine.quit()
