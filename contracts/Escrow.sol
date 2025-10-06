// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Escrow {
    IERC20 public usdc;
    address public platform;
    mapping(string => uint256) public escrows;
    mapping(string => address) public providers;

    event GigFunded(string indexed gigId, address indexed hirer, address indexed provider, uint256 amount);
    event GigReleased(string indexed gigId, address indexed provider, uint256 providerAmount, uint256 fee);

    constructor(address _usdc, address _platform) {
        usdc = IERC20(_usdc);
        platform = _platform;
    }

    function fundEscrow(string memory gigId, address provider, uint256 amount) external {
        require(usdc.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        escrows[gigId] = amount;
        providers[gigId] = provider;
        emit GigFunded(gigId, msg.sender, provider, amount);
    }

    function approveGig(string memory gigId) external {
        require(msg.sender == platform, "Only platform can approve");
        uint256 amount = escrows[gigId];
        address provider = providers[gigId];
        require(amount > 0, "No funds in escrow");
        require(provider != address(0), "Provider not set");
        uint256 fee = amount * 5 / 1000; // 0.5% fee
        uint256 providerAmount = amount - fee;
        escrows[gigId] = 0;
        require(usdc.transfer(platform, fee), "Fee transfer failed");
        require(usdc.transfer(provider, providerAmount), "Provider transfer failed");
        emit GigReleased(gigId, provider, providerAmount, fee);
    }
}