import pkg from "hardhat";
const { ethers } = pkg;

async function main() {
  const usdcAddress = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"; 
  const Escrow = await ethers.getContractFactory("Escrow");
  const escrow = await Escrow.deploy(usdcAddress);
  await escrow.waitForDeployment();
  console.log("Escrow deployed to:", await escrow.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});