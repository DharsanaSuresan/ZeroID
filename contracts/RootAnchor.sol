// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RootAnchor {

    bytes32 public merkleRoot;
    address public owner;

    event RootUpdated(bytes32 newRoot);

    constructor() {
        owner = msg.sender;
    }

    function updateRoot(bytes32 newRoot) external {
        require(msg.sender == owner, "Only owner");
        merkleRoot = newRoot;
        emit RootUpdated(newRoot);
    }

    function getRoot() external view returns (bytes32) {
        return merkleRoot;
    }
}
