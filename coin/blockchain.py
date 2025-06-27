import hashlib
import time
from block import Block

class Blockchain:
    def __init__(self, proof_mode='pow'):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2  # Für Proof-of-Work
        self.pending_transactions = []
        self.mining_reward = 50  # Belohnung pro Block
        self.proof_mode = proof_mode  # 'pow' oder 'pos'

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address):
        if self.proof_mode == 'pow':
            return self.mine_pending_transactions_pow(miner_address)
        else:
            return self.mine_pending_transactions_pos(miner_address)

    def mine_pending_transactions_pow(self, miner_address):
        # Füge die Mining-Belohnung als Transaktion hinzu
        reward_tx = {"from": "System", "to": miner_address, "amount": self.mining_reward}
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def mine_pending_transactions_pos(self, validator_address=None):
        # Wähle Validator nach Guthaben (einfach: proportional zum Guthaben)
        if not validator_address:
            validator_address = self.select_validator()
        reward_tx = {"from": "System", "to": validator_address, "amount": self.mining_reward}
        self.pending_transactions.append(reward_tx)
        new_block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_latest_block().hash)
        # Kein Mining nötig, Block wird direkt hinzugefügt
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def select_validator(self):
        # Wähle Validator proportional zum Guthaben (Lotterie)
        balances = {}
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict):
                    if tx.get("from") != "System":
                        balances[tx.get("from")] = balances.get(tx.get("from"), 0) - tx.get("amount", 0)
                    balances[tx.get("to")] = balances.get(tx.get("to"), 0) + tx.get("amount", 0)
        # Entferne System-Adresse
        balances.pop("System", None)
        # Lotterie: Je mehr Guthaben, desto mehr Lose
        import random
        weighted = []
        for addr, bal in balances.items():
            if bal > 0:
                weighted += [addr] * int(bal)
        if weighted:
            return random.choice(weighted)
        return None

    def serialize_transaction(self, tx):
        # Serialisiere die Transaktionsdaten (ohne Signatur) für die Signaturprüfung
        return f"{tx.get('from')}->{tx.get('to')}:{tx.get('amount')}"

    def add_transaction(self, transaction):
        # Mining-Belohnung darf immer hinzugefügt werden
        if transaction.get("from") == "System":
            self.pending_transactions.append(transaction)
            return True
        # Prüfe, ob der Absender genug Guthaben hat
        if self.get_balance(transaction.get("from")) >= transaction.get("amount", 0):
            # Prüfe Signatur
            from wallet import Wallet
            message = self.serialize_transaction(transaction)
            if not ("signature" in transaction and "public_key" in transaction):
                print("Transaktion abgelehnt: Signatur oder Public Key fehlt.")
                return False
            if not Wallet.verify_signature(transaction["public_key"], message, transaction["signature"]):
                print("Transaktion abgelehnt: Signatur ungültig.")
                return False
            # Prüfe, ob Adresse zum Public Key passt
            import hashlib
            pubkey_bytes = bytes.fromhex(transaction["public_key"])
            address = hashlib.sha256(pubkey_bytes).hexdigest()
            if address != transaction["from"]:
                print("Transaktion abgelehnt: Public Key passt nicht zur Absender-Adresse.")
                return False
            self.pending_transactions.append(transaction)
            return True
        else:
            print(f"Transaktion abgelehnt: {transaction.get('from')} hat nicht genug Guthaben.")
            return False

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict):
                    if tx.get("from") == address:
                        balance -= tx.get("amount", 0)
                    if tx.get("to") == address:
                        balance += tx.get("amount", 0)
        return balance

    def add_peer_chain(self, peer_chain):
        # Füge eine Peer-Chain hinzu (Simulation)
        if not hasattr(self, 'peer_chains'):
            self.peer_chains = []
        self.peer_chains.append(peer_chain)

    def resolve_conflicts(self):
        # Longest-Chain-Regel: Übernehme die längste gültige Chain aus den Peers
        if not hasattr(self, 'peer_chains'):
            return False
        max_length = len(self.chain)
        new_chain = None
        for peer in self.peer_chains:
            if len(peer.chain) > max_length:
                max_length = len(peer.chain)
                new_chain = peer.chain
        if new_chain:
            self.chain = new_chain
            return True
        return False 