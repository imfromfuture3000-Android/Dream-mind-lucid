pragma solidity ^0.8.20;
contract OneiroSphere {
    mapping(address => string[]) public dreams;
    event DreamInterfaced(address indexed dreamer, string ipfsHash);
    function interfaceDream(string memory ipfsHash) public {
        dreams[msg.sender].push(ipfsHash);
        emit DreamInterfaced(msg.sender, ipfsHash);
    }
}
