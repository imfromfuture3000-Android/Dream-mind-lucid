// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title DreamPriceOracle
 * @dev Price oracle for Dream-Mind-Lucid tokens
 */
contract DreamPriceOracle is Ownable, Pausable {
    // Price feed configuration
    struct PriceFeed {
        AggregatorV3Interface aggregator;
        uint8 decimals;
        bool isActive;
    }

    // Token price data
    struct TokenPrice {
        uint256 price;      // Price in USD (18 decimals)
        uint256 timestamp;  // Last update timestamp
        uint256 volume24h;  // 24h trading volume
        int8 priceChange;   // 24h price change percentage
    }

    // Mappings
    mapping(address => PriceFeed) public priceFeeds;
    mapping(address => TokenPrice) public tokenPrices;
    mapping(address => bool) public authorizedUpdaters;

    // Constants
    uint256 public constant PRICE_EXPIRY = 1 hours;
    uint256 public constant MAX_PRICE_CHANGE = 50; // 50% max change

    // Events
    event PriceUpdated(address token, uint256 price, uint256 timestamp);
    event PriceFeedAdded(address token, address aggregator);
    event UpdaterAdded(address updater);
    event UpdaterRemoved(address updater);

    constructor() {
        authorizedUpdaters[msg.sender] = true;
    }

    // Modifiers
    modifier onlyAuthorizedUpdater() {
        require(authorizedUpdaters[msg.sender], "Not authorized");
        _;
    }

    /**
     * @dev Add a new price feed for a token
     */
    function addPriceFeed(
        address token,
        address aggregator
    ) external onlyOwner {
        require(token != address(0), "Invalid token");
        require(aggregator != address(0), "Invalid aggregator");

        AggregatorV3Interface feed = AggregatorV3Interface(aggregator);
        priceFeeds[token] = PriceFeed({
            aggregator: feed,
            decimals: feed.decimals(),
            isActive: true
        });

        emit PriceFeedAdded(token, aggregator);
    }

    /**
     * @dev Update price data for a token
     */
    function updatePrice(
        address token,
        uint256 price,
        uint256 volume24h,
        int8 priceChange
    ) external onlyAuthorizedUpdater whenNotPaused {
        require(token != address(0), "Invalid token");
        
        TokenPrice storage oldPrice = tokenPrices[token];
        
        // Validate price change
        if (oldPrice.price > 0) {
            int256 changePercent = int256(
                ((price - oldPrice.price) * 100) / oldPrice.price
            );
            require(
                changePercent >= -int256(MAX_PRICE_CHANGE) &&
                changePercent <= int256(MAX_PRICE_CHANGE),
                "Price change too large"
            );
        }

        tokenPrices[token] = TokenPrice({
            price: price,
            timestamp: block.timestamp,
            volume24h: volume24h,
            priceChange: priceChange
        });

        emit PriceUpdated(token, price, block.timestamp);
    }

    /**
     * @dev Get the USD price of a token
     */
    function getPrice(address token) public view returns (uint256) {
        TokenPrice memory price = tokenPrices[token];
        require(price.timestamp > 0, "Price not available");
        require(
            block.timestamp - price.timestamp <= PRICE_EXPIRY,
            "Price expired"
        );
        return price.price;
    }

    /**
     * @dev Get the Chainlink price feed price
     */
    function getChainlinkPrice(
        address token
    ) public view returns (uint256) {
        PriceFeed memory feed = priceFeeds[token];
        require(feed.isActive, "No active feed");

        (, int256 price,,,) = feed.aggregator.latestRoundData();
        require(price > 0, "Invalid price");

        // Convert to 18 decimals
        return uint256(price) * 10**(18 - feed.decimals);
    }

    /**
     * @dev Get comprehensive price data for a token
     */
    function getPriceData(
        address token
    ) external view returns (
        uint256 price,
        uint256 timestamp,
        uint256 volume24h,
        int8 priceChange
    ) {
        TokenPrice memory data = tokenPrices[token];
        return (
            data.price,
            data.timestamp,
            data.volume24h,
            data.priceChange
        );
    }

    /**
     * @dev Calculate value in USD
     */
    function calculateUSDValue(
        address token,
        uint256 amount
    ) external view returns (uint256) {
        uint256 price = getPrice(token);
        return (amount * price) / 1e18;
    }

    // Admin functions
    function addUpdater(address updater) external onlyOwner {
        authorizedUpdaters[updater] = true;
        emit UpdaterAdded(updater);
    }

    function removeUpdater(address updater) external onlyOwner {
        authorizedUpdaters[updater] = false;
        emit UpdaterRemoved(updater);
    }

    function pause() external onlyOwner {
        _pause();
    }

    function unpause() external onlyOwner {
        _unpause();
    }
}
