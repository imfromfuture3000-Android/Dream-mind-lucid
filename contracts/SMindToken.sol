// SPDX-License-Identifier: MIT
// contracts/SMindToken.sol - Cognitive Staking Token
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract SMindToken is IERC20 {
    string public name = "SMIND Token";
    string public symbol = "SMIND";
    uint8 public decimals = 18;
    
    uint256 private _totalSupply = 777777777 * 10**18; // 777,777,777 SMIND tokens
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    address public immutable owner;
    
    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = 0x4B1a58A3057d03888510d93B52ABad9Fee9b351d;
        _balances[owner] = _totalSupply;
        emit Transfer(address(0), owner, _totalSupply);
    }

    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function allowance(address owner_, address spender) public view override returns (uint256) {
        return _allowances[owner_][spender];
    }

    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "ERC20: transfer amount exceeds allowance");
        
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "ERC20: transfer from zero address");
        require(to != address(0), "ERC20: transfer to zero address");
        require(_balances[from] >= amount, "ERC20: transfer amount exceeds balance");

        _balances[from] -= amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _approve(address owner_, address spender, uint256 amount) internal {
        require(owner_ != address(0), "ERC20: approve from zero address");
        require(spender != address(0), "ERC20: approve to zero address");
        
        _allowances[owner_][spender] = amount;
        emit Approval(owner_, spender, amount);
    }

    function mint(address to, uint256 amount) public onlyOwner {
        require(to != address(0), "ERC20: mint to zero address");
        
        _totalSupply += amount;
        _balances[to] += amount;
        emit Transfer(address(0), to, amount);
        emit Mint(to, amount);
    }

    function burn(uint256 amount) public {
        require(_balances[msg.sender] >= amount, "ERC20: burn amount exceeds balance");
        
        _balances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Transfer(msg.sender, address(0), amount);
        emit Burn(msg.sender, amount);
    }
}