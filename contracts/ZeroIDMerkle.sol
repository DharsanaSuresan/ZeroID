// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ZeroIDMerkle {

    bytes32 public merkleRoot;
    address public admin;

    event RootUpdated(bytes32 oldRoot, bytes32 newRoot);

    constructor(bytes32 _initialRoot) {
        admin = msg.sender;
        merkleRoot = _initialRoot;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "ZeroID: Unauthorized");
        _;
    }

    function updateMerkleRoot(bytes32 _newRoot) external onlyAdmin {
        bytes32 oldRoot = merkleRoot;
        merkleRoot = _newRoot;
        emit RootUpdated(oldRoot, _newRoot);
    }

    function verifyProof(
        bytes32[] calldata proof,
        bytes32 leaf
    ) external view returns (bool) {

        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            computedHash = keccak256(
                abi.encodePacked(computedHash, proof[i])
            );
        }

        return computedHash == merkleRoot;
    }

    function transferAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Invalid address");
        admin = newAdmin;
    }
}
