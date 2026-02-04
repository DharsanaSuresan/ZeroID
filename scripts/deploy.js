const hre = require("hardhat");

async function main() {

  // Initial Merkle root (empty tree initialization)
  const initialRoot =
    "0x0000000000000000000000000000000000000000000000000000000000000000";

  // Get contract factory
  const ZeroID = await hre.ethers.getContractFactory("ZeroIDMerkle");

  // Deploy contract
  const contract = await ZeroID.deploy(initialRoot);

  // Wait for deployment
  await contract.deployed();

  console.log("✅ ZeroID Contract Deployed Successfully!");
  console.log("📍 Contract Address:", contract.address);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
