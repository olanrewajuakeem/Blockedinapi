import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const MockUSDC = await ethers.getContractFactory("MockUSDC");
  const usdc = await MockUSDC.deploy();
  await usdc.waitForDeployment();
  console.log("MockUSDC deployed to:", await usdc.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});