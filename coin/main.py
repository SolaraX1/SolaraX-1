from blockchain import Blockchain
import time
from wallet import Wallet

if __name__ == "__main__":
    blockchain = Blockchain()
    print("Genesis Block Hash:", blockchain.chain[0].hash)

    # Beispiel-Transaktionen hinzufügen
    blockchain.add_transaction({"from": "Alice", "to": "Bob", "amount": 10})
    blockchain.add_transaction({"from": "Bob", "to": "Charlie", "amount": 5})

    # Mining der ausstehenden Transaktionen
    miner_address = "Miner1"
    print(f"Starte Mining für {miner_address}...")
    mined_block = blockchain.mine_pending_transactions(miner_address)
    print("Geminter Block Hash:", mined_block.hash)
    print("Nonce für geminten Block:", mined_block.nonce)
    print("Transaktionen im Block:", mined_block.transactions)

    # Simuliere weitere Transaktionen und einen zweiten Miner
    blockchain.add_transaction({"from": "Bob", "to": "Alice", "amount": 2})
    blockchain.add_transaction({"from": "Alice", "to": "Charlie", "amount": 1})
    miner2_address = "Miner2"
    print(f"Starte Mining für {miner2_address}...")
    mined_block2 = blockchain.mine_pending_transactions(miner2_address)
    print("Geminter Block Hash:", mined_block2.hash)
    print("Nonce für geminten Block:", mined_block2.nonce)
    print("Transaktionen im Block:", mined_block2.transactions)

    # Balances nach dem zweiten Mining anzeigen
    print("Balance von Alice:", blockchain.get_balance("Alice"))
    print("Balance von Bob:", blockchain.get_balance("Bob"))
    print("Balance von Charlie:", blockchain.get_balance("Charlie"))
    print(f"Balance von {miner_address}:", blockchain.get_balance(miner_address))
    print(f"Balance von {miner2_address}:", blockchain.get_balance(miner2_address))

    # --- Netzwerk-Simulation: Zwei Nodes ---
    print("\n--- Netzwerk-Simulation: Zwei Nodes ---")
    node1 = Blockchain()
    node2 = Blockchain()

    # Beide Nodes starten mit eigenen Transaktionen und Minern
    node1.add_transaction({"from": "Alice", "to": "Bob", "amount": 10})
    node1.mine_pending_transactions("MinerA")
    node2.add_transaction({"from": "Alice", "to": "Charlie", "amount": 5})
    node2.mine_pending_transactions("MinerB")

    # Node1 mined noch einen Block
    node1.add_transaction({"from": "Bob", "to": "Charlie", "amount": 2})
    node1.mine_pending_transactions("MinerA")

    print("Balances vor Synchronisation:")
    print("Node1 - Alice:", node1.get_balance("Alice"), "Bob:", node1.get_balance("Bob"), "Charlie:", node1.get_balance("Charlie"), "MinerA:", node1.get_balance("MinerA"))
    print("Node2 - Alice:", node2.get_balance("Alice"), "Bob:", node2.get_balance("Bob"), "Charlie:", node2.get_balance("Charlie"), "MinerB:", node2.get_balance("MinerB"))

    # Nodes synchronisieren (Longest-Chain-Regel)
    node2.add_peer_chain(node1)
    node2.resolve_conflicts()

    print("Balances nach Synchronisation (Node2 übernimmt längste Chain):")
    print("Node2 - Alice:", node2.get_balance("Alice"), "Bob:", node2.get_balance("Bob"), "Charlie:", node2.get_balance("Charlie"), "MinerA:", node2.get_balance("MinerA"), "MinerB:", node2.get_balance("MinerB"))

    # --- Wallet-Demo ---
    print("\n--- Wallet-Demo ---")
    wallet = Wallet()
    print("Adresse:", wallet.address)
    print("Public Key (hex):", wallet.public_key.to_string().hex())
    message = "Testnachricht"
    signature = wallet.sign(message)
    print("Signatur:", signature)
    verified = Wallet.verify_signature(wallet.public_key.to_string().hex(), message, signature)
    print("Signatur gültig?", verified)

    # --- Signierte Transaktion Demo ---
    print("\n--- Signierte Transaktion Demo ---")
    sender_wallet = Wallet()
    recipient_wallet = Wallet()
    tx_data = {
        "from": sender_wallet.address,
        "to": recipient_wallet.address,
        "amount": 5,
        "public_key": sender_wallet.public_key.to_string().hex()
    }
    # Signatur erzeugen
    message = Blockchain().serialize_transaction(tx_data)
    tx_data["signature"] = sender_wallet.sign(message)
    # Transaktion hinzufügen
    bc = Blockchain()
    bc.add_transaction(tx_data)
    bc.mine_pending_transactions(sender_wallet.address)
    print("Balance Sender:", bc.get_balance(sender_wallet.address))
    print("Balance Empfänger:", bc.get_balance(recipient_wallet.address))

    # --- Proof-of-Stake Demo ---
    print("\n--- Proof-of-Stake Demo ---")
    pos_chain = Blockchain(proof_mode='pos')
    w1 = Wallet()
    w2 = Wallet()
    # w1 bekommt initial Coins durch Mining im PoW-Modus (Simulation)
    pow_chain = Blockchain()
    pow_chain.add_transaction({"from": "System", "to": w1.address, "amount": 100})
    pow_chain.mine_pending_transactions(w1.address)
    # Übertrage Coins von w1 zu w2 (signiert)
    tx = {
        "from": w1.address,
        "to": w2.address,
        "amount": 30,
        "public_key": w1.public_key.to_string().hex()
    }
    message = pos_chain.serialize_transaction(tx)
    tx["signature"] = w1.sign(message)
    pos_chain.add_transaction(tx)
    # Block minten (Validator wird automatisch gewählt)
    pos_chain.mine_pending_transactions()
    print("Balance w1:", pos_chain.get_balance(w1.address))
    print("Balance w2:", pos_chain.get_balance(w2.address))

    # --- 1.000.000 SolaraX-Coins an eigene Adresse ---
    my_address = ""  # Trage hier deine Wallet-Adresse ein
    blockchain.add_transaction({"from": "System", "to": my_address, "amount": 1_000_000})
    blockchain.mine_pending_transactions(my_address)
    print(f"Balance von {my_address}: {blockchain.get_balance(my_address)} SolaraX") 