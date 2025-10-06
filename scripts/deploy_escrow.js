const { ethers } = require("hardhat");

async function main() {
    const Escrow = await ethers.getContractFactory("Escrow");
    const escrow = await Escrow.deploy(
        "0x036CbD53842c5426634e7929541eC2318f3dCF7e", 
        "0x6F072C39423F15AD0D57C5CeD599DBf071E3F3FD" 
    );
    await escrow.waitForDeployment();
    console.log("Escrow deployed to:", escrow.target);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});