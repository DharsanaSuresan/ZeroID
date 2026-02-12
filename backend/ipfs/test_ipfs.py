from ipfs_service import upload_json_to_ipfs

test_data = {
    "name": "Saniya Mhatre",
    "course": "BTech Computer Engineering",
    "university": "SNDT Women’s University"
}

ipfs_hash = upload_json_to_ipfs(test_data)

print("Uploaded to IPFS successfully!")
print("IPFS CID:", ipfs_hash)
print("View at: https://gateway.pinata.cloud/ipfs/" + ipfs_hash)
