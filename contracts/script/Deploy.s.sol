// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {Script, console} from "forge-std/Script.sol";
import {HelloWeek1} from "../src/HelloWeek1.sol";

contract DeployHelloWeek1 is Script {
    function run() external returns (HelloWeek1 hello) {
        string memory initial = vm.envOr("INITIAL_GREETING", string("GM AI x Web3 School"));
        uint256 pk = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(pk);
        hello = new HelloWeek1(initial);
        vm.stopBroadcast();

        console.log("HelloWeek1 deployed at:", address(hello));
        console.log("Initial greeting     :", hello.greeting());
        console.log("Deployer             :", hello.deployer());
    }
}
