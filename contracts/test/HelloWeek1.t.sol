// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {Test} from "forge-std/Test.sol";
import {HelloWeek1} from "../src/HelloWeek1.sol";

contract HelloWeek1Test is Test {
    HelloWeek1 internal hello;
    address internal alice = makeAddr("alice");
    address internal bob   = makeAddr("bob");

    event Greeted(address indexed caller, string newGreeting, uint256 totalCount);
    event Reset(address indexed caller);

    function setUp() public {
        vm.prank(alice);
        hello = new HelloWeek1("hello week 1");
    }

    function testInitialState() public view {
        assertEq(hello.deployer(), alice);
        assertEq(hello.greeting(), "hello week 1");
        assertEq(hello.greetCount(), 0);
    }

    function testAnyoneCanGreet() public {
        vm.expectEmit(true, false, false, true, address(hello));
        emit Greeted(bob, "GM from bob", 1);
        vm.prank(bob);
        hello.greet("GM from bob");

        assertEq(hello.greeting(), "GM from bob");
        assertEq(hello.greetCount(), 1);
    }

    function testEmptyGreetingReverts() public {
        vm.prank(bob);
        vm.expectRevert(HelloWeek1.EmptyGreeting.selector);
        hello.greet("");
    }

    function testOnlyDeployerCanReset() public {
        vm.prank(bob);
        vm.expectRevert(abi.encodeWithSelector(HelloWeek1.NotDeployer.selector, bob));
        hello.reset();

        vm.prank(alice);
        hello.reset();
        assertEq(hello.greeting(), "");
        assertEq(hello.greetCount(), 0);
    }

    function testFuzz_GreetIncrementsCount(string calldata first, string calldata second) public {
        vm.assume(bytes(first).length > 0 && bytes(second).length > 0);
        vm.prank(bob);
        hello.greet(first);
        vm.prank(alice);
        hello.greet(second);
        assertEq(hello.greetCount(), 2);
        assertEq(hello.greeting(), second);
    }
}
