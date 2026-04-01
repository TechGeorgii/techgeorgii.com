---
layout: ../../layouts/ArticleLayout.astro
title: "Uniswap V3 SDK Swap Tutorial 4/5 – Get swap route"
description: "This is the part 4 of Uniswap V3 SDK Swap Tutorial, full source code. A crucial part of making a swap is creating a swap route. This is the optimal path with swap parameters which Uniswap constructs to make the desired s"
pubDate: "2022-07-29"
---

This is the part 4 of [Uniswap V3 SDK Swap Tutorial](/uniswap-v3-sdk-tutorial/), [full source code](https://github.com/TechGeorgii/uniswap-v3-sdk-tutorial-ts).

A crucial part of making a swap is creating a swap route. This is the optimal path with swap parameters which Uniswap constructs to make the desired swap.

### How to conduct token swap in Uniswap

Swap is conducted in the following way:

1. You first ask Uniswap for a swap route with desired parameters.
2. Uniswap gives you that route that includes:
   1. Path on how swap would be made optimally. For example, if swap WETH->USDT is to be made, a path WETH->DAI->USDT can be more optimal to get more USDT for a given amount of WETH.
   2. Optimal quote.
   3. Swap gas and gas price estimations.
   4. And many other parameters.
3. If you are fine with that quote you submit swap transaction with that route and wait for result.

Let’s see what we need to specify to ask [Uniswap for a route](https://docs.uniswap.org/sdk/guides/auto-router):

- Input or output amount depending on type of trade (next point). In our tutorial we swap fixed amount of WETH (input token) to get some USDT, so we specify it in ***inAmount*** variable.
- Type of trade (swap):
  - EXACT\_INPUT – we fix the amount of input tokens (let’s say 10 WETH) to get as much USDT as possible.
  - EXACT\_OUTPUT – we fix the amount of output tokens (let’s say we need 100 USDT as an output) and ask Uniswap to construct the route to spend as few WETH as possible.
- We also set swapOptions, in our example:
  - recipient – wallet address that will get the result coins
  - slippageTolerance in % – how much of a quoted amount we can tolerate. E.g., if the quote indicated we would get 100 USDT as a result, in case of 5% slippage tolerance a swap wouldn’t be executed if less than 95 USDT would be our result coins.
  - deadline – deadline in absolute seconds. In this example add 1800 seconds (so that 30 minutes). If swap takes longer than it wouldn’t be successful.
- routerConfig. A prominent parameter is maxSwapsPerPath that defines how many intermediary swaps we can tolerate. E.g., if maxSwapsPerPath is set to 1 than only direct swap WETH->USDT would be allowed. When testing I once had to limit maxSwapsPerPath to 1 since on Rinkeby test network a suggested route USDT->DAI->WETH didn’t work for me due to (I guess) broken data – a UniswapV2Pair contract balance for DAI was greater than 2^112-1 (<https://github.com/Uniswap/v2-core/blob/master/contracts/UniswapV2Pair.sol>) and overflow error was thrown. Direct USDT->WETH swap worked just fine.

### Uniswap AlphaRouter and route loading

After this explanation it should be straightforward. First, let’s ask Uniswap for a route and check if route is returned:

```typescript
const inAmount = CurrencyAmount.fromRawAmount(tokenIn, amountIn.toString());

const router = new AlphaRouter({ chainId: tokenIn.chainId, provider: provider });
const route = await router.route(
    inAmount,
    tokenOut,
    TradeType.EXACT_INPUT,
    // swapOptions
    {
        recipient: walletAddress,
        slippageTolerance: new Percent(5, 100),          // Big slippage – for a test
        deadline: Math.floor(Date.now() / 1000 + 1800)    // add 1800 seconds – 30 mins deadline
    },
    // router config
    {
        maxSwapsPerPath: 1 // remove this if you want multi-hop swaps as well.
    }
);

if (route == null || route.methodParameters === undefined)
    throw "No route loaded";
```

For example, on Goerli test network as of July 2022 only WETH-UNI swaps are available, so you’d get a null route trying to swap other tokens.

Then let’s print quote and gas fees:

```typescript
console.log(`   You'll get ${route.quote.toFixed()} of ${tokenOut.symbol}`);
// output quote minus gas fees
console.log(`   Gas Adjusted Quote: ${route.quoteGasAdjusted.toFixed()}`);
console.log(`   Gas Used Quote Token: ${route.estimatedGasUsedQuoteToken.toFixed()}`);
console.log(`   Gas Used USD: ${route.estimatedGasUsedUSD.toFixed()}`);
console.log(`   Gas Used: ${route.estimatedGasUsed.toString()}`);
console.log(`   Gas Price Wei: ${route.gasPriceWei}`);
console.log('');
```

To those who is confused about gas and gas price like I was. Gas is the amount of computing work Ethereum needs to get the work done. Most simple swaps I tested require 300,000 of computational work and that does not change on network load. Simply put, this is a number of computation steps for Ethereum virtual machine.

Gas price is the amount in wei you pay for each computational step. If you want to speed up execution of your swap than set gas price more than estimated (**route.gasPriceWei**) so that nodes would be incentivised to process your operation first.

So, we finished part 4 and in this part we asked Uniswap for a swap route and got it afterwards. See [part 5](/uniswap-v3-sdk-swap-tutorial-part-5-execute-a-swap/) on how to execute actual swap.
