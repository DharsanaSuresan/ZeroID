// import { HardhatUserConfig } from "hardhat/config";
// import "@nomiclabs/hardhat-ethers";
// import * as dotenv from "dotenv";

// // dotenv.config();

// const config: HardhatUserConfig = {
//   solidity: "0.8.20"
//   // ,
//   // networks: {
//   //   sepolia: {
//   //     url: process.env.SEPOLIA_RPC_URL!,
//   //     accounts: [process.env.SEPOLIA_PRIVATE_KEY!],
//   //   },
//   // },
// };

// export default config;

import { HardhatUserConfig } from "hardhat/config";
import "@nomiclabs/hardhat-ethers";
import * as dotenv from "dotenv";

dotenv.config();

const config: HardhatUserConfig = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL!,
      accounts: [process.env.SEPOLIA_PRIVATE_KEY!],
      chainId: 11155111,
    },
  },
};

export default config;

