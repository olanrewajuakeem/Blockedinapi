require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: "0.8.20", // Matches deployed contract
  networks: {
    base_sepolia: {
      url: "https://base-sepolia.g.alchemy.com/v2/DUE-KloSh-vpMsfffjSm3",
      accounts: ["0x0737f840a13cb021223a79b45aeef62f06bbe8bf68d4a1d1dd7ccee2fa500bf7"]
    }
  },
  etherscan: {
    apiKey: "ZIDE7Q71CTATUHZTGRYRIP3W3KBYTQPCHB", // Replace with Etherscan API key
    customChains: [
      {
        network: "base_sepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org"
        }
      }
    ]
  },
  sourcify: {
    enabled: true
  }
};