// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title HelloWeek1
/// @notice Minimal contract for AI x Web3 School Week 1 — illustrates state, events,
///         and a small access-control rule (only deployer can reset).
/// @dev Intentionally tiny so the deploy & call trace is fully auditable in Etherscan.
contract HelloWeek1 {
    address public immutable deployer;
    string public greeting;
    uint256 public greetCount;

    event Greeted(address indexed caller, string newGreeting, uint256 totalCount);
    event Reset(address indexed caller);

    error NotDeployer(address caller);
    error EmptyGreeting();

    constructor(string memory _initial) {
        deployer = msg.sender;
        greeting = _initial;
        emit Greeted(msg.sender, _initial, 0);
    }

    /// @notice Anyone can post a greeting; counter increments.
    function greet(string calldata _greeting) external {
        if (bytes(_greeting).length == 0) revert EmptyGreeting();
        greeting = _greeting;
        unchecked { greetCount += 1; }
        emit Greeted(msg.sender, _greeting, greetCount);
    }

    /// @notice Only deployer can wipe state — demonstrates a minimal permission check.
    function reset() external {
        if (msg.sender != deployer) revert NotDeployer(msg.sender);
        greeting = "";
        greetCount = 0;
        emit Reset(msg.sender);
    }
}
