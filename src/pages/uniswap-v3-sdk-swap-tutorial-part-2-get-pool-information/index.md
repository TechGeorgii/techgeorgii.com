---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial 2/5 – Get pool information"
description: "This is the second part of Uniswap V3 SDK Swap Tutorial, full source code. In this part we’ll download and print out pool information. Pool is just a smart contract, responsible for swapping one token for another, for ex"
pubDate: "2022-07-18"
---

This is the second part of [Uniswap V3 SDK Swap Tutorial](/uniswap-v3-sdk-tutorial/), [full source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts).

In this part we’ll download and print out pool information. Pool is just a smart contract, responsible for swapping one token for another, for example, WETH-USDT pool ([more about pools](https://docs.uniswap.org/protocol/V2/concepts/core-concepts/pools)).

### Get Uniswap pool smart contract address

To get pool smart contract address we use Uniswap Factory that is also a smart contract deployed on 0x1F98431c8aD98523631AE4a59f267346ea31F984 (all chains). Addresses of Uniswap deployed contracts can be found [here](https://docs.uniswap.org/protocol/reference/deployments) (they are all the same on all chains).

```typescript
const UNISWAP_FACTORY_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984';
const factoryContract = new ethers.Contract(UNISWAP_FACTORY_ADDRESS, IUniswapV3Factory.abi, provider);

// loading pool smart contract address
const poolAddress = await factoryContract.getPool(
    tokenIn.address,
    tokenOut.address,
    3000);  // commission - 3%

if (Number(poolAddress).toString() === "0") // there is no such pool for provided In-Out tokens.
    throw `Error: No pool ${tokenIn.symbol}-${tokenOut.symbol}`;
```

In the code above, we call getPool function of Uniswap Factory smart contract and pass addresses of our token pair. Third parameter is integer parameter that is the commission in hundredths of a bip (one bip = 1e-6).

If zero is returned as pool address it means there is no such pool so we throw an error.

### Loading Uniswap pool immutable data

Next step is to load pool immutable data, that doesn’t change over time (e.g. pool tokens, fee) and pool state data (most obviously, token prices) that is variable over time.

To do it we create [ethers.js smart contract](https://docs.ethers.io/v5/api/contract/contract/) object. ABI (interface) for this contract (***IUniswapV3Pool.abi***) is the one we import from Uniswap SDK:

```typescript
const poolContract = new ethers.Contract(poolAddress, IUniswapV3Pool.abi, provider);
```

Next follows a function to load pool immutable parameters asynchronously:

```typescript
const getPoolImmutables = async function () {
    const [factory, token0, token1, fee, tickSpacing, maxLiquidityPerTick] = await Promise.all([
        poolContract.factory(),
        poolContract.token0(),
        poolContract.token1(),
        poolContract.fee(),
        poolContract.tickSpacing(),
        poolContract.maxLiquidityPerTick(),
    ]);

    return {
        factory: factory,
        token0: token0,
        token1: token1,
        fee: fee,
        tickSpacing: tickSpacing,
        maxLiquidityPerTick: maxLiquidityPerTick,
    }
}
```

And here is the function to load pool’s state (variable) parameters like token prices. [Here](https://docs.uniswap.org/sdk/guides/fetching-prices) you can read more about the math behind it and [this](https://docs.uniswap.org/protocol/reference/core/libraries/SqrtPriceMath) is the functions to deal with it.

```typescript
const getPoolState = async function () {
    const [liquidity, slot] = await Promise.all([poolContract.liquidity(), poolContract.slot0()]);

    return {
        liquidity: liquidity,
        sqrtPriceX96: slot[0],
        tick: slot[1],
        observationIndex: slot[2],
        observationCardinality: slot[3],
        observationCardinalityNext: slot[4],
        feeProtocol: slot[5],
        unlocked: slot[6],
    }
}
```

Finally, we call both these functions and after data is loaded Pool object is created. This is just a TypeScript object for your convenience:

```typescript
const [immutables, state] = await Promise.all([getPoolImmutables(), getPoolState()]);

const pool = new Pool(
    tokenIn,
    tokenOut,
    immutables.fee,
    state.sqrtPriceX96.toString(),
    state.liquidity.toString(),
    state.tick
);
```

We can then print price of tokens in the pool:

```typescript
console.log(`1 ${pool.token0.symbol} = ${pool.token0Price.toSignificant()} ${pool.token1.symbol}`);
console.log(`1 ${pool.token1.symbol} = ${pool.token1Price.toSignificant()} ${pool.token0.symbol}`);
```

Here it is, we finished third part of Uniswap V3 SDK Swap Tutorial and learned how to load pool information for a pair of tokens we’d like to work with. Next is the [Part 3 – Get quotes with Uniswap Quoter](/uniswap-v3-sdk-swap-tutorial-part-3-get-quotes-with-uniswap-quoter/)
