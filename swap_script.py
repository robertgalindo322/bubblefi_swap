from web3 import Web3
import json
import time

# === Загрузка конфигурации из config.json ===
with open("config.json", "r") as f:
    config = json.load(f)

RPC_URL = config["rpc_url"]
CHAIN_ID = config["chain_id"]
CONTRACT_ADDRESS = config["contract_address"]
WALLET_ADDRESS = config["wallet_address"]

# === Чтение приватного ключа из privatekeys.txt ===
PRIVATE_KEY = None
with open("privatekeys.txt", "r") as f:
    for line in f:
        if line.strip().startswith("wallet1_private_key="):
            PRIVATE_KEY = line.strip().split("=")[1]
            break

if not PRIVATE_KEY:
    raise Exception("Приватный ключ не найден в privatekeys.txt")

# === ABI контракта свопа (заменить на актуальный) ===
SWAP_CONTRACT_ABI = json.loads('[]')  # Подставьте реальный ABI

# === Инициализация Web3 ===
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Не удалось подключиться к ноде")

# === Функция отправки транзакции ===
def send_tx(w3, contract, function_name, args):
    nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)

    transaction = contract.functions[function_name](*args).build_transaction({
        'chainId': CHAIN_ID,
        'gas': 300000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Транзакция отправлена: {tx_hash.hex()}")

    # Ожидание завершения
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"Статус: {tx_receipt.status}")
    return tx_receipt

# === Основная логика ===
def main():
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=SWAP_CONTRACT_ABI)

    # Пример: вызов функции swapExactETHForTokens
    tx_receipt = send_tx(
        w3,
        contract,
        'swapExactETHForTokens',
        [
            0,  # amountOutMin
            ["0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", "0x..."],  # path
            WALLET_ADDRESS,
            int(time.time()) + 10 * 60  # deadline
        ]
    )
    print("Транзакция завершена:", tx_receipt.transactionHash.hex())

if __name__ == "__main__":
    main()
