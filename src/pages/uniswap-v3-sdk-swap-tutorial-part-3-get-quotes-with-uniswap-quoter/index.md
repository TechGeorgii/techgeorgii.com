---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial 3/5 – Get quote"
description: "This is the part 3 of Uniswap V3 SDK Swap Tutorial, full source code. In this part we’ll call Quoter interface with ethers.js to get quote for a swap. First we format inAmountStr according to decimals of this token. ethe"
pubDate: "2022-07-18"
---

This is the part 3 of [Uniswap V3 SDK Swap Tutorial](/uniswap-v3-sdk-tutorial/), [full source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts).

In this part we’ll call [Quoter interface](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/IQuoter.sol) with ethers.js to get quote for a swap.

First we format inAmountStr according to decimals of this token. ethers.js has very handy functions for it. Always use the number of decimals after the decimal point you got from the chain (***tokenIn.decimals***) since on some test networks I’ve encountered unusual values (let’s say 6 instead of 18 widely used on mainnet):

```typescript
const amountIn = ethers.utils.parseUnits(inAmountStr, tokenIn.decimals);
```

Next step is to actually call the quoter and get ***quotedAmountOut***. Uniswap quoter address is the same on all chains, [here](https://docs.uniswap.org/protocol/reference/deployments) you can find all addresses of Uniswap smart contracts.

```typescript
const UNISWAP_QUOTER_ADDRESS = '0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6'
const quoterContract = new ethers.Contract(UNISWAP_QUOTER_ADDRESS, QuoterABI.abi, provider);

const quotedAmountOut = await quoterContract.callStatic.quoteExactInputSingle(
    tokenIn.address,
    tokenOut.address,
    pool.fee,
    amountIn,
    0
);
```

There are few nuances tho.

1. We use special feature of ethers.js called “callStatic” (note contract.**callStatic**.METHOD\_NAME call). Quoter interface’ methods modify blockchain state (they call non-view functions), so this technique emulates call of a method by telling a node to pretend that a call is not state-changing and return the result.
2. We use quoteExactInputSingle method, it means for a swap we supply some exact amount of ***tokenIn***.
3. This swap is done in a single exchange (e.g. WETH-USDT) within one pool. To get a quote for a multi-hop swap (e.g. WETH-DAI-USDT), you can use method  [Quoter interface.](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/IQuoter.sol)***quoteExactInput***, where swap path is passed.

We can then print the quote using ***ethers.utils.formatUnits*** to format quote according to decimals of ***tokenOut***.

```typescript
console.log(`You'll get approximately ${ethers.utils.formatUnits(quotedAmountOut, tokenOut.decimals)} ${tokenOut.symbol} for ${inAmountStr} ${tokenIn.symbol}`);
```

That’s it, we successfully got a swap quote. The [next part](/uniswap-v3-sdk-swap-tutorial-part-4-get-swap-route/) is about getting a route for a swap.
