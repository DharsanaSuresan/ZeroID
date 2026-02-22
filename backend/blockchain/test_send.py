from backend.blockchain.send_root import send_root

# fake root for testing
root = "0x" + "12"*32

gas = send_root(root)
print("Gas:", gas)
