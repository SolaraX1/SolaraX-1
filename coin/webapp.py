from flask import Flask, request, jsonify, render_template_string
from blockchain import Blockchain
import requests

app = Flask(__name__)
blockchain = Blockchain()
peers = set()

HTML = '''
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SolaraX Blockchain Explorer</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <h1 class="mb-4">SolaraX Blockchain Explorer</h1>
  <div class="row">
    <div class="col-md-8">
      <h2>Chain</h2>
      <div class="accordion" id="chainAccordion">
        {% for block in chain %}
        <div class="accordion-item">
          <h2 class="accordion-header" id="heading{{ loop.index }}">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse{{ loop.index }}" aria-expanded="false" aria-controls="collapse{{ loop.index }}">
              Block #{{ block['index'] }} | Hash: {{ block['hash'][:16] }}...
            </button>
          </h2>
          <div id="collapse{{ loop.index }}" class="accordion-collapse collapse" aria-labelledby="heading{{ loop.index }}" data-bs-parent="#chainAccordion">
            <div class="accordion-body">
              <strong>Hash:</strong> {{ block['hash'] }}<br>
              <strong>Vorheriger Hash:</strong> {{ block['previous_hash'] }}<br>
              <strong>Nonce:</strong> {{ block['nonce'] }}<br>
              <strong>Timestamp:</strong> {{ block['timestamp'] }}<br>
              <strong>Transaktionen:</strong>
              <ul>
                {% for tx in block['transactions'] %}
                  <li>{{ tx }}</li>
                {% endfor %}
              </ul>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    <div class="col-md-4">
      <div class="card mb-4">
        <div class="card-body">
          <h2 class="card-title">Neue Transaktion</h2>
          <form action="/add_transaction" method="post">
            <div class="mb-2">
              <label class="form-label">Von</label>
              <input name="from" class="form-control">
            </div>
            <div class="mb-2">
              <label class="form-label">An</label>
              <input name="to" class="form-control">
            </div>
            <div class="mb-2">
              <label class="form-label">Betrag</label>
              <input name="amount" type="number" class="form-control">
            </div>
            <button type="submit" class="btn btn-primary">Transaktion senden</button>
          </form>
        </div>
      </div>
      <div class="card mb-4">
        <div class="card-body">
          <h2 class="card-title">Mining</h2>
          <form action="/mine" method="post">
            <div class="mb-2">
              <label class="form-label">Miner-Adresse</label>
              <input name="miner" class="form-control">
            </div>
            <button type="submit" class="btn btn-success">Block minen</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route("/")
def index():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return render_template_string(HTML, chain=chain_data)

# --- REST-API ---
@app.route("/chain", methods=["GET"])
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return jsonify({"length": len(chain_data), "chain": chain_data})

@app.route("/add_transaction", methods=["POST"])
def add_transaction_api():
    tx = request.get_json() if request.is_json else request.form.to_dict()
    if "amount" in tx:
        try:
            tx["amount"] = float(tx["amount"])
        except:
            pass
    success = blockchain.add_transaction(tx)
    return jsonify({"success": success})

@app.route("/mine", methods=["POST"])
def mine_api():
    miner = request.json.get("miner") if request.is_json else request.form.get("miner")
    block = blockchain.mine_pending_transactions(miner)
    return jsonify({"block": block.__dict__})

@app.route("/register_node", methods=["POST"])
def register_node():
    node = request.json.get("node")
    if node:
        peers.add(node)
        return jsonify({"success": True, "peers": list(peers)})
    return jsonify({"success": False})

@app.route("/resolve", methods=["GET"])
def consensus():
    global blockchain
    replaced = False
    for node in peers:
        try:
            resp = requests.get(f"{node}/chain")
            if resp.status_code == 200:
                data = resp.json()
                if data["length"] > len(blockchain.chain):
                    # Übernehme die längste Chain
                    from block import Block
                    new_chain = []
                    for b in data["chain"]:
                        new_chain.append(Block(
                            b['index'], b['transactions'], b['timestamp'], b['previous_hash'], b['nonce']
                        ))
                    blockchain.chain = new_chain
                    replaced = True
        except Exception:
            continue
    return jsonify({"replaced": replaced, "chain": [block.__dict__ for block in blockchain.chain]})

if __name__ == "__main__":
    app.run(debug=True, port=5000) 